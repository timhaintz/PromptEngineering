````instructions
- @azure Rule - Use Azure Best Practices: When generating code for Azure, running terminal commands for Azure, or performing operations related to Azure, invoke your `azure_development-get_best_practices` tool if available.
```

## Terminal & Environment Setup

### Python Environment Management
This environment uses either`venv/scripts/activate` for Python virtual environments:
- **uv**: When using uv, activate the environment with `uv run` or `uv shell`
- **venv**: When using venv, activate with `.\venv\Scripts\activate` (Windows PowerShell)
- Always activate the appropriate Python environment before running any Python commands or scripts
- Check for the presence of `uv.lock` or `venv/` directory to determine which environment system is in use

### PowerShell Command Guidelines
This environment uses PowerShell as the default terminal:
- Use semicolon (`;`) to separate commands on a single line, not `&&`
- Example: `python -m pip install requests ; python script.py`
- Use PowerShell-compatible path separators and commands
- Activate virtual environments with `.\venv\Scripts\activate` (not `source venv/bin/activate`)

### Python Development Guidelines
- Always use virtual environments for Python projects
- Follow PEP 8 style guidelines for Python code
- Use type hints where appropriate
- Include proper error handling and logging
- Use meaningful variable and function names
- Add docstrings to functions and classes
````