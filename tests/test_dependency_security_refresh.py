"""Offline security boundaries and ordinary controls for the November refresh."""

import asyncio
import hashlib
from io import BytesIO
import os
import ssl
import stat
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


@pytest.mark.skipif(os.name != "posix", reason="POSIX UnixFileLock content and permission boundary")
@pytest.mark.parametrize("alias", ["existing", "hardlink"])
def test_filelock_preserves_existing_victim_content_and_mode(tmp_path, alias):
    # UnixFileLock must not truncate or chmod an inode it did not create.
    # https://github.com/tox-dev/filelock/security/advisories/GHSA-69hj-f68j-2879
    from filelock import FileLock

    victim = tmp_path / "victim.txt"
    victim.write_bytes(b"private existing contents")
    victim.chmod(0o600)
    lock_path = victim
    if alias == "hardlink":
        lock_path = tmp_path / "attacker.lock"
        os.link(victim, lock_path)

    with FileLock(lock_path, mode=0o666, timeout=1):
        assert victim.read_bytes() == b"private existing contents"
        assert stat.S_IMODE(victim.stat().st_mode) == 0o600
    assert victim.read_bytes() == b"private existing contents"
    assert stat.S_IMODE(victim.stat().st_mode) == 0o600


def test_filelock_huggingface_wrapper_and_reentrant_lock_still_work(tmp_path):
    from filelock import FileLock
    from huggingface_hub.utils import WeakFileLock

    path = tmp_path / "normal.lock"
    lock = FileLock(path, timeout=1)
    with lock:
        with lock:
            assert lock.is_locked
            assert lock.lock_counter == 2
    assert not lock.is_locked
    with WeakFileLock(path, timeout=1) as held:
        assert held.is_locked
    assert not held.is_locked


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


def test_opentelemetry_accepts_boundary_and_normal_propagation_and_exports_locally():
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

    propagator = TraceContextTextMapPropagator()
    boundary = "vendor=value" + " " * (8192 - len("vendor=value"))
    context = propagator.extract({"traceparent": _TRACEPARENT, "tracestate": boundary})
    assert trace.get_current_span(context).get_span_context().trace_state["vendor"] == "value"
    outgoing = {}
    propagator.inject(outgoing, context=context)
    assert outgoing == {"traceparent": _TRACEPARENT, "tracestate": "vendor=value"}

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    try:
        with provider.get_tracer("offline-security-refresh").start_as_current_span("local", context=context):
            pass
        spans = exporter.get_finished_spans()
        assert len(spans) == 1
        assert spans[0].parent.trace_id == int("1234567890abcdef1234567890abcdef", 16)
    finally:
        provider.shutdown()


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


@pytest.mark.parametrize("persist", [False, True])
def test_aiohttp_expiring_other_path_preserves_host_only_scope(tmp_path, persist):
    # https://github.com/aio-libs/aiohttp/pull/13674
    from aiohttp import CookieJar
    from http.cookies import SimpleCookie
    from yarl import URL

    async def exercise():
        jar = CookieJar()
        jar.update_cookies(SimpleCookie("session=private; Path=/"), URL("https://example.invalid/"))
        if persist:
            path = tmp_path / "cookies.json"
            jar.save(path)
            jar = CookieJar()
            jar.load(path)
        jar.update_cookies(
            SimpleCookie("session=expired; Domain=example.invalid; Path=/other; Max-Age=0"),
            URL("https://evil.example.invalid/other"),
        )
        assert jar.filter_cookies(URL("https://example.invalid/"))["session"].value == "private"
        assert "session" not in jar.filter_cookies(URL("https://evil.example.invalid/"))
        jar.update_cookies(
            SimpleCookie("shared=ordinary; Domain=example.invalid; Path=/"),
            URL("https://example.invalid/"),
        )
        assert jar.filter_cookies(URL("https://evil.example.invalid/"))["shared"].value == "ordinary"

    asyncio.run(exercise())


@pytest.mark.parametrize("max_age", ["9" * 400, "not-a-number", "600"], ids=["oversized", "malformed", "ordinary"])
def test_aiohttp_handles_huge_malformed_and_normal_max_age(max_age):
    # https://github.com/aio-libs/aiohttp/pull/13677
    from aiohttp import CookieJar
    from http.cookies import SimpleCookie
    from yarl import URL

    async def exercise():
        jar = CookieJar()
        cookie = SimpleCookie()
        cookie["session"] = "ordinary"
        cookie["session"]["max-age"] = max_age
        jar.update_cookies(cookie, URL("https://example.invalid/"))
        assert jar.filter_cookies(URL("https://example.invalid/"))["session"].value == "ordinary"

    asyncio.run(exercise())


def test_aiohttp_unknown_cookie_attributes_do_not_create_extra_cookies():
    # https://github.com/aio-libs/aiohttp/pull/13800
    from aiohttp._cookie_helpers import parse_set_cookie_headers

    header = "session=ordinary; " + "; ".join(f"unknown{i}=value" for i in range(20)) + "; Path=/; Secure"
    parsed = parse_set_cookie_headers([header])
    assert [name for name, _ in parsed] == ["session"]
    assert parsed[0][1].value == "ordinary"
    assert parsed[0][1]["path"] == "/"
    assert parsed[0][1]["secure"]


def test_chromadb_local_explicit_vector_retrieval_with_updated_telemetry():
    import chromadb
    from chromadb.config import Settings

    client = chromadb.Client(Settings(anonymized_telemetry=False))
    name = "offline_dependency_refresh"
    collection = client.create_collection(name, embedding_function=None)
    try:
        collection.add(ids=["local"], embeddings=[[1.0, 0.0]], documents=["local document"])
        result = collection.query(query_embeddings=[[1.0, 0.0]], n_results=1)
        assert result["ids"] == [["local"]]
        assert result["documents"] == [["local document"]]
    finally:
        client.delete_collection(name)
