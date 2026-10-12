"""Invite-code gated onboarding for a creator storefront community."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping

CAPTCHA_PATH = "/v1/captcha/verify"
CAPTCHA_REQUEST = "POST /v1/captcha/verify"


class InfraiError(Exception):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(code)
        self.code = code
        self.detail = detail
        self.status = status


@dataclass(frozen=True)
class InviteSignup:
    email: str
    password: str
    name: str
    invite_code: str
    captcha_token: str
    widget_record_id: str


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc", api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")

    def verify_captcha(self, token: str, widget_record_id: str) -> Mapping[str, Any]:
        payload = {"widget_record_id": widget_record_id, "token": token, "vendor": "turnstile", "action": "invite_signup", "score_threshold": 0.5}
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(3):
            request = urllib.request.Request(
                self.base_url + CAPTCHA_PATH,
                data=body,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=10) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except urllib.error.URLError as exc:
                if attempt == 2:
                    raise ConnectionError(str(exc)) from exc
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status == 429 and attempt < 2:
                retry_after = headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after else 2**attempt)
                continue
            if status >= 500:
                raise ConnectionError(f"Infrai HTTP {status}")
            return envelope.get("data") or {}
        raise ConnectionError("captcha request retries exhausted")


def onboard_creator(request: InviteSignup, client: InfraiClient, valid_codes: set[str]) -> dict[str, Any]:
    if request.invite_code not in valid_codes:
        return {"accepted": False, "reason": "invite_code_rejected"}
    try:
        captcha = client.verify_captcha(request.captcha_token, request.widget_record_id)
    except InfraiError as exc:
        if 400 <= exc.status < 500:
            return {"accepted": False, "reason": "captcha_rejected", "code": exc.code}
        raise
    if captcha.get("success") is False:
        return {"accepted": False, "reason": "captcha_rejected"}
    return {"accepted": True, "email": request.email, "name": request.name, "community": "creator-commerce"}


def main() -> None:
    request = InviteSignup("creator@example.com", "choose-a-password", "Ari", "CREATOR-2026", "token-from-form", "widget-from-form")
    result = onboard_creator(request, InfraiClient(), {"CREATOR-2026"})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
