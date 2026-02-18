"""
FastAPI backend bridge for the bt-sec-analyzer UI.

Provides REST API and WebSocket endpoints that the Svelte frontend
communicates with. Bridges frontend calls to the core Python engine.
"""

import asyncio
import json
import logging
import os
import pty
import select
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------


class ScanRequest(BaseModel):
    duration: int = 10
    classic: bool = True
    ble: bool = True


class AttackRequest(BaseModel):
    attack_type: str
    target: str
    duration: Optional[int] = None
    parameters: Dict[str, Any] = {}


class ReportRequest(BaseModel):
    format: str = "pdf"


class SummarizeRequest(BaseModel):
    context: str = ""


class ConfigPatch(BaseModel):
    key: str
    value: Any


class FrontendLogEntry(BaseModel):
    level: str = "ERROR"
    message: str
    context: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="bt-sec-analyzer API",
        version="0.1.0",
        description="Backend bridge for the bt-sec-analyzer desktop UI",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Lazy engine singleton ------------------------------------------

    _engine_holder: Dict[str, Any] = {}

    def get_engine():
        if "engine" not in _engine_holder:
            from bt_sectester.core.engine import BTSecEngine

            _engine_holder["engine"] = BTSecEngine()
        return _engine_holder["engine"]

    # ---- Log broadcasting -----------------------------------------------

    log_subscribers: List[WebSocket] = []

    class WebSocketLogHandler(logging.Handler):
        """Forward Python log records to all connected WebSocket clients."""

        def emit(self, record: logging.LogRecord) -> None:
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "message": self.format(record),
                "logger": record.name,
            }
            dead: List[WebSocket] = []
            for ws in log_subscribers:
                try:
                    asyncio.run_coroutine_threadsafe(
                        ws.send_json(entry),
                        asyncio.get_event_loop(),
                    )
                except Exception:
                    dead.append(ws)
            for ws in dead:
                log_subscribers.remove(ws)

    ws_handler = WebSocketLogHandler()
    ws_handler.setLevel(logging.DEBUG)
    logging.getLogger("bt_sectester").addHandler(ws_handler)

    # ---- REST endpoints -------------------------------------------------

    @app.get("/api/status")
    async def status():
        try:
            engine = get_engine()
            return {
                "connected": True,
                "ethical_mode": engine.config.app.ethical_mode,
                "adapter": engine.config.bluetooth.default_adapter,
                "scanning": False,
                "session_id": engine.session_id,
            }
        except Exception as exc:
            return {"connected": False, "error": str(exc)}

    @app.get("/api/adapters")
    async def adapters():
        result = subprocess.run(
            ["hciconfig"], capture_output=True, text=True, timeout=5
        )
        found = []
        for line in result.stdout.splitlines():
            if line and not line.startswith("\t"):
                parts = line.split(":")
                if parts:
                    found.append({"id": parts[0].strip(), "name": parts[0].strip()})
        if not found:
            found = [{"id": "hci0", "name": "hci0"}]
        return {"adapters": found}

    @app.post("/api/scan")
    async def scan(req: ScanRequest):
        engine = get_engine()
        devices = engine.scan_devices(
            duration=req.duration, classic=req.classic, ble=req.ble
        )
        return {"devices": devices, "count": len(devices)}

    @app.get("/api/devices")
    async def devices():
        engine = get_engine()
        return {"devices": engine.session_data.get("devices", [])}

    @app.get("/api/enumerate/{mac}")
    async def enumerate_services(mac: str):
        engine = get_engine()
        services = engine.enumerate_services(mac)
        return services

    @app.post("/api/attack")
    async def attack(req: AttackRequest):
        from bt_sectester.modules.attacks.attack_simulator import (
            AttackSimulator,
            AttackType,
        )

        engine = get_engine()
        simulator = AttackSimulator(
            privilege_manager=engine.privilege_manager,
            ethical_mode=engine.config.app.ethical_mode,
        )

        type_map = {
            "dos_flood": AttackType.DOS_FLOOD,
            "deauthentication": AttackType.DEAUTH,
            "passive_sniffing": AttackType.SNIFF,
            "pin_bruteforce": AttackType.PIN_BRUTE,
        }
        attack_type = type_map.get(req.attack_type)
        if attack_type is None:
            return {"error": f"Unknown attack type: {req.attack_type}"}

        result = simulator.execute_attack(
            attack_type=attack_type,
            target=req.target,
            duration=req.duration,
            parameters=req.parameters,
        )
        result_dict = result.to_dict()

        # Persist in session
        engine.session_data.setdefault("attacks", []).append(result_dict)

        return result_dict

    @app.post("/api/attack/{attack_id}/stop")
    async def stop_attack(attack_id: str):
        # Placeholder — proper implementation would track running attack refs
        return {"stopped": True, "attack_id": attack_id}

    @app.get("/api/attacks")
    async def get_attacks():
        engine = get_engine()
        return {"attacks": engine.session_data.get("attacks", [])}

    @app.post("/api/report")
    async def report(req: ReportRequest):
        from bt_sectester.modules.reporting.report_generator import ReportGenerator

        engine = get_engine()
        generator = ReportGenerator(
            output_dir=Path("reports"),
            company_name=engine.config.reporting.get(
                "company_name", "Security Assessment"
            ),
        )

        if req.format == "html":
            path = generator.generate_html_report(engine.session_data)
        else:
            path = generator.generate_pdf_report(engine.session_data)

        return {"path": str(path), "format": req.format}

    @app.post("/api/ai/summarize")
    async def summarize(req: SummarizeRequest):
        engine = get_engine()
        if engine.ollama_client is None:
            return {"summary": "Ollama is not available. Start Ollama and restart the backend."}

        logs_data = engine.session_data.get("logs", [])
        summary = engine.ollama_client.summarize_logs(
            logs_data, context=req.context or "Bluetooth security assessment"
        )
        return {"summary": summary}

    @app.get("/api/config")
    async def get_config():
        engine = get_engine()
        return engine.config.dict()

    @app.patch("/api/config")
    async def patch_config(patch: ConfigPatch):
        engine = get_engine()
        engine.config.set(patch.key, patch.value)
        return {"ok": True, "key": patch.key}

    @app.post("/api/log")
    async def frontend_log(entry: FrontendLogEntry):
        """Receive structured log entries from the Svelte frontend."""
        level = entry.level.upper()
        level_no = getattr(logging, level, logging.ERROR)
        _logger = logging.getLogger("bt_sectester.frontend")
        _logger.log(level_no, entry.message, extra={"frontend_context": entry.context or {}})
        return {"ok": True}

    @app.websocket("/ws/logs")
    async def ws_logs(ws: WebSocket):
        await ws.accept()
        log_subscribers.append(ws)
        try:
            while True:
                # Keep connection alive; client doesn't send data
                await ws.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            if ws in log_subscribers:
                log_subscribers.remove(ws)

    # ---- WebSocket: interactive terminal --------------------------------

    @app.websocket("/ws/terminal")
    async def ws_terminal(ws: WebSocket):
        await ws.accept()

        master_fd, slave_fd = pty.openpty()

        shell = os.environ.get("SHELL", "/bin/bash")
        proc = subprocess.Popen(
            [shell],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            preexec_fn=os.setsid,
        )
        os.close(slave_fd)

        # Read from PTY → send to WS
        async def reader():
            loop = asyncio.get_event_loop()
            try:
                while proc.poll() is None:
                    r, _, _ = await loop.run_in_executor(
                        None, select.select, [master_fd], [], [], 0.1
                    )
                    if master_fd in r:
                        data = os.read(master_fd, 4096)
                        if data:
                            await ws.send_text(data.decode("utf-8", errors="replace"))
            except Exception:
                pass

        reader_task = asyncio.create_task(reader())

        try:
            while True:
                data = await ws.receive_text()
                os.write(master_fd, data.encode("utf-8"))
        except WebSocketDisconnect:
            pass
        finally:
            reader_task.cancel()
            proc.terminate()
            os.close(master_fd)

    # ---- Optionally serve built Svelte frontend -------------------------

    dist_dir = Path(__file__).parent.parent.parent / "ui" / "dist"
    if dist_dir.exists():
        app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")

    return app


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "bt_sectester.core.api_bridge:app",
        host="127.0.0.1",
        port=8745,
        reload=False,
        log_level="info",
    )
