# AI Dev Workflow Auto-Provision Service

## Initial Prompt

I need an internal web app for my company Triumph that will provision their Windows/WSL machine in a very precise opinionated way. The team is quite junior so it needs to be as automated as possible, stepping them through the steps and ensuring they happen in a valid order as prescribed by the dependency tree of the final machine state.

## Assumptions

- Clients will be running windows
- WSL distro is `Ubuntu`
- WSL home path is accessible from windows as `\\wsl.localhost\Ubuntu\home\<username>` (from here on out, referred to as `$HOME`)
- Main code/repository path is `$HOME/repos`
- WSL will be completely fresh so DON’T assume even basic apps will be installed yet (i.e. gh, curl, etc)

## Requirements

- Should be build using this stack: [GitHub - fastapi/full-stack-fastapi-template: Full stack, modern web application template. Using FastAPI, React, SQLModel, PostgreSQL, Docker, GitHub Actions, automatic HTTPS and more.](https://github.com/fastapi/full-stack-fastapi-template)
- Architecture should be designed knowing mac support will eventually be added (i.e. perhaps building the first provisioner on a strategy pattern that allows us to implement platforms with an extracted common interface)
- The frontend will display a checklist of installation steps, ordered by dependency.
- A downloadable agent, installed on the client machine, will execute the provisioning tasks.
- The web UI will communicate with the local agent to initiate these tasks.
- The agent will be composed of specialized sub-agents, each designed for a specific task (e.g., installing a particular tool).
- The agent can be pre-configured with a company-wide token, so junior developers do not need to manage their own.
