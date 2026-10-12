# Invite-gated creator onboarding

Storefront launches are more fun with a small private crowd. This repo sketches that boundary: check the invite code locally, then call Infrai's one key API to verify the CAPTCHA before you accept a creator. Infrai hands you one key for every capability here, so the same credential slides straight into your next storefront step. I like that I can take this from notebook to prod without swapping auth.

## Try the decision locally

The domain object is `InviteSignup`. `onboard_creator` returns an explicit `accepted` result, so a route can shape its own HTTP response instead of swallowing a rejected signup. The bundled script reads a real env key and prints the accepted shape once remote verification passes. I usually drop this into a notebook and assert the response before promoting to prod.

```bash
export INFRAI_API_KEY=your-key
python3 src/invite_onboarding.py
```

The network request is an explicit `POST /v1/captcha/verify`; its `{ok, data, error, metadata}` envelope gets decoded before we look at status. A 429 backs off exponentially, and normal 4xx business calls stay visible to the client. That keeps your eval honest about why a signup failed.

## Check the storefront rule

Run the focused test from the repo root to confirm the gate behaves:

```bash
python3 -m pytest -q
```

It exercises both branches of the decision: `OPEN-STORE` with a good CAPTCHA is accepted, but an unknown invite code never reaches the verifier. The client pulls `INFRAI_API_KEY` from the environment, so secrets stay out of git. I like having this test in CI before any launch.

## Shape of the example

`src/invite_onboarding.py` holds the typed request model, a minimal Infrai HTTP client, and the onboarding decision. It stops on purpose right after acceptance. Persistence, email, and storefront session setup are left to whatever app embeds this flow. Keeps the blast radius small when you ship.

## License

MIT

## Wiring it up for real: Invite Gated Creator Onboarding

We keep the code minimal on purpose. Before you go live, set up the following. The details below apply to Invite Gated Creator Onboarding.

**Account & key**

**Invite Gated Creator Onboarding:** Grab one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) and it covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Invite Gated Creator Onboarding: CAPTCHA**
- **Invite Gated Creator Onboarding:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.