"""Keep the explicitly selected CI unit tests offline and credential-free."""

import socket

import pytest


_offline_guard = pytest.MonkeyPatch()


def _network_disabled(*args, **kwargs):
    raise RuntimeError("Network access is disabled in the offline unit test suite")


def pytest_sessionstart(session):
    # Apply before collection: application imports must not contact services either.
    _offline_guard.setenv("PYTHON_DOTENV_DISABLED", "1")
    _offline_guard.setenv("LANGSMITH_TRACING", "false")
    _offline_guard.setenv("LANGCHAIN_TRACING_V2", "false")
    _offline_guard.setenv("ANONYMIZED_TELEMETRY", "false")
    _offline_guard.setattr(socket.socket, "connect", _network_disabled)
    _offline_guard.setattr(socket.socket, "connect_ex", _network_disabled)
    _offline_guard.setattr(socket, "create_connection", _network_disabled)
    _offline_guard.setattr(socket, "getaddrinfo", _network_disabled)


def pytest_sessionfinish(session, exitstatus):
    _offline_guard.undo()
