# bAIos CLI

🤖 **AI-powered workspace management and automation CLI**

bAIos is a modern command-line interface that brings AI-powered automation and workspace management to your development environment. Built with Python and Typer, it provides an intuitive and powerful set of tools for developers.

## 🚀 Features

- **System Health Checks**: Comprehensive system and environment validation
- **Workspace Management**: Intelligent workspace analysis and configuration
- **AI-Powered Automation**: Smart automation for common development tasks
- **Rich Terminal UI**: Beautiful, colorful output with progress indicators
- **Extensible Architecture**: Modular design for easy feature additions

## 📦 Installation

### From Source (Development)

1. Clone the repository:
```bash
git clone <repository-url>
cd bAIos/cli
```

2. Install in development mode:
```bash
pip install -e .
```

3. Verify installation:
```bash
baios --version
```

### Using pip (Future)

```bash
pip install baios
```

## 🎯 Usage

### Basic Commands

```bash
# Show version
baios --version

# Get help
baios --help

# Quick health check
baios check health

# System check
baios check system

# Workspace analysis
baios check workspace

# Run all checks
baios check all
```

### Available Commands

- `baios hello [NAME]` - Simple greeting command (example)
- `baios status` - Show bAIos system status
- `baios check health` - Quick health check
- `baios check system` - Detailed system requirements check
- `baios check workspace` - Analyze current workspace
- `baios check all` - Run comprehensive checks

## 🔧 Development

### Setup Development Environment

1. **Clone and setup**:
```bash
git clone <repository-url>
cd bAIos/cli
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

2. **Install pre-commit hooks**:
```bash
pre-commit install
```

3. **Run tests**:
```bash
pytest
```

4. **Code formatting**:
```bash
black baios/
isort baios/
```

5. **Type checking**:
```bash
mypy baios/
```

### Project Structure

```
cli/
├── baios/                  # Main package
│   ├── __init__.py        # Package initialization
│   ├── main.py            # CLI entry point
│   └── commands/          # Command modules
│       ├── __init__.py
│       └── check.py       # Check commands
├── tests/                 # Test suite (to be created)
├── pyproject.toml         # Project configuration
└── README.md             # This file
```

### Adding New Commands

1. Create a new module in `baios/commands/`
2. Import and add it to `baios/commands/__init__.py`
3. Register it in `baios/main.py`

Example:
```python
# baios/commands/my_command.py
import typer
from rich import print as rprint

app = typer.Typer(help="My command description")

@app.command()
def my_action():
    """My action description"""
    rprint("[green]Hello from my command![/green]")

# baios/main.py
from .commands import my_command
app.add_typer(my_command.app, name="my-cmd", help="My command help")
```

## 📋 Requirements

- **Python**: 3.8 or higher
- **Dependencies**: 
  - `typer[all]` - CLI framework with rich features
  - `rich` - Rich text and beautiful formatting
  - `pydantic` - Data validation and settings management
  - `click` - Command line interface toolkit

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=baios

# Run specific test file
pytest tests/test_check.py

# Run tests with verbose output
pytest -v
```

## 📚 Documentation

### CLI Help

Each command includes built-in help:

```bash
baios --help                 # Main help
baios check --help           # Check commands help
baios check system --help    # System check help
```

### Command Examples

**Health Check**:
```bash
$ baios check health
💚 bAIos Health Check

┌─ Health Status ──────────────────────┐
│ 🟢 HEALTHY                          │
│                                      │
│ All essential components are         │
│ working properly!                    │
└──────────────────────────────────────┘
```

**System Check**:
```bash
$ baios check system
🔍 Running system checks...

┌─ 🖥️ System Check Results ────────────────────────────────────┐
│ Component  Status     Details                                │
│ Python     ✅ OK      v3.11.5                               │
│ Platform   ℹ️ INFO    Linux 5.15.0                          │
│ Git        ✅ OK      v2.34.1                               │
│ Node.js    ✅ OK      v18.17.0                              │
└───────────────────────────────────────────────────────────────┘
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

- [ ] AI-powered workspace optimization
- [ ] Integration with popular development tools
- [ ] Configuration management
- [ ] Project templates and scaffolding
- [ ] Automated development workflows
- [ ] Plugin system for extensibility

## 💬 Support

- 📚 Documentation: [Coming Soon]
- 🐛 Issues: [GitHub Issues](https://github.com/delorenj/bAIos/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/delorenj/bAIos/discussions)

---

Built with ❤️ by the bAIos team