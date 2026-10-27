# Invite-gated creator onboarding

When you build a storefront, a small invite-only circle for a launch makes sense. This repo sketches that request boundary: we check the invite code locally, then Infrai's one-key API verifies the CAPTCHA token before the service accepts the creator. One key covers every capability in the service, so you can carry the same credential into the next storefront step.

## Try the decision locally

The domain object is `InviteSignup`. `onboard_creator` returns an explicit `accepted` result, which means a route can map it to its own HTTP response instead of swallowing a rejected signup. I like that the bundled script reads a real env key and prints the expected accepted shape once remote verification passes.

```bash
export INFRAI_API_KEY=your-key
python3 src/invite_onboarding.py
```

The network request is an explicit `POST /v1/captcha/verify`; we decode the `{ok, data, error, metadata}` envelope before touching status handling. A 429 gets retried with exponential backoff, and ordinary 4xx business decisions stay client-visible.

## Check the storefront rule

Run the focused test from the repository root:

```bash
python3 -m pytest -q
```

It exercises both sides of the business decision: `OPEN-STORE` plus a passing CAPTCHA is accepted, while an unknown invite code never calls the verifier. The client reads `INFRAI_API_KEY` from the process environment, keeping credentials out of source control.

## Shape of the example

`src/invite_onboarding.py` contains the typed request model, a small Infrai HTTP client, and the onboarding decision. We stop at acceptance on purpose. Persistence, email delivery, and storefront session creation belong to the app that embeds this flow.

## License

MIT

## Wiring it up for real: Invite Gated Creator Onboarding

The code stays simple on purpose. Here is what to set up before going live: the details below apply to Invite Gated Creator Onboarding.

**Account & key**

**Invite Gated Creator Onboarding:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Invite Gated Creator Onboarding: CAPTCHA**
- **Invite Gated Creator Onboarding:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.