# WSL Environment Provisioning Specification

## Overview
This specification defines the complete setup requirements for a WSL development environment optimized for AI development, system administration, and modern DevOps workflows.

## System Requirements
- WSL2 with Ubuntu 22.04 LTS
- Windows Terminal with proper configuration
- Git with SSH key setup
- Modern shell environment (zsh + oh-my-zsh)

## Core Tools Installation

### Package Management
- [ ] Update apt repositories: `sudo apt update && sudo apt upgrade -y`
- [ ] Install essential packages: `sudo apt install -y curl wget git build-essential`
- [ ] Install zsh: `sudo apt install -y zsh`
- [ ] Install oh-my-zsh: `sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"`

### Development Environment
- [ ] Install mise for version management: `curl https://mise.run | sh`
- [ ] Configure mise in shell profile
- [ ] Install Node.js via mise: `mise install node@20`
- [ ] Install Python via mise: `mise install python@3.11`
- [ ] Install uv for Python package management: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Install pnpm: `npm install -g pnpm`
- [ ] Install pipx: `python -m pip install --user pipx`

### AI Development Tools
- [ ] Install Claude Code: `pipx install claude-code`
- [ ] Install gptme: `pipx install gptme`
- [ ] Install Gemini CLI: `npm install -g @google-ai/gemini-cli`
- [ ] Setup OpenRouter configuration

### Shell Configuration
- [ ] Setup ~/.local/bin in PATH
- [ ] Configure zsh with custom aliases
- [ ] Setup shell completions for tools
- [ ] Create symlinks for config files to ~/.config/

### Security & Authentication
- [ ] Configure GitHub CLI: `gh auth login`
- [ ] Setup SSH keys for GitHub
- [ ] Configure Claude Code with API keys
- [ ] Setup Vault client for secrets management

### System Utilities
- [ ] Install docker.io: `sudo apt install -y docker.io`
- [ ] Add user to docker group: `sudo usermod -aG docker $USER`
- [ ] Install docker-compose: `sudo apt install -y docker-compose`
- [ ] Install htop, tree, jq: `sudo apt install -y htop tree jq`
- [ ] Install ripgrep and fd: `sudo apt install -y ripgrep fd-find`

## Configuration Files
- [ ] ~/.zshrc with proper PATH and aliases
- [ ] ~/.config/mise/config.toml for tool versions
- [ ] ~/.config/git/config for Git settings
- [ ] ~/.ssh/config for SSH connections
- [ ] ~/.docker/config.json for Docker registries

## Verification Steps
- [ ] Verify all tools are in PATH and working
- [ ] Test GitHub authentication
- [ ] Test Claude Code functionality
- [ ] Verify Docker installation
- [ ] Check shell configuration and aliases
- [ ] Validate mise tool management

## Environment Variables
- [ ] OPENROUTER_API_KEY configured
- [ ] GITHUB_TOKEN configured
- [ ] ANTHROPIC_API_KEY configured
- [ ] PATH includes ~/.local/bin
- [ ] MISE_DATA_DIR properly set

## Quality Checks
- [ ] All binaries executable and in PATH
- [ ] Shell starts without errors
- [ ] Tool versions match specifications
- [ ] Authentication working for all services
- [ ] Configuration files properly linked