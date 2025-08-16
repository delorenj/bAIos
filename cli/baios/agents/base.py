#!/usr/bin/env python3
"""
Base Agent class for bAIos CLI specialized agents.

This module provides the abstract base class that all specialized agents inherit from,
defining the common interface and core functionality.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple
import platform
import subprocess
import os
from pathlib import Path
import re
import tempfile
import datetime


class Agent(ABC):
    """
    Abstract base class for bAIos specialized agents.
    
    Each agent represents a domain expert that can answer questions and provide
    guidance within their area of expertise.
    """
    
    def __init__(self, name: str, expertise: str, personality: str = ""):
        """
        Initialize the agent.
        
        Args:
            name: The agent's display name
            expertise: Brief description of agent's expertise area
            personality: Optional personality description
        """
        self.name = name
        self.expertise = expertise
        self.personality = personality
        
    def ask(self, question: str) -> str:
        """
        Ask the agent a question and get an expert response.
        Base implementation handles script requests.
        
        Args:
            question: The question to ask the agent
            
        Returns:
            The agent's response as a string
        """
        # Check if this is a script request
        is_script_request, script_type, suggested_filename = self.detect_script_request(question)
        
        if is_script_request:
            # Let derived class handle script generation
            return self.handle_script_request(question, script_type, suggested_filename)
        
        # For non-script requests, derived class must implement
        return self.handle_question(question)
    
    def handle_script_request(self, question: str, script_type: str, 
                            suggested_filename: str) -> str:
        """
        Handle a request to create a script.
        Override in derived classes for custom script generation.
        
        Args:
            question: Original question
            script_type: Type of script detected
            suggested_filename: Suggested filename
            
        Returns:
            Response about script creation
        """
        # Default implementation - derived classes should override
        return f"🤖 **{self.name}** detected a script request but doesn't have specific implementation yet.\n\nRequest type: {script_type}\nSuggested file: {suggested_filename}"
    
    @abstractmethod
    def handle_question(self, question: str) -> str:
        """
        Handle non-script questions. Must be implemented by derived classes.
        
        Args:
            question: The question to ask the agent
            
        Returns:
            The agent's response as a string
        """
        pass
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get basic system information that all agents can use.
        
        Returns:
            Dictionary containing system information
        """
        return {
            "platform": platform.system(),
            "platform_release": platform.release(), 
            "platform_version": platform.platform(),
            "architecture": platform.machine(),
            "processor": platform.processor() or "Unknown",
            "python_version": platform.python_version(),
            "home_dir": str(Path.home()),
            "current_dir": str(Path.cwd()),
            "user": os.environ.get("USER", os.environ.get("USERNAME", "Unknown"))
        }
    
    def run_command(self, command: str, capture_output: bool = True) -> Optional[str]:
        """
        Run a system command safely.
        
        Args:
            command: Command to execute
            capture_output: Whether to capture and return output
            
        Returns:
            Command output if capture_output is True and command succeeds, None otherwise
        """
        try:
            if capture_output:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return result.stdout.strip() if result.returncode == 0 else None
            else:
                result = subprocess.run(command.split(), timeout=10)
                return None
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return None
    
    def check_command_available(self, command: str) -> bool:
        """
        Check if a command is available on the system.
        
        Args:
            command: Command name to check
            
        Returns:
            True if command is available, False otherwise
        """
        return self.run_command(f"which {command}") is not None
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.name} - {self.expertise}"
    
    def __repr__(self) -> str:
        """Developer representation of the agent."""
        return f"Agent(name='{self.name}', expertise='{self.expertise}')"
    
    def detect_script_request(self, question: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Detect if the user is requesting a script or file to be created.
        
        Args:
            question: The user's question
            
        Returns:
            Tuple of (is_script_request, script_type, suggested_filename)
        """
        question_lower = question.lower()
        
        # Common patterns for script requests
        script_patterns = [
            (r'write\s+(?:a\s+)?(?:simple\s+)?(\w+)?\s*script', 'script'),
            (r'create\s+(?:a\s+)?(?:simple\s+)?(\w+)?\s*script', 'script'),
            (r'generate\s+(?:a\s+)?(?:simple\s+)?(\w+)?\s*script', 'script'),
            (r'write\s+(?:a\s+)?(\w+)?\s*file', 'file'),
            (r'create\s+(?:a\s+)?(\w+)?\s*file', 'file'),
            (r'make\s+(?:a\s+)?(\w+)?\s*script', 'script'),
        ]
        
        # Check for script request patterns
        for pattern, request_type in script_patterns:
            match = re.search(pattern, question_lower)
            if match:
                # Detect language/type
                language = match.group(1) if match.group(1) else None
                
                # Determine file extension based on language
                if language:
                    if 'python' in language or 'py' in language:
                        ext = '.py'
                        lang_type = 'python'
                    elif 'bash' in language or 'shell' in language or 'sh' in language:
                        ext = '.sh'
                        lang_type = 'bash'
                    elif 'javascript' in language or 'js' in language:
                        ext = '.js'
                        lang_type = 'javascript'
                    elif 'java' in language and 'script' not in language:
                        ext = '.java'
                        lang_type = 'java'
                    else:
                        ext = '.txt'
                        lang_type = 'text'
                else:
                    # Default to Python if no language specified
                    ext = '.py'
                    lang_type = 'python'
                
                # Generate filename
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{self.name.lower().replace(' ', '_')}_{request_type}_{timestamp}{ext}"
                
                return True, lang_type, filename
        
        return False, None, None
    
    def write_script(self, content: str, filename: Optional[str] = None, 
                    description: Optional[str] = None) -> Tuple[bool, str]:
        """
        Write a script to the filesystem.
        
        Args:
            content: The script content
            filename: Optional filename (will auto-generate if not provided)
            description: Optional description of the script
            
        Returns:
            Tuple of (success, filepath_or_error)
        """
        try:
            # Use provided filename or generate one
            if not filename:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{self.name.lower().replace(' ', '_')}_script_{timestamp}.txt"
            
            # Ensure safe path (write to temp directory for safety)
            filepath = self.safe_path(filename)
            
            # Write the script
            with open(filepath, 'w') as f:
                # Add header comment if description provided
                if description:
                    if filepath.suffix == '.py':
                        f.write(f'#!/usr/bin/env python3\n')
                        f.write(f'"""\n{description}\n"""\n\n')
                    elif filepath.suffix == '.sh':
                        f.write(f'#!/bin/bash\n')
                        f.write(f'# {description}\n\n')
                    elif filepath.suffix == '.js':
                        f.write(f'// {description}\n\n')
                
                f.write(content)
            
            # Make script executable if it's a shell script
            if filepath.suffix in ['.sh', '.bash']:
                os.chmod(filepath, 0o755)
            
            return True, str(filepath)
            
        except Exception as e:
            return False, str(e)
    
    def create_file(self, content: str, filepath: str, 
                   file_type: Optional[str] = None) -> Tuple[bool, str]:
        """
        Create a file with the given content.
        
        Args:
            content: File content
            filepath: Path to create the file
            file_type: Optional file type hint
            
        Returns:
            Tuple of (success, filepath_or_error)
        """
        try:
            # Ensure safe path
            safe_filepath = self.safe_path(filepath)
            
            # Create parent directories if needed
            safe_filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            with open(safe_filepath, 'w') as f:
                f.write(content)
            
            return True, str(safe_filepath)
            
        except Exception as e:
            return False, str(e)
    
    def safe_path(self, user_path: str) -> Path:
        """
        Ensure a path is safe to write to.
        
        Args:
            user_path: User-provided path
            
        Returns:
            Safe Path object
        """
        # Convert to Path object
        path = Path(user_path)
        
        # If it's just a filename, put it in temp directory
        if not path.is_absolute() and len(path.parts) == 1:
            # Create agent-specific temp directory
            temp_dir = Path(tempfile.gettempdir()) / 'baios_agents' / self.name.lower().replace(' ', '_')
            temp_dir.mkdir(parents=True, exist_ok=True)
            return temp_dir / path
        
        # If it's in current directory, allow it
        if not path.is_absolute():
            return Path.cwd() / path
        
        # For absolute paths, verify they're in safe locations
        safe_dirs = [
            Path.home(),
            Path('/tmp'),
            Path(tempfile.gettempdir()),
            Path.cwd()
        ]
        
        # Check if path is within a safe directory
        for safe_dir in safe_dirs:
            try:
                path.relative_to(safe_dir)
                return path
            except ValueError:
                continue
        
        # If not in safe directory, put in temp
        temp_dir = Path(tempfile.gettempdir()) / 'baios_agents' / self.name.lower().replace(' ', '_')
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir / path.name
    
    def format_script_response(self, success: bool, filepath: str, 
                              content_preview: Optional[str] = None) -> str:
        """
        Format a response about script creation.
        
        Args:
            success: Whether the operation succeeded
            filepath: Path where file was created or error message
            content_preview: Optional preview of the content
            
        Returns:
            Formatted response string
        """
        if success:
            response = f"✅ **Script created successfully!**\n\n"
            response += f"📁 **Location:** `{filepath}`\n\n"
            
            if content_preview:
                response += f"**📝 Preview:**\n```\n{content_preview[:500]}\n"
                if len(content_preview) > 500:
                    response += "...\n"
                response += "```\n\n"
            
            response += f"**🚀 To run the script:**\n"
            
            # Add run instructions based on file type
            path = Path(filepath)
            if path.suffix == '.py':
                response += f"```bash\npython {filepath}\n```\n"
            elif path.suffix in ['.sh', '.bash']:
                response += f"```bash\nchmod +x {filepath}  # Make executable\n{filepath}\n```\n"
            elif path.suffix == '.js':
                response += f"```bash\nnode {filepath}\n```\n"
            
            return response
        else:
            return f"❌ **Failed to create script:** {filepath}\n\nPlease check permissions and try again."