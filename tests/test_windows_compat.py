"""
Tests for Windows asyncio compatibility patch.
"""

import sys
from unittest.mock import MagicMock

import pytest

from src.server.windows_compat import apply_windows_asyncio_patch


def test_apply_windows_asyncio_patch():
    apply_windows_asyncio_patch()

    if sys.platform == "win32":
        from asyncio.proactor_events import _ProactorBasePipeTransport

        assert getattr(_ProactorBasePipeTransport, "_qsc_patched", False) is True

        # Test that _call_connection_lost suppresses WinError 10054
        transport = MagicMock()
        transport._called_connection_lost = False
        transport._protocol = MagicMock()
        mock_sock = MagicMock()
        mock_sock.fileno.return_value = 1
        mock_sock.shutdown.side_effect = ConnectionResetError(10054, "An existing connection was forcibly closed")
        transport._sock = mock_sock
        transport._server = MagicMock()

        # Call the unbound method on our mock
        _ProactorBasePipeTransport._call_connection_lost(transport, None)

        assert transport._called_connection_lost is True
        assert transport._sock is None
        assert transport._server is None
        mock_sock.close.assert_called_once()
