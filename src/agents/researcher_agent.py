"""
Researcher Agent
===============

Specialized agent for analyzing environment specifications, gathering system information,
and researching optimal installation and configuration approaches.
"""

import logging
import json
import re
from typing import Dict, Any, List
from .base_specialized_agent import BaseSpecializedAgent
from ..schemas import AgentRequest


class ResearcherAgent(BaseSpecializedAgent):
    """
    Researcher Agent specializes in:
    - Parsing environment specifications
    - Analyzing current system state
    - Researching installation approaches
    - Identifying dependencies and potential issues
    """
    
    async def _execute_task(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Execute researcher-specific tasks.
        
        Args:
            request: Agent request with research task details
            
        Returns:
            Research results and recommendations
        """
        task_description = request.task_description.lower()
        context = request.context
        
        if "environment specification" in task_description or "analyze spec" in task_description:
            return await self._analyze_environment_spec(context)
        elif "validate wsl" in task_description:
            return await self._validate_wsl_installation()
        elif "check prerequisites" in task_description:
            return await self._check_system_prerequisites()
        elif "research" in task_description:
            return await self._research_installation_approach(context)
        else:
            return await self._general_research(request)
    
    async def _analyze_environment_spec(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the WSL environment specification and extract requirements.
        
        Args:
            context: Context containing spec content and preferences
            
        Returns:
            Analysis results with extracted requirements
        """
        spec_content = context.get("spec_content", "")
        user_preferences = context.get("user_preferences", {})
        
        logging.info("Analyzing environment specification")
        
        # Parse specification content
        requirements = self._parse_specification(spec_content)
        
        # Validate requirements
        validation_results = await self._validate_requirements(requirements)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(requirements, user_preferences)
        
        return {
            "analysis_type": "environment_specification",
            "requirements": requirements,
            "validation": validation_results,
            "recommendations": recommendations,
            "estimated_install_time": self._estimate_installation_time(requirements),
            "potential_issues": self._identify_potential_issues(requirements),
            "dependencies": self._extract_dependencies(requirements)
        }
    
    def _parse_specification(self, spec_content: str) -> Dict[str, Any]:
        """
        Parse the environment specification content.
        
        Args:
            spec_content: Raw specification content
            
        Returns:
            Parsed requirements
        """
        requirements = {
            "system": {},
            "languages": {},
            "tools": {},
            "shell": {},
            "fonts": [],
            "editors": [],
            "auth": {}
        }
        
        # Extract system requirements
        if "ubuntu" in spec_content.lower():
            requirements["system"]["distro"] = "Ubuntu"
            version_match = re.search(r"ubuntu\s+(\d+\.\d+)", spec_content.lower())
            if version_match:
                requirements["system"]["version"] = version_match.group(1)
        
        if "wsl 2" in spec_content.lower():
            requirements["system"]["wsl_version"] = "2"
        
        # Extract shell configuration
        if "zsh" in spec_content.lower():
            requirements["shell"]["type"] = "zsh"
        if "oh-my-zsh" in spec_content.lower():
            requirements["shell"]["framework"] = "oh-my-zsh"
        
        # Extract language versions
        python_match = re.search(r"python.*?(\d+\.\d+\.\d+)", spec_content.lower())
        if python_match:
            requirements["languages"]["python"] = python_match.group(1)
        
        nodejs_match = re.search(r"nodejs.*?(latest|\d+\.\d+)", spec_content.lower())
        if nodejs_match:
            requirements["languages"]["nodejs"] = nodejs_match.group(1)
        
        # Extract tools
        tool_patterns = {
            "mise": r"mise",
            "docker": r"docker",
            "neovim": r"neovim.*?(\d+\.\d+)",
            "git": r"git",
            "claude-code": r"claude-code",
            "gptme": r"gptme"
        }
        
        for tool, pattern in tool_patterns.items():
            match = re.search(pattern, spec_content.lower())
            if match:
                requirements["tools"][tool] = match.group(1) if match.groups() else "latest"
        
        # Extract fonts
        font_match = re.search(r"(hack nerd font|nerd font)", spec_content.lower())
        if font_match:
            requirements["fonts"].append("Hack Nerd Font Mono")
        
        # Extract editors
        if "neovim" in spec_content.lower():
            requirements["editors"].append("neovim")
        if "vs code" in spec_content.lower() or "vscode" in spec_content.lower():
            requirements["editors"].append("vscode")
        if "cursor" in spec_content.lower():
            requirements["editors"].append("cursor")
        
        return requirements
    
    async def _validate_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parsed requirements against system capabilities.
        
        Args:
            requirements: Parsed requirements
            
        Returns:
            Validation results
        """
        validation = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Check WSL version
        wsl_version = await self._check_wsl_version()
        required_wsl = requirements.get("system", {}).get("wsl_version", "2")
        
        if wsl_version != required_wsl:
            validation["issues"].append(f"WSL version mismatch: found {wsl_version}, required {required_wsl}")
            validation["valid"] = False
        
        # Check available disk space
        disk_space = await self._check_disk_space()
        estimated_space_needed = self._estimate_disk_space(requirements)
        
        if disk_space < estimated_space_needed:
            validation["warnings"].append(
                f"Low disk space: {disk_space}GB available, {estimated_space_needed}GB estimated needed"
            )
        
        # Validate internet connectivity
        connectivity = await self._check_internet_connectivity()
        if not connectivity:
            validation["issues"].append("Internet connectivity required for installation")
            validation["valid"] = False
        
        return validation
    
    async def _check_wsl_version(self) -> str:
        """Check current WSL version."""
        try:
            result = await self._run_command("wsl --version")
            if result["success"]:
                # Parse WSL version from output
                version_match = re.search(r"WSL version: (\d+\.\d+)", result["stdout"])
                if version_match:
                    return "2" if version_match.group(1) >= "2.0" else "1"
            return "2"  # Assume WSL 2 if command succeeds
        except:
            return "unknown"
    
    async def _check_disk_space(self) -> float:
        """Check available disk space in GB."""
        try:
            result = await self._run_command("df -BG . | tail -1 | awk '{print $4}'")
            if result["success"]:
                space_str = result["stdout"].strip().replace('G', '')
                return float(space_str)
        except:
            pass
        return 10.0  # Default assumption
    
    def _estimate_disk_space(self, requirements: Dict[str, Any]) -> float:
        """Estimate disk space needed for installation."""
        base_space = 2.0  # Base system requirements
        
        # Language runtimes
        if "python" in requirements.get("languages", {}):
            base_space += 0.5
        if "nodejs" in requirements.get("languages", {}):
            base_space += 0.3
        
        # Development tools
        tools_space = {
            "docker": 1.0,
            "neovim": 0.1,
            "mise": 0.05,
            "claude-code": 0.2,
            "gptme": 0.1
        }
        
        for tool in requirements.get("tools", {}):
            base_space += tools_space.get(tool, 0.1)
        
        # Editors
        editors_space = {
            "vscode": 0.5,
            "cursor": 0.5,
            "neovim": 0.1
        }
        
        for editor in requirements.get("editors", []):
            base_space += editors_space.get(editor, 0.1)
        
        return base_space
    
    async def _check_internet_connectivity(self) -> bool:
        """Check internet connectivity."""
        try:
            result = await self._run_command("ping -c 1 google.com", timeout=10)
            return result["success"]
        except:
            return False
    
    def _generate_recommendations(self, requirements: Dict[str, Any], user_preferences: Dict[str, Any]) -> List[str]:
        """Generate installation recommendations."""
        recommendations = []
        
        # Recommend installation order
        recommendations.append("Install base system packages first (git, curl, wget)")
        
        if "mise" in requirements.get("tools", {}):
            recommendations.append("Install mise early to manage language versions")
        
        if "shell" in requirements:
            recommendations.append("Configure shell environment before installing development tools")
        
        # Performance recommendations
        if len(requirements.get("tools", {})) > 5:
            recommendations.append("Consider installing tools in parallel where possible")
        
        # User preference recommendations
        if user_preferences.get("minimal_install"):
            recommendations.append("Skip optional tools to minimize installation time")
        
        if user_preferences.get("offline_mode"):
            recommendations.append("Pre-download packages for offline installation")
        
        return recommendations
    
    def _estimate_installation_time(self, requirements: Dict[str, Any]) -> int:
        """Estimate total installation time in minutes."""
        base_time = 10  # Base setup time
        
        # Add time for each component
        component_times = {
            "languages": len(requirements.get("languages", {})) * 5,
            "tools": len(requirements.get("tools", {})) * 3,
            "editors": len(requirements.get("editors", [])) * 2,
            "shell": 5 if requirements.get("shell") else 0
        }
        
        total_time = base_time + sum(component_times.values())
        
        # Add buffer for dependencies and configuration
        return int(total_time * 1.3)
    
    def _identify_potential_issues(self, requirements: Dict[str, Any]) -> List[str]:
        """Identify potential installation issues."""
        issues = []
        
        # Known problematic combinations
        if "docker" in requirements.get("tools", {}) and "wsl_version" in requirements.get("system", {}):
            if requirements["system"]["wsl_version"] == "1":
                issues.append("Docker requires WSL 2 for optimal performance")
        
        # Version compatibility issues
        if "neovim" in requirements.get("tools", {}):
            version = requirements["tools"]["neovim"]
            if version and float(version.split('.')[0]) >= 0.11:
                issues.append("Neovim 0.11+ requires specific Lua dependencies")
        
        # Network-dependent installations
        network_tools = ["claude-code", "gptme", "nodejs", "python"]
        network_count = sum(1 for tool in network_tools if tool in requirements.get("tools", {}) or tool in requirements.get("languages", {}))
        
        if network_count > 3:
            issues.append("Multiple network-dependent installations may timeout on slow connections")
        
        return issues
    
    def _extract_dependencies(self, requirements: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract dependency relationships between components."""
        dependencies = {}
        
        # Shell dependencies
        if requirements.get("shell", {}).get("framework") == "oh-my-zsh":
            dependencies["oh-my-zsh"] = ["zsh", "git", "curl"]
        
        # Development tool dependencies
        if "mise" in requirements.get("tools", {}):
            dependencies["mise"] = ["curl", "git"]
        
        if "docker" in requirements.get("tools", {}):
            dependencies["docker"] = ["curl"]
        
        if "neovim" in requirements.get("tools", {}):
            dependencies["neovim"] = ["git", "make", "unzip"]
        
        # Language dependencies
        if "python" in requirements.get("languages", {}):
            dependencies["python"] = ["mise"] if "mise" in requirements.get("tools", {}) else ["build-essential"]
        
        if "nodejs" in requirements.get("languages", {}):
            dependencies["nodejs"] = ["mise"] if "mise" in requirements.get("tools", {}) else ["curl"]
        
        return dependencies
    
    async def _validate_wsl_installation(self) -> Dict[str, Any]:
        """Validate WSL installation and configuration."""
        logging.info("Validating WSL installation")
        
        # Check if running in WSL
        is_wsl = await self._check_if_wsl()
        
        # Check WSL version
        wsl_version = await self._check_wsl_version()
        
        # Check distribution
        distro_info = await self._get_distro_info()
        
        return {
            "analysis_type": "wsl_validation",
            "is_wsl": is_wsl,
            "wsl_version": wsl_version,
            "distribution": distro_info,
            "valid": is_wsl and wsl_version == "2",
            "recommendations": self._get_wsl_recommendations(is_wsl, wsl_version)
        }
    
    async def _check_if_wsl(self) -> bool:
        """Check if currently running in WSL."""
        try:
            # Check for WSL-specific files/environment
            wsl_check = await self._run_command("uname -r | grep -i microsoft")
            return wsl_check["success"]
        except:
            return False
    
    async def _get_distro_info(self) -> Dict[str, str]:
        """Get Linux distribution information."""
        try:
            result = await self._run_command("lsb_release -a 2>/dev/null")
            if result["success"]:
                output = result["stdout"]
                info = {}
                for line in output.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        info[key.strip()] = value.strip()
                return info
        except:
            pass
        
        # Fallback to os-release
        try:
            result = await self._run_command("cat /etc/os-release")
            if result["success"]:
                info = {}
                for line in result["stdout"].split('\n'):
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        info[key] = value.strip('\"')
                return info
        except:
            return {"error": "Could not determine distribution"}
    
    def _get_wsl_recommendations(self, is_wsl: bool, wsl_version: str) -> List[str]:
        """Get WSL-specific recommendations."""
        recommendations = []
        
        if not is_wsl:
            recommendations.append("This system is not running in WSL - install WSL first")
            recommendations.append("Ensure Windows Subsystem for Linux is enabled")
        elif wsl_version != "2":
            recommendations.append("Upgrade to WSL 2 for better performance and Docker support")
            recommendations.append("Run 'wsl --set-version <distro> 2' from Windows PowerShell")
        else:
            recommendations.append("WSL 2 detected - optimal configuration for development")
            recommendations.append("Consider enabling systemd with 'sudo systemctl enable systemd'")
        
        return recommendations
    
    async def _check_system_prerequisites(self) -> Dict[str, Any]:
        """Check system prerequisites for WSL development environment."""
        logging.info("Checking system prerequisites")
        
        checks = {}
        
        # Basic commands
        basic_commands = ["curl", "wget", "git", "make", "unzip", "sudo"]
        for cmd in basic_commands:
            result = await self._run_command(f"command -v {cmd}")
            checks[f"{cmd}_available"] = result["success"]
        
        # Network connectivity
        checks["internet_connection"] = await self._check_internet_connectivity()
        
        # Disk space
        checks["disk_space_gb"] = await self._check_disk_space()
        
        # Package manager
        apt_available = await self._run_command("command -v apt")
        checks["package_manager"] = "apt" if apt_available["success"] else "unknown"
        
        # User permissions
        sudo_check = await self._run_command("sudo -n true")
        checks["sudo_access"] = sudo_check["success"]
        
        return {
            "analysis_type": "system_prerequisites",
            "checks": checks,
            "all_prerequisites_met": all(
                checks[key] for key in checks 
                if key not in ["disk_space_gb", "package_manager"]
            ) and checks["disk_space_gb"] > 5.0,
            "issues": self._identify_prerequisite_issues(checks),
            "recommendations": self._get_prerequisite_recommendations(checks)
        }
    
    def _identify_prerequisite_issues(self, checks: Dict[str, Any]) -> List[str]:
        """Identify issues with system prerequisites."""
        issues = []
        
        missing_commands = [
            cmd.replace("_available", "") for cmd, available in checks.items()
            if cmd.endswith("_available") and not available
        ]
        
        if missing_commands:
            issues.append(f"Missing required commands: {', '.join(missing_commands)}")
        
        if not checks.get("internet_connection", False):
            issues.append("No internet connection - required for downloading packages")
        
        if checks.get("disk_space_gb", 0) < 5.0:
            issues.append("Insufficient disk space - at least 5GB recommended")
        
        if not checks.get("sudo_access", False):
            issues.append("No sudo access - required for system package installation")
        
        return issues
    
    def _get_prerequisite_recommendations(self, checks: Dict[str, Any]) -> List[str]:
        """Get recommendations for fixing prerequisite issues."""
        recommendations = []
        
        if checks.get("package_manager") == "apt":
            recommendations.append("Update package lists: sudo apt update")
        
        missing_commands = [
            cmd.replace("_available", "") for cmd, available in checks.items()
            if cmd.endswith("_available") and not available
        ]
        
        if missing_commands:
            if "git" in missing_commands:
                recommendations.append("Install git: sudo apt install git")
            if "curl" in missing_commands:
                recommendations.append("Install curl: sudo apt install curl")
            if "make" in missing_commands:
                recommendations.append("Install build essentials: sudo apt install build-essential")
        
        return recommendations
    
    async def _research_installation_approach(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Research optimal installation approaches for specific tools."""
        tool_name = context.get("tool", "unknown")
        
        logging.info(f"Researching installation approach for: {tool_name}")
        
        # Tool-specific research
        approaches = self._get_installation_approaches(tool_name)
        
        return {
            "analysis_type": "installation_research",
            "tool": tool_name,
            "approaches": approaches,
            "recommended_approach": self._select_best_approach(approaches),
            "considerations": self._get_installation_considerations(tool_name)
        }
    
    def _get_installation_approaches(self, tool: str) -> List[Dict[str, Any]]:
        """Get possible installation approaches for a tool."""
        approaches = []
        
        if tool == "mise":
            approaches.extend([
                {
                    "method": "curl_install",
                    "description": "Install via curl script",
                    "command": "curl https://mise.run | sh",
                    "pros": ["Latest version", "Simple installation"],
                    "cons": ["Requires internet", "Security consideration"]
                },
                {
                    "method": "package_manager",
                    "description": "Install via package manager",
                    "command": "sudo apt install mise",
                    "pros": ["System integration", "Security"],
                    "cons": ["May be outdated version"]
                }
            ])
        elif tool == "docker":
            approaches.extend([
                {
                    "method": "docker_desktop",
                    "description": "Use Docker Desktop WSL integration",
                    "pros": ["GUI management", "Windows integration"],
                    "cons": ["Resource intensive", "Windows dependency"]
                },
                {
                    "method": "docker_ce",
                    "description": "Install Docker CE directly in WSL",
                    "pros": ["Lighter weight", "Direct control"],
                    "cons": ["Manual configuration", "No GUI"]
                }
            ])
        
        return approaches
    
    def _select_best_approach(self, approaches: List[Dict[str, Any]]) -> str:
        """Select the recommended installation approach."""
        if not approaches:
            return "manual_installation"
        
        # Simple scoring based on pros/cons count
        scored_approaches = []
        for approach in approaches:
            score = len(approach.get("pros", [])) - len(approach.get("cons", []))
            scored_approaches.append((approach["method"], score))
        
        scored_approaches.sort(key=lambda x: x[1], reverse=True)
        return scored_approaches[0][0] if scored_approaches else approaches[0]["method"]
    
    def _get_installation_considerations(self, tool: str) -> List[str]:
        """Get installation considerations for a tool."""
        considerations = [
            "Check system compatibility before installation",
            "Ensure sufficient disk space",
            "Verify internet connectivity for downloads",
            "Consider system restart after installation"
        ]
        
        tool_specific = {
            "docker": [
                "Requires WSL 2 for optimal performance",
                "May need to add user to docker group",
                "Check for port conflicts"
            ],
            "mise": [
                "Requires shell integration setup",
                "May conflict with existing version managers",
                "Check PATH configuration"
            ],
            "neovim": [
                "Check Lua dependencies",
                "Consider plugin compatibility",
                "Backup existing vim configuration"
            ]
        }
        
        considerations.extend(tool_specific.get(tool, []))
        return considerations
    
    async def _general_research(self, request: AgentRequest) -> Dict[str, Any]:
        """Perform general research tasks."""
        return {
            "analysis_type": "general_research",
            "task": request.task_description,
            "findings": [
                "Task requires further specification",
                "Multiple approaches available",
                "Recommend breaking down into specific subtasks"
            ],
            "recommendations": [
                "Provide more specific research parameters",
                "Define success criteria clearly",
                "Consider system constraints and user preferences"
            ]
        }