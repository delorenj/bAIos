# Root Agent

This is the Root Agent for the bAIos provisioning system. It is responsible for orchestrating the execution of the specialized sub-agents.

## Usage

The Root Agent takes a natural language query as input and delegates the task to the appropriate sub-agent.

```bash
python -m agents.root_agent.agent "install python"
```

### Supported Queries

The Root Agent currently supports the following keywords in queries:

*   `python`: Installs Python.
*   `node`: Installs Node.js.
*   `git`: Installs Git.
*   `zsh`: Installs Zsh.
*   `wsl`: Installs WSL.
*   `ubuntu`: Installs Ubuntu.
*   `claude`: Installs Claude Code.
*   `gptme`: Installs GPTme.
