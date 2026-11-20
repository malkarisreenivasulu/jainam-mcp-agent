# Troubleshooting

Start with `python -m jainam_mcp doctor`. To test broker connectivity explicitly, add `--online`.

| Symptom | Action |
|---|---|
| Python/Git not found | Install prerequisites, reopen Terminal; on Windows try `py -3` |
| Unsupported Python | Create a new venv with Python 3.11–3.14; do not reuse another project's old venv |
| Installation cannot fetch SDK | Git and outbound GitHub access are required. Check your proxy/certificates; never disable TLS verification |
| `No module named jainam_mcp` | Use this project's `.venv` Python and install with `python -m pip install .` |
| `NOT_CONFIGURED` | Run `configure` in your own terminal under the same OS user as the client |
| Partial environment configuration | Set both JAINAM variables or unset both; no partial file fallback |
| `SESSION_EXPIRED_OR_DENIED` | Renew your own session using login/configure and restart every MCP client process |
| `BROKER_ERROR` | Check account entitlement and current API docs; a broker may report errors with HTTP 200 |
| `RATE_LIMITED` | Stop repeated requests and retry later according to broker guidance |
| `NETWORK_ERROR` | Check internet, Jainam availability and certificates; no DNS/IP patches are installed |
| No candles | Verify current token, exchange, resolution, millisecond timestamps and broker data availability |
| Instrument search returns `BROKER_ERROR` | The broker may be returning a web/login page or unusable CSV. Confirm a valid session, entitlement and current endpoint with Jainam; this is not an empty-symbol result |
| No instrument matches | Use a shorter query and correct exchange; contract masters change |
| POSIX permission error | Run `chmod 600` on your private credentials file, not on a shared directory |
| Server is silent in Terminal | Normal for stdio MCP: the AI client must launch it; Ctrl+C exits |
| Tools absent in Claude/VS Code | Generate config with the correct venv Python, merge valid JSON, restart server/client and review tool selection |
| ChatGPT cannot see a tunnel | Check its organization/workspace association, access and running tunnel client using OpenAI's guide |

`jainam_status` is an offline configuration check. Only `doctor --online` or a broker-reading tool verifies connectivity. Never treat `credentials_configured: true` as proof of a valid session.

`login` needs your existing registered callback; it does not capture redirects itself. If the exchange response cannot be recognized, the command fails safely without printing it. Use Jainam's documented process to obtain a session and run `configure`.

When reporting a bug include OS, Python/package versions, failing tool name and the sanitized error code. Do not include `.env`, credentials files, broker HTTP bodies/headers, full callback URLs, account screenshots or raw financial results. Never paste secrets into a GitHub issue.

## First-time sign-in checklist (v0.1.3)

- `NOT_CONFIGURED`: installation succeeded but no session has been saved. Run `python -m jainam_mcp setup`. `configure` requires an existing session; it does not exchange APP Code or Secret Key.
- `connection_tested: false` with `doctor --online`: missing credentials prevented a broker request. Resolve setup first.
- `zsh: suspended`: Ctrl+Z suspended setup. Use `jobs` to inspect suspended commands, resume the intended one with `fg`, and cancel it with Ctrl+C before starting fresh.
- A credentials JSON path is a file, not a shell command. Do not execute or paste its contents. It is created only after successful setup/configure.
- Callback timeout: verify the exact registered Redirect URL, use the browser on the same machine, and check Jainam login completed. For external callbacks use `login --manual`.
- Browser success alone is insufficient: wait for Terminal confirmation and check `doctor --online`. Regenerate any secret accidentally shared in chat, screenshots or issues.

## Session exchange failed after the browser returned (v0.1.4)

A successful callback means the redirect reached this computer. It does not mean
Jainam issued a usable session. Do not paste the callback URL into a shell or chat.

- `AUTH_EXCHANGE_REJECTED`: Jainam explicitly rejected the exchange (including HTTP 200 with `status: NotOk`). Run setup again for a fresh authorization code. If the APP Code/Secret Key pair is correct and it repeats, confirm API entitlement/app status with Jainam. This error alone does not prove a wrong secret.
- `AUTH_RESPONSE_UNSUPPORTED`: response lacks a unique explicitly named `userSession`. The printed **safe response shape** contains only fixed field names, types and array counts, never raw response values or arbitrary field names. Share only that diagnostic. Do not rename an unknown `token` field to `userSession` without a verified broker contract.
- `AUTH_HTTP_ERROR`, `AUTH_NON_JSON`, `AUTH_NETWORK_ERROR`: the HTTP status, response format or network prevented exchange. Retry with a fresh authorization after resolving connectivity/service issues.

Failed setup does not overwrite an existing credentials file. `configure` cannot
repair a rejected exchange; it only stores a session already issued by Jainam.

The v0.1.3 error “No unique userSession found” conflated a broker rejection with
an unsupported response schema. Upgrade to v0.1.4 for explicit diagnostics.
