# Inventory

## Required .env Keys

- GITHUB_PERSONAL_ACCESS_TOKEN
- OPENROUTER_API_KEY
- REPO_PATH (defaults to `$HOME/repos`)
- NERD_FONT (defaults to `Hack Nerd Font Mono`)

## Acceptance Criteria

**WSL/Ubuntu**

- zsh is installed and set to the default shell
- ohmyzsh is installed and all the basic plugins are added (git, docker, python)
- mise is installed and the activation command is added to the zshrc
- gh is installed and auth login complete with non-enterprise, ssh key, and PAT
- ssh ed2559 key is generated with no passphrase
- `git@github.com:YIC-Triumph/zshyzsh`` is cloned into `~/.config/`
- zshrc includes `export ZSH_CUSTOM=$HOME/.config/zshyzsh`
- latest neovim is installed from packaged distributable on website (not apt) >v0.11
- lazyvim is installed and placed in `~/.config/nvim`
- mise used to install several system-wide tools (python 3.12.9, uv@latest, nodejs@latest, pipx@latest)
- gptme is installed using `pipx install 'gptme[all]'`
- gptme-rag is installed using `pipx install gptme-rag`
- sst/opencode is installed
- claude-code is installed with `npm i -g @anthropic-ai/claude-code`
- claude-code is authenticated with a long running token
- claude-flow is installed with `npm i -g claude-flow@latest`
- docker can bring up the hello world container
- docker compose v2 is installed and working
- A symlink to `cursor` installed in windows is placed in `~/.local/bin`
- A symlink to `vscode` installed in windows is placed in `~/.local/bin`
- mise config is set to `experimental`

**Windows**

- Hack Nerd Font Mono downloaded and is installed in Windows
- Alacritty terminal is downloaded and installed in Windows
- Alacritty is configured to start in wsl as the Windows user (not admin)
- Docker Desktop is downloaded and installed
