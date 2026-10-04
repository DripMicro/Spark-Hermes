---
name: oauthlib
description: Layout, test commands and known weak spots of the oauthlib checkout (OAuth 1 and OAuth 2 request signing and endpoint logic). Load when the issue imports oauthlib.
---
# oauthlib checkout

- Package at `/testbed/oauthlib/`: `oauth1/rfc5849/` (signature, parameters, endpoints), `oauth2/rfc6749/`
  (clients, grant_types, endpoints, tokens, parameters, errors), `openid/connect/core/`, and
  `common.py` (Request object, encoding helpers).
- Tests at `/testbed/tests/`, mirroring the package (for example `tests/oauth2/rfc6749/clients/`).
- Endpoint and grant code returns a triple of headers, body and status. Expected values are exact: header
  names and content types, JSON keys, error codes such as `invalid_request`, status numbers, and the order
  and encoding of query parameters. Assert them literally.
- Validation code is a long chain of checks that raise specific error classes from `oauth2/rfc6749/errors.py`;
  a check removed, inverted, or raising the wrong class is the common change. Sibling grant types
  (authorization_code, implicit, refresh_token, client_credentials, password) implement the same steps
  and are a good reference for what a step should look like.
- Signature helpers in `oauth1/rfc5849/signature.py` are pure functions; a reordered or dropped
  normalisation step shows up as a different base string. Recompute it from the RFC description in the
  docstring.
- OpenID dispatchers pick a handler by inspecting scopes and response types; a swapped choice there inverts
  behaviour for one flow only.
