# Set up Jainam MCP Agent on your computer

You do not need to be a programmer. Do each step in order. Never paste your API secret, session or authorization code into an AI conversation, GitHub issue or screenshot.

## 1. What you need

- A Jainam account with access to [ProTrade developer applications](https://protrade.jainam.in/developers). Check API eligibility and charges directly with Jainam.
- Python 3.11, 3.12, 3.13 or 3.14 from [python.org](https://www.python.org/downloads/). On Windows select **Add Python to PATH**.
- [Git](https://git-scm.com/downloads), including on Windows: installation fetches the pinned SDK from GitHub.
- Claude Desktop or VS Code with an MCP-capable Copilot setup. ChatGPT has additional tunnel/workspace requirements explained separately.

Verify in Terminal (macOS/Linux) or PowerShell (Windows):

```sh
python --version
git --version
```

If `python` is not found on macOS/Linux, try `python3`. On Windows try `py -3`. Use the same Python throughout. Stop if it is older than 3.11.

## 2. Download the released source

```sh
git clone --branch v0.1.3 https://github.com/malkarisreenivasulu/jainam-mcp-agent.git
cd jainam-mcp-agent
```

A detached-HEAD message from cloning a release tag is normal. You are using a fixed release rather than a moving development branch.

## 3. Install in its own environment

macOS/Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

Windows PowerShell (activation is not necessary):

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
```

For subsequent Windows commands in this guide, use `.\.venv\Scripts\python.exe` wherever you see `python`. This also avoids PowerShell script-execution-policy issues. Never install this using `sudo pip`.

The installation downloads the MCP SDK and the maintainer's public Jainam Python SDK, pinned to the commit behind v0.1.1. Nothing is read from the maintainer's private computer or from your existing project `.env` files.

## 4. Choose one sign-in method

A **user session** is a secret temporary credential issued by Jainam. Your developer **appCode** identifies an app; **apiSecret** signs its login exchange. They are different from the issued session.

### If you already have a valid session

```sh
python -m jainam_mcp configure
```

At the hidden prompts enter your Jainam user ID and user session. Input is deliberately not echoed. Paste only the session value, not an entire response or callback URL. Credentials are saved outside this repository:

- macOS/Linux: `~/.config/jainam-mcp/credentials.json`
- Windows: `%APPDATA%\jainam-mcp\credentials.json` when APPDATA is available; otherwise `~/.config/jainam-mcp/credentials.json`.

On POSIX the new file is mode `0600`. On Windows protect it with your user account's normal private file permissions; POSIX modes are not Windows ACL guarantees. This is plaintext local storage, not a vault or encryption. Prefer a non-synced private location. See [Security](../SECURITY.md).

### Recommended: guided sign-in with your developer app

**Set these fields while creating the app, before running `setup`:**

| Jainam app field | Required action for this MCP |
|---|---|
| Redirect URL | Enter exactly `http://127.0.0.1:8765/callback`. This is the MCP default, not your APP Code. Click Save/Update. |
| Postback URL | Leave blank if allowed. The package does not receive postbacks. If Jainam requires this field, ask Jainam for its supported configuration before proceeding. Do not use a dummy URL or `/callback` as an implemented postback endpoint. |

The default is built into the MCP, but **registration in your Jainam app is manual and required**. The command cannot update your developer app settings. Do not substitute `localhost` in only one place: this listener uses the exact `127.0.0.1:8765` address. If Jainam rejects the loopback URL, use the manual method below with a real callback you control.

1. Open the [Jainam developer portal](https://protrade.jainam.in/developers) and create or edit your own app. This release uses **ProTrade Open API v2**, not XTS API keys.
2. Fill in the required developer contact/app fields. Set **Redirect URL** to exactly `http://127.0.0.1:8765/callback` and save. Postback URL is a separate broker setting; this package does not implement a postback receiver. Follow Jainam's requirements for that field rather than assuming the login callback handles it.
3. Note the app's **APP Code** and **Secret Key**. APP Code identifies your developer app; your trading client ID is different. API eligibility and available app settings depend on Jainam.
4. In the activated environment run:

   ```sh
   python -m jainam_mcp setup
   ```

5. Enter APP Code, then Secret Key at the hidden prompts. Nothing appearing while you type or paste is normal. Press Enter after each value. Do not press Ctrl+Z: that suspends the command instead of completing it. Ctrl+C cancels.
6. Complete Jainam login/MFA in the browser on **the same computer** within three minutes. Jainam redirects to your registered URL. The local listener captures `userId` and `authCode`; you do not copy them. Return to Terminal for the saved-session confirmation. The Secret Key and auth code are not saved.
7. Run `python -m jainam_mcp doctor --online`. Proceed only when `credentials_configured` and `online_ok` are true. A saved session alone does not prove broker access.
8. Generate your client configuration below and restart your MCP client.

The listener binds only to `127.0.0.1:8765`, starts before the browser opens, suppresses callback request logging, and closes after capture, cancellation or timeout. Never expose this port publicly. It expects GET callback query parameters named `userId` and `authCode`. This is broker SSO, not MCP OAuth. No broker password is collected by the package. No undocumented state parameter is added; the broker callback is not claimed to have cryptographic state correlation. The broker session exchange validates the authorization code with your app secret.

**Important limitation:** automated tests use synthetic callbacks, not real Jainam accounts. Loopback Redirect URL acceptance, actual callback fields, MFA and API entitlement must be verified with your own app. This update does not claim a successful production login for every account.

### Existing external callback or loopback URL rejected

If Jainam refuses a loopback redirect, or you already have a reachable callback you control, retain that registered URL and run:

```sh
python -m jainam_mcp login --manual
```

Enter APP Code and Secret Key, complete browser sign-in, then enter the `userId` and fresh `authCode` received by your callback at the hidden terminal prompts. The package cannot receive a callback sent to an arbitrary website. Do not use someone else's callback URL. Expired or already-used codes require a new login. If your broker response has no unique `userSession`, login stops without printing its payload.

If port 8765 is occupied, close the other app or use the manual method. Remote SSH/headless setup should use a callback you control and the manual method; localhost in a remote browser is not necessarily the machine running Python.

### Upgrading an existing clone

Keep your private credentials file; do not delete or publish it. From your clone:

```sh
git fetch origin --tags
git switch --detach v0.1.3
python -m pip install .
python -m jainam_mcp setup
python -m jainam_mcp doctor --online
```

Restart each MCP client after renewal. If the existing clone is elsewhere, use its activated environment. Only run commands for your operating system; Windows `py` and `Scripts\python.exe` commands do not work in macOS zsh.

### Advanced: environment variables

If both `JAINAM_USER_ID` and `JAINAM_USER_SESSION` are present, they override the file. A partial pair fails explicitly; it will not combine one account's ID with another session. Use your local secret manager to set them. The server never auto-loads `.env`, and examples deliberately contain no secret values. Clear old variables if changing back to file configuration.

## 5. Check setup

```sh
python -m jainam_mcp doctor
```

Expected: `credentials_configured: true`, `connection_tested: false`. This proves configuration can load, **not** that Jainam accepts the session.

Optionally verify the session using one read-only funds request:

```sh
python -m jainam_mcp doctor --online
```

Expected: `online_ok: true`. The diagnostic does not print funds, session tokens, account IDs or broker error bodies. If it fails, use [Troubleshooting](TROUBLESHOOTING.md).

## 6. Connect your AI client

Choose [Claude](CLAUDE.md), [VS Code](VSCODE.md), or [ChatGPT](CHATGPT.md). Run the client-config command with **this environment's Python** so it generates the right absolute path.

## 7. First requests

- “Use jainam_status to check configuration.”
- “Using Jainam tools, summarize my holdings. Do not make recommendations.”
- “Show my existing positions and explain the returned fields.”
- “Search MCX contracts containing GOLD, limit 5.”

If you run `serve` yourself, a quiet terminal is normal: it waits for MCP protocol messages from a client. Do not type secrets into it. Ctrl+C stops it.

## Renew a session / remove the project

When the broker expires a session, rerun `login` or `configure`, then **restart the MCP server in each client**. Sessions load once per server process. Expiry is set by Jainam, not promised by this project.

To remove it, delete the client's `jainam` entry and the local credentials file, revoke the session/app at Jainam where available, then delete the project folder. Uninstalling the Python package alone does not revoke a broker session.
