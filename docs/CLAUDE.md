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

**Use the installed Claude Desktop app for these steps.** Open the app itself, not a Claude website tab.

**6A. Open Claude's settings file**

1. On **Mac**, click **Claude** in the top menu bar, then **Settings**. On **Windows**, open Claude's application menu and choose **Settings**. Exact menu placement may vary by version.
2. Select **Developer**, then **Edit Config**. You are looking for **`claude_desktop_config.json`**.
3. If a folder opens instead of an editor, right-click that file and open it in a plain-text editor, such as VS Code, Notepad on Windows, or TextEdit on Mac. Do not use Word or a rich-text document. If using TextEdit, choose **Format → Make Plain Text** if that option appears.
4. Before editing an existing file, save a copy as a backup. Keep that backup private because other servers may have credentials in it.

**Can't find the file?** These are the usual locations:

- Mac: in Finder choose **Go → Go to Folder**, paste `~/Library/Application Support/Claude/`, and press Enter.
- Windows: press **Windows+R**, paste `%APPDATA%\Claude`, and press Enter.

Look for `claude_desktop_config.json` in that folder. If it is not there, return to Claude's **Developer → Edit Config** to create/open it. Do not create a `.txt` file with a similar name. If your Claude version does not offer local MCP/Developer settings, check that version's supported configuration before continuing.

**6B. Copy the generated configuration from section 2**

You can select the generated text in Terminal, or copy it directly to your clipboard with the matching command below, from the project folder:

**Mac:**

```sh
.venv/bin/python -m jainam_mcp client-config claude | pbcopy
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m jainam_mcp client-config claude | Set-Clipboard
```

These commands copy configuration, not passwords. It is normal for them to print nothing. Paste with **Command+V** on Mac or **Ctrl+V** on Windows.

**6C. Choose the situation that matches your file**

| Your configuration file currently contains… | What to paste |
|---|---|
| Nothing, or only `{}` | Select all and paste the **entire generated configuration**. |
| Other settings, but no `mcpServers` | Keep those settings. Add the generated **`"mcpServers": { ... }` property** inside the file's outer `{ }`. Separate it from the other properties with a comma. Do not paste another whole document around them. |
| An existing `mcpServers` object with other servers | Keep the existing object. Copy only **`"jainam": { ... }`** from the generated text and add it alongside the other server entries. Add a comma between entries. |
| A `jainam` entry already inside `mcpServers` | Replace **only that existing Jainam entry** with the newly generated entry. Do not add a duplicate. |

For an existing configuration, paste the generated output into a temporary plain-text editor tab so you can select the required part. The `...` above means the actual contents from your generated output—**do not type three dots into JSON**.

Keep your other servers and application preferences. Use one outer JSON document and one `mcpServers` object. There must be **commas between entries**, **no comma after the last entry**, and **no comments**. Your generated Python path is already correct; do not replace it with `/absolute/path/...`, `python`, or `npx`.

**6D. Save and restart Claude once**

1. Save as **`claude_desktop_config.json`**, keeping the `.json` extension.
2. Fully quit Claude. On Mac use **Claude → Quit** or **Command+Q**. On Windows use the application's **Quit/Exit** action, including the tray icon if Claude is still running there. Closing only the window may leave it running.
3. Reopen Claude Desktop and start a new conversation.
4. Check that Jainam is listed in the local MCP/developer settings and that its tools are available to the conversation. Tool controls can vary by Claude version. Continue to section 4 and approve the Jainam read tool if requested.

**Never put APP Code, Secret Key, authorization code or session in Claude's JSON.** Do not copy someone else's complete configuration or unrelated tokens. This step registers the local program; your private Jainam login details are already saved separately.

### Check JSON syntax locally if Claude reports a configuration error

These commands validate JSON syntax without printing the configuration or any existing server secrets. They do not check that the Python executable exists or that Claude can launch it.

**Mac:**

```sh
.venv/bin/python -m json.tool "$HOME/Library/Application Support/Claude/claude_desktop_config.json" > /dev/null
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m json.tool "$env:APPDATA\Claude\claude_desktop_config.json" > $null
```

No output with a successful command means the JSON parses. An error reports its line/column; check commas, quotes and braces there. Do not paste the full configuration into a public issue or chat.

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
