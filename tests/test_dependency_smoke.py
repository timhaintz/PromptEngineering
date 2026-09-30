"""Exercise updated dependencies locally, without models, downloads, or tokens."""

import asyncio
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
from io import BytesIO
import json
import socket
from uuid import uuid4

import pytest


def test_offline_guard_rejects_network():
    with pytest.raises(RuntimeError, match="Network access is disabled"):
        socket.create_connection(("example.invalid", 443))


def test_langsmith_run_schema_and_langchain_splitter():
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langsmith.schemas import Run

    document = Document(page_content="alpha beta gamma delta", metadata={"source": "local"})
    chunks = RecursiveCharacterTextSplitter(chunk_size=10, chunk_overlap=0).split_documents([document])
    assert [chunk.page_content for chunk in chunks] == ["alpha beta", "gamma", "delta"]
    assert all(chunk.metadata == document.metadata for chunk in chunks)

    run = Run(
        id=uuid4(), name="offline-split", run_type="chain",
        start_time=datetime.now(timezone.utc), inputs={"text": document.page_content},
        outputs={"chunks": [chunk.page_content for chunk in chunks]},
    )
    restored = Run.model_validate_json(run.model_dump_json())
    assert restored.inputs == run.inputs
    assert restored.outputs == run.outputs


def test_pydantic_settings_environment_and_validation(monkeypatch):
    from pydantic import ValidationError
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class OfflineSettings(BaseSettings):
        model_config = SettingsConfigDict(env_prefix="OFFLINE_SMOKE_", env_file=None)
        retries: int = 1
        tracing: bool = False

    monkeypatch.setenv("OFFLINE_SMOKE_RETRIES", "3")
    monkeypatch.setenv("OFFLINE_SMOKE_TRACING", "false")
    assert OfflineSettings().model_dump() == {"retries": 3, "tracing": False}
    monkeypatch.setenv("OFFLINE_SMOKE_RETRIES", "invalid")
    with pytest.raises(ValidationError):
        OfflineSettings()


def test_pillow_png_round_trip():
    from PIL import Image

    image = Image.new("RGB", (2, 2), color=(12, 34, 56))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    with Image.open(buffer) as decoded:
        decoded.load()
        assert decoded.format == "PNG"
        assert decoded.size == image.size
        assert decoded.getpixel((1, 1)) == (12, 34, 56)


def test_aiohttp_session_and_cookie_lifecycle():
    from aiohttp import ClientSession
    from yarl import URL

    async def exercise():
        async with ClientSession(trust_env=False) as session:
            session.cookie_jar.update_cookies({"local": "value"}, response_url=URL("https://example.invalid/"))
            assert session.cookie_jar.filter_cookies(URL("https://example.invalid/"))["local"].value == "value"
            assert session.closed is False
        assert session.closed is True

    asyncio.run(exercise())


def test_cryptography_authenticated_encryption_and_tamper_detection():
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    cipher = AESGCM(AESGCM.generate_key(bit_length=128))
    nonce = b"offline-test"
    encrypted = cipher.encrypt(nonce, b"local plaintext", b"context")
    assert cipher.decrypt(nonce, encrypted, b"context") == b"local plaintext"
    with pytest.raises(InvalidTag):
        cipher.decrypt(nonce, encrypted, b"changed context")


def test_cryptography_pyjwt_rsa_round_trip():
    from cryptography.hazmat.primitives.asymmetric import rsa
    import jwt

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = jwt.encode({"sub": "offline-validation"}, private_key, algorithm="RS256")
    assert jwt.decode(token, private_key.public_key(), algorithms=["RS256"]) == {"sub": "offline-validation"}


def test_openai_and_azure_clients_construct_without_credentials_or_requests():
    from azure.ai.inference import ChatCompletionsClient
    from azure.core.credentials import AzureKeyCredential
    from openai import AzureOpenAI

    with AzureOpenAI(
        api_key="offline-placeholder", azure_endpoint="https://example.invalid",
        api_version="2024-10-21",
    ) as client:
        assert client.base_url.host == "example.invalid"
    with ChatCompletionsClient(
        endpoint="https://example.invalid", credential=AzureKeyCredential("offline-placeholder"),
    ) as client:
        assert client is not None


_JWT_TEST_KEY = b"0123456789abcdef0123456789abcdef"


def _signed_token(payload, *, padded=False):
    encode = base64.urlsafe_b64encode
    trim = (lambda value: value) if padded else (lambda value: value.rstrip(b"="))
    header = trim(encode(b'{"alg":"HS256","typ":"JWT"}'))
    payload = trim(encode(payload))
    message = header + b"." + payload
    signature = trim(encode(hmac.new(_JWT_TEST_KEY, message, hashlib.sha256).digest()))
    return message + b"." + signature


def test_pyjwt_claims_algorithms_and_signature_validation():
    import jwt

    payload = {"sub": "offline", "iss": "local-issuer", "aud": "local-audience",
               "exp": datetime.now(timezone.utc) + timedelta(minutes=2)}
    token = jwt.encode(payload, _JWT_TEST_KEY, algorithm="HS256")
    options = {"require": ["exp", "iss", "aud", "sub"]}
    decoded = jwt.decode(token, _JWT_TEST_KEY, algorithms=["HS256"], issuer="local-issuer",
                         audience="local-audience", options=options)
    assert decoded["sub"] == "offline"
    with pytest.raises(jwt.InvalidAudienceError):
        jwt.decode(token, _JWT_TEST_KEY, algorithms=["HS256"], audience="wrong")
    with pytest.raises(jwt.InvalidIssuerError):
        jwt.decode(token, _JWT_TEST_KEY, algorithms=["HS256"], issuer="wrong", audience="local-audience")
    with pytest.raises(jwt.InvalidAlgorithmError):
        jwt.decode(token, _JWT_TEST_KEY, algorithms=["RS256"])
    expired = jwt.encode({"exp": 1}, _JWT_TEST_KEY, algorithm="HS256")
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(expired, _JWT_TEST_KEY, algorithms=["HS256"])
    header, _, signature = token.encode().split(b".")
    changed = base64.urlsafe_b64encode(b'{"sub":"changed"}').rstrip(b"=")
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(header + b"." + changed + b"." + signature, _JWT_TEST_KEY, algorithms=["HS256"])


def test_pyjwt_deep_payload_raises_decode_error_instead_of_recursion_error():
    import jwt

    # CPython 3.12's C JSON decoder has its own recursion limit, so use a
    # genuinely too-deep document rather than changing sys.getrecursionlimit().
    payload = b'{"nested":' + b"[" * 10000 + b"0" + b"]" * 10000 + b"}"
    with pytest.raises(RecursionError):
        json.loads(payload)
    with pytest.raises(jwt.DecodeError):
        jwt.decode(_signed_token(payload), _JWT_TEST_KEY, algorithms=["HS256"])


def test_pyjwt_inconsistent_ed25519_private_jwk_is_rejected():
    import jwt
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization

    private = Ed25519PrivateKey.generate()
    unrelated = Ed25519PrivateKey.generate().public_key()
    raw_private = private.private_bytes(serialization.Encoding.Raw,
        serialization.PrivateFormat.Raw, serialization.NoEncryption())
    raw_public = unrelated.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    encode = lambda data: base64.urlsafe_b64encode(data).rstrip(b"=").decode()
    jwk = {"kty": "OKP", "crv": "Ed25519", "d": encode(raw_private), "x": encode(raw_public)}
    with pytest.raises(jwt.InvalidKeyError):
        jwt.PyJWK.from_dict(jwk)


def test_pyjwt_padded_signature_remains_compatible():
    import jwt

    token = _signed_token(json.dumps({"sub": "padded-compatibility"}, separators=(",", ":")).encode(), padded=True)
    assert token.split(b".")[-1].endswith(b"=")
    assert jwt.decode(token, _JWT_TEST_KEY, algorithms=["HS256"]) == {"sub": "padded-compatibility"}


def test_urllib3_retry_and_gzip_response_lifecycle():
    import gzip
    from urllib3.response import HTTPResponse
    from urllib3.util.retry import Retry

    retry = Retry(total=2, status_forcelist={503}, allowed_methods=None)
    response = HTTPResponse(status=503, headers={"Retry-After": "3"})
    assert retry.is_retry("POST", 503)
    assert retry.get_retry_after(response) == 3
    next_retry = retry.increment(method="POST", response=response)
    assert next_retry.total == 1
    assert len(next_retry.history) == 1
    decoded = HTTPResponse(body=BytesIO(gzip.compress(b"local response")),
        headers={"Content-Encoding": "gzip"}, decode_content=True)
    assert decoded.data == b"local response"


def test_urllib3_chunk_size_line_is_bounded():
    import http.client
    from urllib3.exceptions import ProtocolError
    from urllib3.response import HTTPResponse

    class MemorySocket:
        def makefile(self, *args, **kwargs):
            return BytesIO(b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n" +
                           b"f" * 65537 + b"\r\n")

    raw = http.client.HTTPResponse(MemorySocket(), method="GET")
    raw.begin()
    response = HTTPResponse(body=raw, headers=dict(raw.getheaders()), status=raw.status,
        original_response=raw, preload_content=False, request_method="GET")
    with pytest.raises(ProtocolError, match="chunk size line exceeded"):
        list(response.read_chunked())


def test_urllib3_deflate_decoder_drains_at_eof_without_looping():
    import zlib
    from urllib3.response import DeflateDecoder

    decoder = DeflateDecoder()
    decoded = decoder.decompress(zlib.compress(b"A" * 100) + b"tail", max_length=50)
    for _ in range(4):
        decoded += decoder.decompress(b"", max_length=50)
        if not decoder.has_unconsumed_tail:
            break
    assert decoded == b"A" * 100
    assert decoder.has_unconsumed_tail is False


@pytest.mark.parametrize("certificate_hostname", ["xn--fa-hia.de", "fass.de"])
def test_anyio_tls_verifies_idna2008_hostname_in_memory(tmp_path, certificate_hostname):
    import ssl

    import anyio
    from anyio.streams.stapled import StapledObjectStream
    from anyio.streams.tls import TLSStream
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    # All key material and certificates are generated locally for this test.
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, certificate_hostname)])
    now = datetime.now(timezone.utc)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(name).issuer_name(name).public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(certificate_hostname)]), critical=False)
        .sign(key, hashes.SHA256())
    )
    certificate_pem = certificate.public_bytes(serialization.Encoding.PEM)
    certificate_path = tmp_path / "local-certificate.pem"
    key_path = tmp_path / "local-key.pem"
    certificate_path.write_bytes(certificate_pem)
    key_path.write_bytes(key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ))
    key_path.chmod(0o600)
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.load_cert_chain(certificate_path, key_path)
    client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    client_context.load_verify_locations(cadata=certificate_pem.decode())

    async def exercise():
        server_send, server_receive = anyio.create_memory_object_stream[bytes](1)
        client_send, client_receive = anyio.create_memory_object_stream[bytes](1)
        client_stream = StapledObjectStream(client_send, server_receive)
        server_stream = StapledObjectStream(server_send, client_receive)

        async def server():
            try:
                async with await TLSStream.wrap(
                    server_stream, server_side=True, ssl_context=server_context,
                ) as stream:
                    await stream.send((await stream.receive())[::-1])
            except ssl.SSLError:
                # The deliberately wrong certificate causes a client TLS alert.
                if certificate_hostname == "xn--fa-hia.de":
                    raise

        with anyio.fail_after(5):
            async with client_stream, server_stream, anyio.create_task_group() as tasks:
                tasks.start_soon(server)
                if certificate_hostname == "fass.de":
                    with pytest.raises(ssl.SSLCertVerificationError):
                        await TLSStream.wrap(client_stream, hostname="faß.de", ssl_context=client_context)
                    tasks.cancel_scope.cancel()
                else:
                    async with await TLSStream.wrap(
                        client_stream, hostname="faß.de", ssl_context=client_context,
                    ) as stream:
                        await stream.send(b"hello")
                        assert await stream.receive() == b"olleh"

    anyio.run(exercise)


def test_anyio_process_worker_does_not_block_on_stdout_or_stderr():
    import os
    import signal
    import subprocess
    import sys

    # Isolate teardown too: the vulnerable worker pool can hang even during
    # cancellation, so an outer deadline must protect the pytest process.
    driver = '''
import socket
def network_disabled(*args, **kwargs):
    raise RuntimeError("Network access is disabled in the offline worker test")
socket.socket.connect = socket.socket.connect_ex = network_disabled
socket.create_connection = socket.getaddrinfo = network_disabled
import anyio
from anyio import to_process
async def exercise():
    with anyio.fail_after(10):
        result = await to_process.run_sync(
            exec,
            'import sys; sys.stderr.write("x" * 1048576); sys.stderr.flush(); '
            'sys.stdout.write("x" * 1048576); sys.stdout.flush()',
            cancellable=True,
        )
        assert result is None
        assert await to_process.run_sync(pow, 2, 8, cancellable=True) == 256
anyio.run(exercise)
'''
    process = subprocess.Popen(
        [sys.executable, "-c", driver], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, start_new_session=os.name == "posix",
    )
    try:
        stdout, stderr = process.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        process.communicate(timeout=5)
        pytest.fail("AnyIO process worker or teardown exceeded the offline test deadline")
    assert process.returncode == 0, stderr
    assert stdout == ""
