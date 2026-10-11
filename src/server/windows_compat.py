"""
Windows compatibility helpers for asyncio ProactorEventLoop and Uvicorn.

On Windows, Python's ProactorEventLoop uses `_ProactorBasePipeTransport`. When a client
(such as a browser polling /api/v1/network/telemetry, refreshing a page, or closing a socket)
abruptly closes or resets a TCP connection, `_call_connection_lost` attempts to call
`self._sock.shutdown(socket.SHUT_RDWR)` without catching OSError.
On Windows this raises `ConnectionResetError: [WinError 10054] An existing connection was forcibly
closed by the remote host` as an unhandled callback exception.

This helper cleanly patches `_call_connection_lost` to catch and ignore socket shutdown
errors, ensuring socket references are closed and server handles are detached without
polluting logs.
"""

import sys


def apply_windows_asyncio_patch() -> None:
    """Safely suppresses WinError 10054 in asyncio ProactorEventLoop on Windows."""
    if sys.platform != "win32":
        return

    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport
    except ImportError:
        return

    if getattr(_ProactorBasePipeTransport, "_qsc_patched", False):
        return

    def _call_connection_lost_patched(self, exc):
        if self._called_connection_lost:
            return
        try:
            self._protocol.connection_lost(exc)
        finally:
            if hasattr(self, "_sock") and self._sock is not None:
                if hasattr(self._sock, "shutdown") and self._sock.fileno() != -1:
                    try:
                        self._sock.shutdown(2)  # socket.SHUT_RDWR
                    except OSError:
                        pass
                try:
                    self._sock.close()
                except OSError:
                    pass
                self._sock = None
            server = getattr(self, "_server", None)
            if server is not None:
                try:
                    server._detach()
                except Exception:
                    pass
                self._server = None
            self._called_connection_lost = True

    _ProactorBasePipeTransport._call_connection_lost = _call_connection_lost_patched
    _ProactorBasePipeTransport._qsc_patched = True
