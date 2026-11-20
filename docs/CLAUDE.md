# Connect Jainam to Claude Desktop

You do this **once** after Jainam Connect says **Connected**. There are two separate steps: sign in to Jainam, then tell Claude how to launch the local MCP server.

## 1. Sign in to Jainam

Open **Connect.command** on macOS or **Connect.bat** on Windows. On first use, enter your own APP Code and Secret Key and finish browser login. Wait for:

```text
Connected. You can now ask your MCP client for your Jainam account data.
```

`[Process completed]` afterward is normal: the sign-in launcher finished. Claude will start the MCP server itself. You do not need to leave Connect running.

If you have not downloaded/installed the project, start with [Getting started](GETTING_STARTED.md).

## 2. Generate your correct Claude configuration

**macOS — open Terminal and run:**

```sh
cd ~/jainam-mcp-agent
.venv/bin/python -m jainam_mcp client-config claude
```

**Windows — open PowerShell and run:**

```powershell
cd "$HOME\jainam-mcp-agent"
.\.venv\Scripts\python.exe -m jainam_mcp client-config claude
```

If you saved the project somewhere else, open Terminal/PowerShell in that project folder and run the second line. The command prints valid JSON with **your actual absolute Python path**. No virtualenv activation, manual username replacement, or secret values are needed.

**Do not paste `/absolute/path/...` into Claude.** It is a placeholder in the repository's example file, not a working path. Use the generated output above. Do not use `python`, `python3`, or `npx` in place of the generated Jainam command: the generated path points to the environment where Jainam is installed. This Python MCP is not published as an npm package.

## 3. Add Jainam to Claude's configuration

1. In Claude Desktop, open **Settings → Developer → Edit Config**. Menus may vary by client version.
2. If the file is empty, paste the entire generated JSON.
3. If the file already has other servers, copy **only the generated `jainam` entry** into the existing `mcpServers` object. Keep other servers and their settings. Use one `mcpServers` object; do not paste a second complete JSON document into the file.
4. Keep existing application preferences outside `mcpServers` intact. You do not need to copy preferences, account IDs, paths, or another person's entire configuration from an example.
5. Check commas: separate server entries with a comma, but do not put a trailing comma after the last entry. Save the file as valid JSON.
6. Fully quit Claude Desktop, then reopen it. On macOS use **Claude → Quit**; closing a window alone may leave the application running.

The usual file locations are:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Do not put Jainam APP Code, Secret Key, authorization code or user session in this JSON. They stay in the separate private local settings. Do not copy unrelated service tokens from an example; rotate any token accidentally shared publicly.

## 4. Ask your first question

Start a new Claude conversation and ask:

> Use jainam_status to check my connection, then use jainam_funds to show my available funds.

Approve the tool if Claude asks. `credentials_configured: true` confirms a saved session exists; only a successful funds read confirms current broker access. Then try:

> Show my Jainam holdings in a table.

If no Jainam tools appear, revisit the generated Python path and the client restart. Check [Troubleshooting](TROUBLESHOOTING.md). Reinstalling or repeatedly cloning the project is not the next step for a missing tool.

## Everyday use

Open Claude and ask for Jainam data. When a local read detects an expired/missing session and app details are remembered, finish the browser sign-in and ask again. The running server reloads renewed sessions; you do not edit the Claude config or restart it for normal session renewal. If browser renewal fails, open Connect to retry. External callbacks require `connect --manual`.

Claude receives the account data you request. Review its data-use settings. No order placement, modification, cancellation or square-off tools are provided.

For a custom private session location, generate configuration with `--config` before `client-config`; see the [advanced setup](GETTING_STARTED.md#advanced-options).

Reference: [official MCP local-server guide](https://modelcontextprotocol.io/docs/develop/connect-local-servers). The protocol and generated JSON are tested; actual Claude UI/tool access depends on your client and account.
