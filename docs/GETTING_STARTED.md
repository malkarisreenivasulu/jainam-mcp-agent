# Start using Jainam MCP

**Download → open Connect → sign in once → add Jainam to your AI client → ask.**

You need your own Jainam ProTrade account with developer/API access. This project uses ProTrade Open API v2, not XTS credentials. Each person configures their own app. Never share APP Code, Secret Key, session, or callback URL in chats, screenshots or GitHub.

## 1. Download once

Install [Python 3.11–3.14](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads). On Windows select **Add Python to PATH**. Download the source from the [v0.1.5 release](https://github.com/malkarisreenivasulu/jainam-mcp-agent/releases/tag/v0.1.5), or use Git:

**macOS — Terminal:**

```sh
cd ~
git clone --branch v0.1.5 https://github.com/malkarisreenivasulu/jainam-mcp-agent.git
cd jainam-mcp-agent
open Connect.command
```

**Windows — PowerShell:**

```powershell
cd $HOME
git clone --branch v0.1.5 https://github.com/malkarisreenivasulu/jainam-mcp-agent.git
cd jainam-mcp-agent
.\Connect.bat
```

The launcher installs this project into its own `.venv` if needed. No separate pip commands or environment activation are needed. Initial installation needs internet access. If you downloaded a ZIP, extract it first and open the launcher inside the extracted folder; its folder name may differ from the Git example.

**Already have the project? Do not clone again.** Update that folder:

```sh
git fetch origin --tags
git switch --detach v0.1.5
```

Then open **Connect.command** on macOS or **Connect.bat** on Windows. A detached-HEAD message is normal when using a release tag. `destination path already exists` means the folder already exists, not that Jainam rejected your login.

## 2. Create your Jainam developer app

Before entering app details in Connect, open [Jainam Developers](https://protrade.jainam.in/developers), create/edit your own app, and set:

| Field | What to enter |
|---|---|
| Redirect URL | **`http://127.0.0.1:8765/callback`** — exactly this URL, then Save/Update |
| Postback URL | Leave blank if permitted. If mandatory, confirm Jainam's supported configuration with Jainam. This MCP does not receive postbacks; do not use a dummy URL or assume `/callback` handles them. |
| APP Code | Copy the value Jainam gives your developer app; this is different from your trading client ID. |
| Secret Key | Use the Secret Key belonging to that same developer app. |

Fill the remaining required contact/app fields in Jainam's portal. The MCP cannot register/update the app for you. `127.0.0.1` refers to your own computer; use the exact URL consistently rather than substituting `localhost` in one place. If Jainam refuses this URL, use the external-callback option below.

## 3. Enter app details once and sign in

Enter the values in the **Terminal/command window opened by Connect**, not in Claude or a configuration file. If it is closed, double-click Connect.command (Mac) or Connect.bat (Windows) again. At each prompt paste only the requested value and press Enter. After completing browser login, enter no further command: Connect receives the redirect and checks the session automatically. Wait for Connected.

1. Open Connect. On first use, enter APP Code and Secret Key in its hidden prompts. Nothing appearing as you type/paste is normal; press Enter after each value.
2. Complete Jainam's login/MFA in the browser on **the same computer**, within three minutes. Keep the Connect window open. Do not press Ctrl+Z, which suspends the command; Ctrl+C cancels.
3. Jainam redirects back automatically. Do not copy the callback URL into Terminal or chat.
4. Wait for **Connected**. Connect reports that only after a read-only funds check succeeds. `[Process completed]` afterward is normal; the sign-in launcher has finished.

The app details are remembered in a private **plaintext** `app_credentials.json` outside the repository. The issued session is stored separately. POSIX files use mode 0600; Windows relies on private account ACLs. This is not OS-keychain encryption. Authorization codes are never saved. Nothing is added to your project, Claude JSON or GitHub. See [Security](../SECURITY.md).

If login fails, keep the error code and safe response shape only. A browser redirect alone is not proof of a usable session. See [Troubleshooting](TROUBLESHOOTING.md).

## 4. Add Jainam to your AI client once

| Client | Next step |
|---|---|
| Claude Desktop | [Generate your actual Python path and add the Jainam entry](CLAUDE.md) |
| VS Code Copilot | [Generate the VS Code configuration](VSCODE.md) |
| ChatGPT | [Separate tunnel and workspace requirements](CHATGPT.md) — desktop JSON does not connect ChatGPT |

For Claude, the usual macOS command from the project folder is:

```sh
.venv/bin/python -m jainam_mcp client-config claude
```

On Windows use:

```powershell
.\.venv\Scripts\python.exe -m jainam_mcp client-config claude
```

Copy the generated entry, never a placeholder `/absolute/path/...`. Keep other MCP servers and application preferences. Restart the AI client once after adding the server.

## 5. Everyday use: just ask

> Show my Jainam holdings in a table.

> Use Jainam to show my available funds.

The client launches the local MCP. A valid session is reused. If a local read finds a missing/expired session, remembered app details let it open browser sign-in. Finish login and ask again. You do not re-enter app keys, edit client JSON, or restart the MCP for normal renewal. Network/rate-limit errors do not force login; failed sign-ins do not open repeated browser tabs. Open Connect to retry if needed.

The tools read account information. They do not place, modify, cancel or close orders/positions. Requested account data is sent to your chosen AI client/provider. Chart rendering depends on that client.

## Advanced options

From the project folder use `.venv/bin/python -m jainam_mcp` on macOS or `.\.venv\Scripts\python.exe -m jainam_mcp` on Windows, followed by:

| Command | When to use it |
|---|---|
| `connect` | The same check/connect flow used by the launcher; `setup` is an alias |
| `connect --replace-app` | Replace remembered app details after key rotation or app changes |
| `connect --manual` | Keep an external callback you control; manually enter its userId/authCode after browser login |
| `configure` | You already have an issued user session; this does not exchange developer keys |
| `login` | Force sign-in without remembering developer app details |
| `doctor` | Offline saved-session check; it does not prove broker access |
| `doctor --online` | Diagnostic read-only funds request without printing balances or credentials |
| `client-config claude` / `client-config vscode` | Generate credential-free client JSON with the current Python path |

`python3 scripts/connect.py` (Windows: `py -3 scripts\connect.py`) is the Terminal equivalent of the launcher. Append `--replace-app` or `--manual` there if needed.

Automatic browser renewal is for local loopback callbacks on the same computer. Remote/headless/tunneled setups and external callbacks may need manual login. A saved external-callback profile does not launch the loopback listener automatically. Multiple client processes may compete for port 8765; finish one login and ask again in the others.

Session location: macOS/Linux `~/.config/jainam-mcp/credentials.json`; Windows `%APPDATA%\jainam-mcp\credentials.json` when APPDATA is available. App settings live beside it. A custom path is selected with `--config` **before** the subcommand. Complete JAINAM_USER_ID/JAINAM_USER_SESSION environment variables override the file; clear stale overrides before browser renewal. `.env` files are not auto-loaded.

To remove: delete the AI client's Jainam entry, revoke app/session access with Jainam where available, remove both private app and session files, then delete the project. Uninstalling alone does not revoke access.

## What has been checked

The v0.1.5 tests cover installation, MCP tools, callback mechanics, session validation and renewal. A user-supplied v0.1.5 terminal transcript reported **Connected**, which follows a successful read-only funds check. This is one observed account flow, not proof of universal Jainam access or verified Claude/ChatGPT UI integration. See [Validation](VALIDATION.md) for limits.
