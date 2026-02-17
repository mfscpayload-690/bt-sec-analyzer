"""
Main entry point for bt-sec-analyzer GUI application.
"""

import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

from bt_sectester.utils.config import Config
from bt_sectester.utils.logger import setup_logger


def launch_backend(host: str = "127.0.0.1", port: int = 8745) -> None:
    """Start the FastAPI backend server."""
    import uvicorn

    uvicorn.run(
        "bt_sectester.core.api_bridge:app",
        host=host,
        port=port,
        reload=False,
        log_level="warning",
    )


def launch_frontend_dev() -> subprocess.Popen:
    """Start the Vite dev server (development only)."""
    ui_dir = Path(__file__).parent.parent / "ui"
    if not (ui_dir / "node_modules").exists():
        print("[*] Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=ui_dir, check=True)
    return subprocess.Popen(
        ["npm", "run", "dev", "--", "--open"],
        cwd=ui_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> int:
    """
    Main entry point for bt-sec-analyzer.

    Returns:
        Exit code
    """
    try:
        # Load configuration
        config = Config.load()

        # Setup logging
        log_file = Path(config.logging.output.get("file_path", "logs/bt_sectester.log"))
        setup_logger(
            name="bt_sectester",
            level=config.logging.level,
            log_format=config.logging.format,
            log_file=log_file,
            console=True,
        )

        # Display ethical disclaimer
        if config.ui.get("show_ethical_disclaimer", True):
            print("\n" + "=" * 60)
            print("  BT-SEC-ANALYZER")
            print("  Bluetooth Security Testing Framework")
            print("=" * 60)
            print("\n  This tool is for AUTHORIZED security testing only.")
            print("  Unauthorized use may be illegal and unethical.\n")
            print("=" * 60 + "\n")

            response = input("Do you accept these terms? (yes/no): ").strip().lower()
            if response not in ["yes", "y"]:
                print("\nTerms not accepted. Exiting.")
                return 1

        # CLI-only mode
        if "--cli" in sys.argv:
            print("\n[!] Use CLI mode:")
            print("    bt-sec-analyzer-cli --help\n")
            return 0

        # Launch GUI mode: backend API + frontend
        backend_host = "127.0.0.1"
        backend_port = 8745
        frontend_url = "http://localhost:5173"

        print(f"\n[*] Starting backend API on {backend_host}:{backend_port}...")

        backend_thread = threading.Thread(
            target=launch_backend,
            args=(backend_host, backend_port),
            daemon=True,
        )
        backend_thread.start()

        # Give backend a moment to start
        time.sleep(1)
        print("[+] Backend API running")

        # Check if built frontend exists
        dist_dir = Path(__file__).parent.parent / "ui" / "dist"
        ui_dir = Path(__file__).parent.parent / "ui"
        vite_proc = None

        if dist_dir.exists():
            # Production: serve static files from dist/ via the API server
            frontend_url = f"http://{backend_host}:{backend_port}"
            print(f"[+] Serving built frontend at {frontend_url}")
        elif ui_dir.exists() and (ui_dir / "package.json").exists():
            # Development: launch Vite dev server
            print("[*] Starting Vite dev server...")
            vite_proc = launch_frontend_dev()
            time.sleep(2)
            print(f"[+] Frontend dev server at {frontend_url}")
        else:
            print("[!] No frontend found. Access API directly:")
            print(f"    {backend_host}:{backend_port}/api/status")
            frontend_url = None

        if frontend_url:
            print(f"\n[+] Opening browser: {frontend_url}")
            webbrowser.open(frontend_url)

        print("\n[*] Press Ctrl+C to stop.\n")

        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            if vite_proc:
                vite_proc.terminate()
            print("\n[*] Shutting down.")

        return 0

    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user. Exiting.")
        return 130
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
