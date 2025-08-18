# WSL Development Environment Specification

## Overview

This document defines the declarative specification for a complete WSL-based development environment. It describes the desired end state rather than installation procedures.

## Required Environment Variables

```bash
# ~/.config/zshyzsh/secrets.zsh
GITHUB_PERSONAL_ACCESS_TOKEN="<token>"
OPENROUTER_API_KEY="<key>"
CLAUDE_CODE_API_KEY="<key>"

# ~/.config/zshyzsh/config.zsh  
REPO_PATH="$HOME/repos"
NERD_FONT="Hack Nerd Font Mono"
```

## System Architecture

### Host OS: Windows 11/10
- **WSL 2** with Ubuntu 22.04+ distribution
- **Docker Desktop** integrated with WSL 2
- **Alacritty** terminal configured for WSL access
- **Hack Nerd Font Mono** system font

### WSL Environment: Ubuntu

#### Shell Configuration
- **Default Shell**: `zsh` 
- **Framework**: oh-my-zsh with plugins: `git`, `docker`, `python`
- **Custom Config**: `~/.config/zshyzsh` (from `YIC-Triumph/zshyzsh`)
- **PATH Extension**: `~/.local/bin` included

#### Version Management
- **Tool**: `mise` (experimental mode enabled)
- **Activation**: Integrated in `~/.zshrc`

#### Development Languages & Runtimes
```toml
# ~/.config/mise/config.toml
[tools]
python = "3.12.9"
nodejs = "latest" 
pnpm = "latest"
uv = "latest"
pipx = "latest"
```

#### Code Editors & Tools
- **Primary**: Neovim ≥0.11.0 with LazyVim config in `~/.config/nvim`
- **Secondary**: VS Code (symlinked to `~/.local/bin/vscode`)
- **AI-Enhanced**: Cursor (symlinked to `~/.local/bin/cursor`)

#### Version Control
- **Git**: System package with GitHub SSH authentication
- **GitHub CLI**: Authenticated with SSH key and PAT
- **SSH Key**: ed25519 without passphrase in `~/.ssh/id_ed25519`

#### Container Platform
- **Docker Engine**: Accessible from WSL
- **Docker Compose**: v2 
- **Validation**: `docker run hello-world` succeeds

#### AI Development Tools
- **claude-code**: Global npm package (`@anthropic-ai/claude-code`)
  - Authentication: Long-running token (not API key method)
  - MCP Config: Triumph tools integration
- **claude-flow**: Global npm package (`claude-flow@latest`)
- **gptme**: Installed via pipx with `[all]` extras
  - Config: `~/.config/gptme/config.toml` → `~/.config/zshyzsh/gptme/config.toml`
- **gptme-rag**: Additional pipx package
- **Gemini CLI**: Global npm package (`@google/gemini-cli@latest`)

#### Terminal Multiplexer
- **Zellij**: Installed via custom script
- **Config**: `~/.config/zellij` → `~/.config/zshyzsh/zellij`

#### System Utilities
- **Text Processing**: grep, fzf, jq
- **Network**: wget, ping
- **Archives**: unzip, tar
- **Development**: make, glow (markdown viewer)
- **Monitoring**: top

## Configuration State

### Shell Environment (`~/.zshrc`)
```bash
export ZSH_CUSTOM=$HOME/.config/zshyzsh
export PATH=$HOME/.local/bin:$PATH
# mise activation
eval "$(mise activate zsh)"
```

### mise Configuration
```toml
# ~/.config/mise/config.toml
experimental = true
```

### Symlinks Required
```bash
~/.local/bin/cursor → /mnt/c/Users/<username>/AppData/Local/Programs/cursor/Cursor.exe
~/.local/bin/vscode → /mnt/c/Users/<username>/AppData/Local/Programs/Microsoft\ VS\ Code/Code.exe
~/.config/gptme/config.toml → ~/.config/zshyzsh/gptme/config.toml  
~/.config/zellij → ~/.config/zshyzsh/zellij
```

### GitHub Authentication State
- SSH key `~/.ssh/id_ed25519.pub` added to GitHub account
- GitHub CLI authenticated with token
- SSH agent configured for automatic key loading

## Windows Host Requirements

### Applications Installed
- **Docker Desktop**: WSL 2 backend enabled
- **Alacritty**: Configured to launch WSL as primary shell
- **Hack Nerd Font Mono**: System font installation

### Alacritty Configuration
```yaml
# %APPDATA%\alacritty\alacritty.yml
shell:
  program: wsl.exe
  args: ["~"]
font:
  normal:
    family: "Hack Nerd Font Mono"
```

## Acceptance Criteria

### Core System Validation
- [ ] `zsh --version` shows zsh as default shell
- [ ] `oh-my-zsh` plugins active: git, docker, python
- [ ] `mise --version` available and experimental mode enabled
- [ ] `gh auth status` shows authenticated state
- [ ] `ssh -T git@github.com` authenticates successfully

### Development Environment
- [ ] `nvim --version` shows ≥0.11.0
- [ ] LazyVim configuration loads without errors
- [ ] `python --version` shows 3.12.9 via mise
- [ ] `node --version` shows latest via mise
- [ ] `pnpm --version` shows latest via mise
- [ ] `uv --version` shows latest via mise

### AI Tools
- [ ] `claude --version` shows claude-code installation
- [ ] Claude Code authentication validates
- [ ] `gptme --version` shows working installation
- [ ] `gemini --version` shows working installation
- [ ] GPTme config properly linked

### Container Platform
- [ ] `docker run hello-world` executes successfully
- [ ] `docker compose version` shows v2
- [ ] Docker Desktop integration with WSL confirmed

### Configuration Integrity
- [ ] `$ZSH_CUSTOM` points to `~/.config/zshyzsh`
- [ ] Custom oh-my-zsh configuration loads
- [ ] All symlinks resolve correctly
- [ ] Environment variables available in new shell sessions

## Documentation References

### Installation Guides
- [WSL Installation](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Oh My Zsh](https://ohmyz.sh/)
- [mise Documentation](https://mise.jdx.dev/getting-started.html)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [Neovim Installation](https://github.com/neovim/neovim/blob/master/INSTALL.md)
- [LazyVim Setup](https://www.lazyvim.org/installation)
- [Docker on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code/overview)
- [gptme Documentation](https://gptme.org/docs/)

### Font Resources
- [Hack Nerd Font Downloads](https://github.com/ryanoasis/nerd-fonts/releases)
- [Alacritty Configuration](https://github.com/alacritty/alacritty/blob/master/INSTALL.md)

## Quality Assurance

Each component must satisfy:
- ✅ **Installation Success**: Tool accessible via command line
- ✅ **Version Requirements**: Meets specified minimum versions  
- ✅ **Functionality**: Basic operations complete successfully
- ✅ **Configuration**: Settings properly applied and persistent
- ✅ **Integration**: Interoperates correctly with other components

---

**Environment Scope**: WSL 2 Ubuntu + Windows Host  
**Target Users**: AI-assisted development workflows  
**Estimated Setup Time**: 2-4 hours depending on internet speed  
**Maintenance**: Self-updating tools via mise and package managers