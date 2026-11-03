"""Offline security boundaries and ordinary controls for the November refresh."""

import hashlib
from io import BytesIO
import ssl
import subprocess
import sys
import tarfile

import pytest


def test_certifi_distrusts_compromised_emsign_roots_and_loads_remaining_cas():
    # https://github.com/certifi/python-certifi/security/advisories/GHSA-6q48-6c7w-9gw2
    import certifi

    removed_fingerprints = {
        "40f6af0346a99aa1cd1d555a4e9cce62c7f9634603ee406615833dc8c8d00367",  # G1
        "86a1ecba089c4a8d3bbe2734c612ba341d813e043cf9e8a862cd5c57a36bbe6b",  # G3
        "125609aa301da0a249b97a8239cb6a34216f44dcac9f3954b14292f2e8c8608f",  # C1
        "bc4d809b15189d78db3e1d8cf4f9726a795da1643ca5f1358e1ddb0edc0d7eb3",  # C3
    }
    context = ssl.create_default_context(cafile=certifi.where())
    fingerprints = {hashlib.sha256(certificate).hexdigest() for certificate in context.get_ca_certs(binary_form=True)}
    assert fingerprints.isdisjoint(removed_fingerprints)
    assert context.check_hostname
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.cert_store_stats()["x509_ca"] > 100


_TRACEPARENT = "00-1234567890abcdef1234567890abcdef-1234567890abcdef-01"


@pytest.mark.parametrize("headers", [
    ["vendor=value" + " " * 8181],  # 8193 characters in one field
    ["a=b" + " " * 4093, "c=d" + "\t" * 4093],  # 8193 with the joining comma
])
def test_opentelemetry_discards_oversized_single_and_combined_tracestate(headers):
    # https://github.com/open-telemetry/opentelemetry-python/pull/5746
    from opentelemetry import trace
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

    context = TraceContextTextMapPropagator().extract({
        "traceparent": _TRACEPARENT, "tracestate": headers,
    })
    span = trace.get_current_span(context).get_span_context()
    assert span.is_valid and span.is_remote
    assert span.trace_state.to_header() == ""


def test_opentelemetry_accepts_boundary_and_normal_propagation():
    from opentelemetry import trace
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

    propagator = TraceContextTextMapPropagator()
    boundary = "vendor=value" + " " * (8192 - len("vendor=value"))
    context = propagator.extract({"traceparent": _TRACEPARENT, "tracestate": boundary})
    assert trace.get_current_span(context).get_span_context().trace_state["vendor"] == "value"
    outgoing = {}
    propagator.inject(outgoing, context=context)
    assert outgoing == {"traceparent": _TRACEPARENT, "tracestate": "vendor=value"}


def test_pillow_negative_tar_size_is_rejected_without_looping(tmp_path):
    # The -512 size seeks back to its own header in vulnerable Pillow.
    # https://github.com/python-pillow/Pillow/security/advisories/GHSA-3j72-p6qg-6xp7
    header = bytearray(512)
    header[:5] = b"other"
    header[124:135] = b"-1000".rjust(11)
    path = tmp_path / "negative-size.tar"
    path.write_bytes(header)
    driver = '''
import socket, sys
def offline(*args, **kwargs):
    raise RuntimeError("Network access is disabled")
socket.socket.connect = socket.socket.connect_ex = offline
socket.create_connection = socket.getaddrinfo = offline
from PIL.TarIO import TarIO
try:
    TarIO(sys.argv[1], "wanted")
except ValueError:
    pass
else:
    raise AssertionError("negative TAR size was accepted")
'''
    try:
        completed = subprocess.run(
            [sys.executable, "-B", "-c", driver, str(path)],
            capture_output=True, text=True, timeout=5,
        )
    except subprocess.TimeoutExpired:
        pytest.fail("TarIO did not reject a negative size within the subprocess deadline")
    assert completed.returncode == 0, completed.stderr


@pytest.mark.parametrize("size", [b"-1", b"-1000"])
def test_pillow_rejects_negative_size_even_for_requested_member(tmp_path, size):
    from PIL.TarIO import TarIO

    header = bytearray(512)
    header[:6] = b"wanted"
    header[124:135] = size.rjust(11)
    path = tmp_path / "negative-matching-member.tar"
    path.write_bytes(header)
    with pytest.raises(ValueError, match="negative"):
        TarIO(str(path), "wanted")


def test_pillow_can_read_normal_tar_member_as_image(tmp_path):
    from autogen_core import Image as AgentImage
    from PIL import Image
    from PIL.TarIO import TarIO

    data = BytesIO()
    Image.new("RGB", (2, 2), (12, 34, 56)).save(data, format="PNG")
    contents = data.getvalue()
    path = tmp_path / "normal.tar"
    with tarfile.open(path, "w") as archive:
        info = tarfile.TarInfo("image.png")
        info.size = len(contents)
        archive.addfile(info, BytesIO(contents))
    with TarIO(str(path), "image.png") as member, Image.open(member) as image:
        image.load()
        assert image.size == (2, 2)
        assert image.getpixel((1, 1)) == (12, 34, 56)
        restored = AgentImage.from_base64(AgentImage.from_pil(image).to_base64())
        assert restored.image.getpixel((1, 1)) == (12, 34, 56)
