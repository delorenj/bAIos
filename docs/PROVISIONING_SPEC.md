# Provision Specs

## Install List

**Install in WSL**

- **Neovim**
- **Vim**
- **Git**
- **Zsh**
- Oh-my-zsh
  - 🔧 **Installation**: `sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"`
- **GH cli**
- **Cursor** symlink
- **Claude Code CLI**
- **VS Code** symlink
- **GitHub CLI (gh)**
- **fzf**
- **mise** (version manager)
  - ⚡ **Install**: `curl https://mise.run | sh`

**Install in Windows**

- **Docker** Desktop
- **Hack Nerd Font Mono (font)**
- Alacritty

## Configuration

### Zsh

1. Add `~/.local/bin` to your `$PATH`.
2. Ensure `mise` is activated in your shell.

### gh

1. Login to GitHub CLI with `gh auth login` using the `$GITHUB_PERSONAL_ACCESS_TOKEN` environment variable which should be set in your `.env` file. If not, ask for it
2. Generate a new SSH key with 'gh ssh-key add ~/.ssh/id_ed25519.pub --title "`whoami`-wsl'. This will add the SSH key to your GitHub account.

### Python

1. Install Python 3.12 using `mise install python@3.12`.
2. Set the system Python version to 3.12 with `mise use python@3.12 --system`.

### Node

1. Install Node using `mise install nodejs@latest`.
2. Set the system Node version with `mise use nodejs@latest --system`.

### PNPM

Latest, same as above `mise use pnpm@latest --system`

### UV

Latest, same as above `mise use uv@latest --system`

### GPTme

1. Install GPTme using `pipx install 'gptme['all'']'`.
2. Link the zshyzsh configuration file with `ln -s ~/.config/zshyzsh/gptme/config.toml ~/.config/gptme/config.toml`.

### Claude Code CLI

1. npm i -g @anthropic-ai/claude-code
2. Authenticate with your MAX plan - NOT the API key method.
3. Set the environment variable `CLAUDE_CODE_API_KEY` in your `~/.config/zshyzsh/secrets.zsh`
4. Add the Triumph mcp config by `claude mcp add-json triumph-tools \`cat ~/.config/zshyzsh/mcp/triumph-tools.json\``

### Gemini CLI

1. Install Gemini CLI using `npm i -g @google/gemini-cli@latest`.

### Lazyvim

1.

### Oh-my-zsh

1. Clone `YIC-Triumph/zshyzsh` to `~/.config/`
2. Add `export ZSH_CUSTOM=~/.config/zshyzsh` to your `~/.zshrc`.

### Zellij

1. Run `~/.config/zshyzsh/scripts/install-zellij.sh`
2. Link zellij config with `mv ~/.config/zellij ~/.config/zellij.bk && ln -s ~/.config/zshyzsh/zellij ~/.config/zellij`.

### Alacritty

1. Since alacritty is installed in Windows, you need to copy the config file from `~/.config/zshyzsh/alacritty/alacritty.yml` to your Windows Alacritty config directory, typically located at `C:\Users\<YourUsername>\.config\alacritty\alacritty.yml`.
