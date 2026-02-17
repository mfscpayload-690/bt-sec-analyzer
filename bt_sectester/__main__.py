"""
Main entry point for BT-SecTester GUI application.
"""

import sys
from pathlib import Path

from bt_sectester.core.engine import BTSecEngine
from bt_sectester.utils.config import Config
from bt_sectester.utils.logger import setup_logger


def main() -> int:
    """
    Main entry point for BT-SecTester.

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
            print("\n" + "=" * 80)
            print("BT-SECTESTER - BLUETOOTH SECURITY TESTING FRAMEWORK")
            print("=" * 80)
            print("\n⚠️  ETHICAL USE ONLY ⚠️\n")
            print("This tool is designed for AUTHORIZED security testing only.")
            print("Unauthorized use may be illegal and unethical.\n")
            print("By using this tool, you confirm that:")
            print("  • You have explicit authorization to test target devices")
            print("  • You will comply with all applicable laws")
            print("  • You will enable audit logging for all operations")
            print("  • You will not use this tool for malicious purposes\n")
            print("=" * 80 + "\n")

            response = input("Do you accept these terms? (yes/no): ").strip().lower()
            if response not in ["yes", "y"]:
                print("\nTerms not accepted. Exiting.")
                return 1

        # Initialize engine
        print("\n[*] Initializing BT-SecTester engine...")
        engine = BTSecEngine(config)

        print(f"[+] Engine initialized (Session: {engine.session_id})")
        print(f"[+] Ethical mode: {'ENABLED' if config.app.ethical_mode else 'DISABLED'}")
        print(f"[+] Audit logging: {'ENABLED' if config.logging.audit.get('enabled') else 'DISABLED'}\n")

        # For now, launch CLI interface
        # In the future, this would launch the Tauri/Electron GUI
        print("[!] GUI not yet implemented. Use CLI mode:")
        print("    python -m bt_sectester.cli --help\n")

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
