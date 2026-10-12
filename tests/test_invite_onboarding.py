from src.invite_onboarding import InviteSignup, onboard_creator


class CaptchaStub:
    def __init__(self):
        self.tokens = []

    def verify_captcha(self, token, widget_record_id):
        self.tokens.append((token, widget_record_id))
        return {"success": True}


def test_valid_invite_and_captcha_accept_creator():
    stub = CaptchaStub()
    request = InviteSignup("shop@example.com", "secret", "Mina", "OPEN-STORE", "captcha-token", "widget-id")
    result = onboard_creator(request, stub, {"OPEN-STORE"})
    assert result["accepted"] is True
    assert result["community"] == "creator-commerce"
    assert stub.tokens == [("captcha-token", "widget-id")]


def test_unknown_invite_does_not_call_captcha():
    stub = CaptchaStub()
    request = InviteSignup("shop@example.com", "secret", "Mina", "NOPE", "captcha-token", "widget-id")
    result = onboard_creator(request, stub, {"OPEN-STORE"})
    assert result == {"accepted": False, "reason": "invite_code_rejected"}
    assert stub.tokens == []
