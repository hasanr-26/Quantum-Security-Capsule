"""
Launcher for the QSC settlement node.

Starts the FastAPI application over real TLS. By default it also starts the
interception proxy on a second port, so the "harvest now, decrypt later"
demonstration has a genuine network hop to capture traffic from.

    python -m src.server.run
    python -m src.server.run --no-proxy
    python -m src.server.run --port 9443
"""

import argparse
import sys
import threading

import uvicorn

from src.server import tls_config


def _serve(app_path: str, host: str, port: int, cert: str, key: str, label: str) -> None:
    """Runs one uvicorn instance over TLS."""
    uvicorn.run(
        app_path,
        host=host,
        port=port,
        ssl_certfile=cert,
        ssl_keyfile=key,
        log_level="info",
        access_log=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the QSC settlement node over TLS.")
    parser.add_argument("--host", default=tls_config.DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=tls_config.DEFAULT_PORT)
    parser.add_argument("--proxy-port", type=int, default=tls_config.PROXY_PORT)
    parser.add_argument(
        "--no-proxy",
        action="store_true",
        help="Start only the settlement API, without the interception proxy.",
    )
    parser.add_argument(
        "--regenerate-cert",
        action="store_true",
        help="Force a new self-signed certificate.",
    )
    args = parser.parse_args()

    cert, key = tls_config.ensure_dev_certificate(force=args.regenerate_cert)

    print("=" * 72)
    print(" QSC SETTLEMENT NETWORK - POST-QUANTUM MESSAGE SECURITY NODE")
    print("=" * 72)
    print(f"  Workbench      https://{args.host}:{args.port}/")
    print(f"  API docs       https://{args.host}:{args.port}/api/docs")
    print(f"  Certificate    {cert}")
    if not args.no_proxy:
        print(f"  MITM proxy     https://{args.host}:{args.proxy_port}/  (intercepting)")
    print("=" * 72)
    print("  The certificate is self-signed. Your browser will warn once;")
    print("  accept it to reach the workbench over genuine TLS.")
    print("=" * 72)

    if not args.no_proxy:
        proxy_thread = threading.Thread(
            target=_serve,
            args=(
                "src.server.mitm_proxy:proxy_app",
                args.host,
                args.proxy_port,
                cert,
                key,
                "proxy",
            ),
            daemon=True,
        )
        proxy_thread.start()

    _serve("src.server.api:app", args.host, args.port, cert, key, "api")
    return 0


if __name__ == "__main__":
    sys.exit(main())
