"""Exercise updated dependencies locally, without models, downloads, or tokens."""

import asyncio
from datetime import datetime, timezone
from io import BytesIO
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
