# Jainam MCP Agent

[![CI](https://github.com/malkarisreenivasulu/jainam-mcp-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/malkarisreenivasulu/jainam-mcp-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Connect Claude Desktop, VS Code Copilot, or a supported ChatGPT tunnel to **your own Jainam account**, using a local, read-only Model Context Protocol server.

**Developed by Sreenivasulu Malkari.** Built on [Jainam API Python](https://github.com/malkarisreenivasulu/jainam-api-python) and the official MCP Python SDK. Independent community software, not an official Jainam product.

| You can ask | What the server does |
|---|---|
| “Show my funds and holdings” | Reads your account data |
| “Summarize my current positions” | Reads positions; does not close them |
| “Show my existing orders and trades” | Reads broker books and order history |
| “Find GOLD contracts on MCX” | Searches the broker's current contract master |
| “Fetch historical candles for this token” | Reads historical data, subject to broker availability |

**No order placement, modification, cancellation, square-off, autonomous trading, or generic HTTP tool.** No subscription, multicast server, Redis, Docker, or KuberaOS installation is needed. Live streaming and live quotes are not exposed. Five reusable MCP prompt templates help clients structure analysis.

## Start here

1. Install Python 3.11–3.14 and Git once. Clone/download this repository, or update your existing clone to v0.1.5. **Do not clone again into a folder that already exists.**
2. In [Jainam Developers](https://protrade.jainam.in/developers), create/edit your own app and register **Redirect URL: `http://127.0.0.1:8765/callback`**. Save/Update. Postback is separate: leave blank if permitted; if mandatory, confirm the supported configuration with Jainam. This MCP has no postback receiver.
3. On macOS, double-click **Connect.command**. On Windows, double-click **Connect.bat**. The launcher prepares the local Python environment and installs/updates this checkout when necessary. Enter APP Code and Secret Key once, then finish Jainam sign-in in the browser.
4. Wait for **Connected**. The command verifies account access before displaying success. Connect your AI client using its guide below, then ask for holdings or funds.

App details are remembered **only on your computer**, in a private plaintext file outside the repository. Sessions are separate. Do not upload either file. Subsequent connections reuse a valid session. When a local MCP read discovers a missing/expired session, saved app details let it open browser login without terminal prompts; finish login and ask again. The running MCP reloads the saved session automatically. If automatic sign-in fails, run Connect again; it does not keep opening browser tabs.

Prefer Terminal? Use the **same command every time**:

```sh
python3 scripts/connect.py
```

On Windows use `py -3 scripts\connect.py`. Existing virtualenv users can run `jainam-mcp connect` directly. Replace a rotated APP Code/Secret Key using `python3 scripts/connect.py --replace-app`. External callbacks use `--manual` and require manual callback input; automatic renewal is for local loopback browser login on the same computer. The developer portal setting must be registered manually; the MCP cannot update it.

[Full step-by-step guide](docs/GETTING_STARTED.md) · [Troubleshooting](docs/TROUBLESHOOTING.md)

A user-reported v0.1.5 login reached verified Connected. Each user still needs their own API entitlement and successful login; this does not establish universal access. If setup reports an unsupported response, share only its safe diagnostic, never keys or callback URLs.

### Connect Claude Desktop once

After Connect says **Connected**, generate the configuration from your project folder:

**macOS:**

```sh
.venv/bin/python -m jainam_mcp client-config claude
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m jainam_mcp client-config claude
```

This prints **your real absolute Python path**. In Claude Desktop open **Settings → Developer → Edit Config**. If the file is empty, paste the generated JSON. If it already has servers, add only the generated `jainam` entry inside its existing `mcpServers` object. Keep other servers and preferences. Save, fully quit Claude and reopen it once.

**Never paste `/absolute/path/...` from an example as your command. Never paste APP Code, Secret Key or session into the client JSON.** This is a Python MCP, not an npm package launched with `npx`.

Then ask: **“Use Jainam to show my available funds.”** `[Process completed]` in the sign-in window is normal; Claude launches the server itself.

[Claude walkthrough](docs/CLAUDE.md) · [VS Code](docs/VSCODE.md) · [ChatGPT's separate requirements](docs/CHATGPT.md)

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
