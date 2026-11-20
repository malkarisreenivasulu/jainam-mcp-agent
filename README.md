# Jainam MCP Agent

[![CI](https://github.com/malkarisreenivasulu/jainam-mcp-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/malkarisreenivasulu/jainam-mcp-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Connect Claude Desktop, VS Code Copilot, or a supported ChatGPT tunnel to **your own Jainam account**, using a local, read-only Model Context Protocol server.

**Developed by Sreenivasulu Malkari.** Built on [Jainam API Python](https://github.com/malkarisreenivasulu/jainam-api-python) and the official MCP Python SDK. Independent community software, not an official Jainam product.

## First time? Follow these 7 steps

**You do not need to write Python code.** This guide connects **Claude Desktop** to your own Jainam account. You enter your developer app details once, finish Jainam's browser login, and then ask Claude for account information.

### Step 1 — Install the three things you need

| Install | What it is for |
|---|---|
| [Python 3.11–3.14](https://www.python.org/downloads/) | Runs Jainam MCP. On Windows, select **Add Python to PATH** during installation. |
| [Git](https://git-scm.com/downloads) | Downloads the project. |
| [Claude Desktop](https://claude.ai/download) | The app where you will ask questions. |

You also need **your own Jainam account with ProTrade developer/API access**. Installing this project does not create a broker account or grant API access. If you do not have that access, confirm eligibility with Jainam first.

### Step 2 — Create your Jainam app once

1. Open [Jainam Developers](https://protrade.jainam.in/developers) in your browser and sign in.
2. Open **My Apps** and create a new app, or edit your existing app. Fill in the required app/contact details.
3. Enter the following URL in **Redirect URL**:

   ```text
   http://127.0.0.1:8765/callback
   ```

4. Click **Save/Update**. Keep this page open: you will need the app's **APP Code** and **Secret Key** in Step 4.

**What about Postback URL?** Leave it blank if Jainam permits. If the form requires it, ask Jainam for its supported configuration before continuing. This MCP does not receive postbacks. Do not enter a dummy URL or assume the login callback above is a postback endpoint.

**APP Code is not your trading client ID.** Use the APP Code and Secret Key from the same app. Keep them private; do not paste them into Claude, GitHub, or this README. The Redirect URL above is a public setup value, not a secret; `127.0.0.1` means your own computer.

### Step 3 — Download and open Connect

Choose **only your computer's instructions** below. Open Terminal on Mac or PowerShell on Windows, then paste the matching commands. Press Enter to run them.

<details open>
<summary><strong>Mac — first installation</strong></summary>

```sh
cd ~
git clone --branch v0.1.5 https://github.com/malkarisreenivasulu/jainam-mcp-agent.git
cd jainam-mcp-agent
open Connect.command
```

</details>

<details>
<summary><strong>Windows — first installation</strong></summary>

```powershell
cd $HOME
git clone --branch v0.1.5 https://github.com/malkarisreenivasulu/jainam-mcp-agent.git
cd jainam-mcp-agent
.\Connect.bat
```

</details>

<details>
<summary><strong>Already downloaded it? Update the existing folder instead</strong></summary>

Do not run `git clone` again. From Terminal/PowerShell:

```sh
cd ~/jainam-mcp-agent
git fetch origin --tags
git switch --detach v0.1.5
```

Then double-click **Connect.command** on Mac or **Connect.bat** on Windows inside the project folder. If you saved the folder somewhere else, open that folder instead. A detached-HEAD notice is normal when using a fixed release tag.

</details>

The Connect launcher prepares the project automatically. The first run may take a few minutes and show installation messages. You do not need to run pip commands or activate a Python environment yourself.

### Step 4 — Enter your app details and finish browser login

1. At **APP Code (hidden)**, paste your own APP Code and press Enter.
2. At **Secret Key (hidden)**, paste that app's Secret Key and press Enter. **You will not see characters while entering these values; that is normal.**
3. Jainam opens in your browser. Finish its login/MFA on this same computer within three minutes. Keep the Connect window open.
4. Return to the Connect window. Wait for:

   ```text
   Connected. You can now ask your MCP client for your Jainam account data.
   ```

**That is the success message.** Connect checks a read-only account request before displaying it. `[Process completed]` afterward is normal: the sign-in window has finished its job. You can close it.

Do not paste the browser's callback address into Terminal. The app receives it automatically. Your app details are remembered in a private **plaintext file on your computer, outside this project**; authorization codes are never saved. Do not upload the private app/session files.

### Step 5 — Generate Claude's configuration automatically

Open a **new** Terminal/PowerShell window. Choose your operating system and run:

**Mac:**

```sh
cd ~/jainam-mcp-agent
.venv/bin/python -m jainam_mcp client-config claude
```

**Windows PowerShell:**

```powershell
cd "$HOME\jainam-mcp-agent"
.\.venv\Scripts\python.exe -m jainam_mcp client-config claude
```

If your project is somewhere else, open Terminal/PowerShell in that folder and run the second line. You will see configuration text starting with `{` and containing `mcpServers` and `jainam`. This text already contains **your correct Python path**. Leave it visible for the next step.

**Do not copy `/absolute/path/...` from an example.** You do not need to type your username or guess a path. The output above supplies the right one. This is a Python MCP; do not replace its generated command with `npx`.

### Step 6 — Add Jainam to Claude once

1. Open **Claude Desktop → Settings → Developer → Edit Config**. Menu names can vary by version.
2. If the configuration file is **empty**, paste the entire generated configuration from Step 5.
3. If it **already has MCP servers**, add only the generated **`jainam` entry inside the existing `mcpServers` object**. Keep your other servers and application preferences. Do not paste a second whole JSON document or create a second `mcpServers` section.
4. Save the file. Entries need commas between them, with no comma after the last entry.
5. **Fully quit Claude Desktop and reopen it once.** On Mac, use **Claude → Quit**; closing only the window may leave it running.

You do **not** put APP Code, Secret Key, authorization code or session into Claude's configuration. The generated Jainam entry contains only its launch command and arguments. [See the detailed Claude guide](docs/CLAUDE.md) if you already have a large configuration file.

### Step 7 — Ask your first question

Start a new conversation in Claude and type:

> Use Jainam to show my available funds.

Approve the Jainam tool if Claude asks. Then try:

> Show my Jainam holdings in a simple table.

Claude must have the Jainam tools available and successfully read the account before it can answer with your data. If the tools are missing, check Step 5's generated path and Step 6's restart; do not reinstall everything.

## What do I do tomorrow?

**Open Claude and ask your question.** You do not repeat the installation or app setup.

- A valid session is reused.
- If the local MCP needs a new session, finish the browser login it opens, then ask again. Your app keys do not need to be entered again.
- If sign-in fails, open **Connect.command** / **Connect.bat** to retry. It does not keep opening browser tabs automatically.
- Normal session renewal does not require editing Claude's configuration or restarting the MCP.

## Stuck? Match the message below

| What you see | What to do |
|---|---|
| `destination path ... already exists` | Use Step 3's **Already downloaded it?** instructions. Do not clone again. |
| `python: command not found` on Mac | Use the exact `.venv/bin/python` command in Step 5 after Connect finishes. |
| No characters at APP Code/Secret Key | Hidden input is intentional. Paste the value and press Enter. |
| `Connected` followed by `[Process completed]` | Sign-in succeeded. Continue with Step 5; Claude starts the server itself. |
| No Jainam tools in Claude | Use the generated path, save valid JSON, fully quit/reopen Claude. |
| `AUTH_*` or `SESSION_NOT_VERIFIED` | Login is not complete. [Check the error guide](docs/TROUBLESHOOTING.md); share only its safe diagnostic, never keys or callback URLs. |

Using **VS Code**? Follow its [client guide](docs/VSCODE.md) after Step 4. **ChatGPT** has [separate tunnel/workspace requirements](docs/CHATGPT.md); the Claude JSON above does not connect ChatGPT.

Advanced options, custom install locations and external callbacks: [full guide](docs/GETTING_STARTED.md). To replace rotated app keys, run Connect with `--replace-app`; external callbacks use `--manual` and do not support automatic loopback renewal.

## What can this project read?

| You can ask | What the server does |
|---|---|
| “Show my funds and holdings” | Reads your account data |
| “Summarize my current positions” | Reads positions; does not close them |
| “Show my existing orders and trades” | Reads broker books and order history |
| “Find GOLD contracts on MCX” | Searches the broker's current contract master |
| “Fetch historical candles for this token” | Reads historical data, subject to broker availability |

**No order placement, modification, cancellation, square-off, autonomous trading, or generic HTTP tool.** No subscription, multicast server, Redis, Docker, or KuberaOS installation is needed. Live streaming and live quotes are not exposed. Five reusable MCP prompt templates help clients structure analysis.

## Copy a prompt. See your portfolio clearly.

After connecting your client, try:

> **Sector-wise donut:** “Show my holdings by sector as a donut chart, weighted by current market value. Use only sourced sector classifications, keep unmapped stocks as Unclassified, and show INR values, percentages and data coverage.”

> **Investment-wise pie:** “Show my stock-wise invested capital as a pie chart using acquisition cost. Show the top 8 stocks plus Other, total invested capital and an underlying table. Do not substitute market value for invested cost.”

> **Holdings dashboard:** “Create KPI cards for invested capital, market value and unrealized P&L, a stock-allocation donut, signed P&L bars and a holdings table. Label missing data and snapshot time.”

> **Positions:** “Show my existing positions as a signed unrealized-P&L bar chart. Separate realized and unrealized P&L, and verify contract units before calculating futures or options exposure.”

> **Trades:** “Show traded turnover by symbol as a donut and fill counts by hour as bars. Count fills, orders and completed round trips separately. Do not treat turnover as profit.”

**[Open the full visual prompt library →](docs/EXAMPLE_PROMPTS.md)** for copy-and-paste prompts, sector/cost/market-value comparisons, treemaps, reconciliation and private HTML reports.

The MCP server reads data; your AI client renders charts if supported. Sector charts require returned classifications or a sourced mapping you provide. Charts cannot establish missing realized P&L, charges or contract multipliers.

## Verification before you use real account data

See the [validation report](docs/VALIDATION.md) for exactly what is tested.
The suite covers all ten tools over MCP with synthetic broker responses, and CI
installs the built wheel in fresh environments across Windows, macOS and Linux.
These checks do **not** prove real Jainam login, API entitlement, production data
schemas or a particular client's chart rendering. Run `doctor --online` and verify
a small real read with your own account after setup. A broker HTML error page is
reported as an error, never a successful empty instrument search.

## Privacy and limitations

Credentials stay in your local environment or private credentials file. This repository contains no maintainer account credentials. The server never returns the configured session token, redacts common identifiers and secret fields, and does not print raw broker errors. Account balances, holdings and trades **are sent to your chosen AI client when you request them**; they may be processed by that client's provider. Review its privacy settings. Local execution does not mean all data stays offline.

You need your own Jainam account, developer application, API entitlement and valid session. Broker access, rate limits and data availability are controlled by Jainam; availability to every account is not guaranteed. This release uses **ProTrade Open API v2**, not XTS/JLite APIs. It is not a public hosted service, financial adviser, or a guarantee of price/data accuracy.

## Documentation

- [Beginner setup and sign-in](docs/GETTING_STARTED.md)
- [Claude Desktop](docs/CLAUDE.md) · [VS Code](docs/VSCODE.md) · [ChatGPT](docs/CHATGPT.md)
- [Visual example prompts](docs/EXAMPLE_PROMPTS.md)
- [Tools and response formats](docs/TOOLS.md)
- [Testing and validation limits](docs/VALIDATION.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Security policy](SECURITY.md) · [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md)

## Upgrade from v0.1.0

The repository/package is now **jainam-mcp-agent**. The `jainam_mcp` Python module,
legacy `jainam-mcp` command and existing `~/.config/jainam-mcp/credentials.json`
location remain compatible. The new `jainam-mcp-agent` command is an alias for the
same CLI. Existing client JSON does not need a module or credentials-path change.
When replacing an installed v0.1.0 package in the same environment, uninstall
`jainam-mcp` first, then install this renamed package to avoid overlapping package
files. Keep your private credentials file. New clone folders use
`jainam-mcp-agent`; generate client JSON with that install's Python. Old GitHub repository URLs redirect, but update remotes to the new URL.

## Development

```sh
python -m pip install -e '.[dev]'
python -m pytest
python -m ruff check .
python -m build
python scripts/scan_secrets.py
```

Tests use synthetic credentials and mocked HTTP. They do not log into a real account or place orders. See [Contributing](CONTRIBUTING.md) for the release checklist and tested boundaries.

MIT licensed. Jainam and ProTrade are trademarks of their respective owners. No affiliation or endorsement is implied. Not investment advice.
