"""Exercise the transitive OAuth client and provider APIs without transport."""

import base64
import hashlib
import json
from types import SimpleNamespace
from urllib.parse import parse_qs, urlencode, urlparse
from unittest.mock import patch

import pytest


def test_requests_oauthlib_authorization_code_pkce_round_trip():
    from oauthlib.oauth2 import RequestValidator, Server
    from requests import Response
    from requests.adapters import BaseAdapter
    from requests_oauthlib import OAuth2Session

    class Validator(RequestValidator):
        def __init__(self):
            self.codes = {}

        def validate_client_id(self, client_id, request):
            request.client = SimpleNamespace(client_id=client_id)
            return client_id == "offline-client"

        def validate_redirect_uri(self, client_id, redirect_uri, request):
            return redirect_uri == "https://client.example.invalid/callback"

        def validate_response_type(self, client_id, response_type, client, request):
            return response_type == "code"

        def validate_scopes(self, client_id, scopes, client, request):
            return scopes == ["read"]

        def is_pkce_required(self, client_id, request):
            return True

        def save_authorization_code(self, client_id, code, request):
            self.codes[code["code"]] = request

        def client_authentication_required(self, request):
            return False

        def authenticate_client_id(self, client_id, request):
            return self.validate_client_id(client_id, request)

        def validate_grant_type(self, client_id, grant_type, client, request):
            return grant_type == "authorization_code"

        def validate_code(self, client_id, code, client, request):
            saved = self.codes.get(code)
            if saved is None:
                return False
            request.user = "offline-user"
            request.scopes = saved.scopes
            return saved.client_id == client_id

        def get_code_challenge(self, code, request):
            return self.codes[code].code_challenge

        def get_code_challenge_method(self, code, request):
            return self.codes[code].code_challenge_method

        def confirm_redirect_uri(self, client_id, code, redirect_uri, client, request):
            return self.codes[code].redirect_uri == redirect_uri

        def save_bearer_token(self, token, request):
            self.token = token

        def invalidate_authorization_code(self, client_id, code, request):
            self.codes.pop(code)

    class LocalTokenAdapter(BaseAdapter):
        def send(self, request, **kwargs):
            assert request.url == "https://auth.example.invalid/token"
            headers, body, status = server.create_token_response(
                request.url, http_method=request.method,
                body=request.body, headers=request.headers,
            )
            response = Response()
            response.status_code = status
            response.headers.update(headers)
            response._content = body.encode()
            response.request = request
            return response

        def close(self):
            pass

    for method in ("plain", "S256"):
        validator = Validator()
        server = Server(validator)
        verifier = "a" * 43
        challenge = verifier if method == "plain" else base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode()).digest()
        ).decode().rstrip("=")
        with OAuth2Session(
            "offline-client", scope=["read"],
            redirect_uri="https://client.example.invalid/callback",
        ) as session:
            session.mount("https://", LocalTokenAdapter())
            authorization_url, state = session.authorization_url(
                "https://auth.example.invalid/authorize",
                code_challenge=challenge, code_challenge_method=method,
            )
            headers, _, status = server.create_authorization_response(
                authorization_url, scopes=["read"], credentials={"user": "offline-user"},
            )
            assert status == 302
            callback_url = headers["Location"]
            assert parse_qs(urlparse(callback_url).query)["state"] == [state]
            code = parse_qs(urlparse(callback_url).query)["code"][0]
            wrong_body = urlencode({
                "client_id": "offline-client", "grant_type": "authorization_code",
                "code": code, "redirect_uri": session.redirect_uri,
                "code_verifier": "b" * 43,
            })
            _, rejected, status = server.create_token_response(
                "https://auth.example.invalid/token", body=wrong_body,
            )
            assert status == 400
            assert json.loads(rejected)["error"] == "invalid_grant"
            token = session.fetch_token(
                "https://auth.example.invalid/token", authorization_response=callback_url,
                include_client_id=True, code_verifier=verifier,
            )
            assert token["token_type"] == "Bearer"
            assert token["scope"] == ["read"]
            assert token["access_token"] == validator.token["access_token"]
            assert code not in validator.codes


def test_requests_oauthlib_refresh_used_by_kubernetes():
    from requests import Response
    from requests_oauthlib import OAuth2Session

    # Exercise the same requests-oauthlib refresh API used by kube_config.
    # The mocked send returns a local response; the socket guard stays active.
    with OAuth2Session("offline-client", token={"refresh_token": "old-refresh"}) as session:
        def respond(request, **kwargs):
            assert request.url == "https://auth.example.invalid/token"
            fields = parse_qs(request.body)
            assert fields["grant_type"] == ["refresh_token"]
            assert fields["refresh_token"] == ["old-refresh"]
            assert request.headers["Authorization"].startswith("Basic ")
            response = Response()
            response.status_code = 200
            response._content = json.dumps({
                "access_token": "new-access", "token_type": "Bearer",
                "refresh_token": "new-refresh", "id_token": "offline-id", "expires_in": 3600,
            }).encode()
            response.request = request
            return response

        with patch.object(session, "send", side_effect=respond) as send:
            token = session.refresh_token(
                "https://auth.example.invalid/token", refresh_token="old-refresh",
                auth=("offline-client", "offline-secret"),
            )
        assert send.call_count == 1
        assert token["refresh_token"] == "new-refresh"
        assert token["id_token"] == "offline-id"
        assert session.token["access_token"] == "new-access"


def test_oauthlib_revocation_jsonp_removed_and_pkce_uses_constant_time_comparison():
    import hmac
    from oauthlib.oauth2 import RequestValidator, Server
    from oauthlib.oauth2.rfc6749.endpoints.revocation import RevocationEndpoint
    from oauthlib.oauth2.rfc6749.grant_types import authorization_code

    class Validator(RequestValidator):
        def client_authentication_required(self, request):
            return False

        def authenticate_client_id(self, client_id, request):
            return client_id == "offline-client"

        def revoke_token(self, token, token_type_hint, request):
            self.revoked = token

    validator = Validator()
    endpoint = RevocationEndpoint(validator)
    callback = "not_a_callback;void(0)//"
    for client_id, expected_status in (("offline-client", 200), ("invalid-client", 401)):
        _, body, status = endpoint.create_revocation_response(
            "https://auth.example.invalid/revoke", body=urlencode({
                "token": "offline-token", "client_id": client_id, "callback": callback,
            }),
        )
        assert status == expected_status
        assert callback not in body
    assert validator.revoked == "offline-token"
    with pytest.raises(TypeError, match="enable_jsonp"):
        RevocationEndpoint(validator, enable_jsonp=True)

    # A malformed grant must be rejected before client authentication is used.
    with patch.object(validator, "client_authentication_required") as authenticate:
        _, body, status = Server(validator).create_token_response(
            "https://auth.example.invalid/token", body="code=offline-code&client_id=offline-client",
        )
    assert status == 400
    assert "error" in json.loads(body)
    authenticate.assert_not_called()

    verifier = "a" * 43
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    with patch.object(authorization_code.hmac, "compare_digest", wraps=hmac.compare_digest) as compare:
        assert authorization_code.code_challenge_method_plain(verifier, verifier)
        assert not authorization_code.code_challenge_method_plain(verifier, "b" * 43)
        assert authorization_code.code_challenge_method_s256(verifier, challenge)
        assert not authorization_code.code_challenge_method_s256("b" * 43, challenge)
    assert compare.call_count == 4
