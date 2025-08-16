#!/usr/bin/env python3
"""
Test suite for agent filesystem capabilities.
Tests the new script writing and file creation features.
"""

import pytest
import tempfile
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from baios.agents.shelldon import Shelldon
from baios.agents.base import Agent


class TestAgentFilesystem:
    """Test filesystem capabilities of agents."""
    
    def setup_method(self):
        """Set up test environment."""
        self.agent = Shelldon()
        self.temp_dir = tempfile.mkdtemp(prefix="baios_test_")
    
    def teardown_method(self):
        """Clean up test environment."""
        # Clean up temp files
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_detect_python_script_request(self):
        """Test detection of Python script requests."""
        questions = [
            "Write a Python script that prints hello",
            "Create a python script for me",
            "Generate a Python script to process files",
            "Make a py script"
        ]
        
        for question in questions:
            is_script, script_type, filename = self.agent.detect_script_request(question)
            assert is_script == True, f"Failed to detect script request in: {question}"
            assert script_type == "python", f"Wrong script type for: {question}"
            assert filename.endswith(".py"), f"Wrong extension for: {question}"
    
    def test_detect_bash_script_request(self):
        """Test detection of Bash script requests."""
        questions = [
            "Write a bash script to backup files",
            "Create a shell script",
            "Generate a sh script for automation"
        ]
        
        for question in questions:
            is_script, script_type, filename = self.agent.detect_script_request(question)
            assert is_script == True, f"Failed to detect script request in: {question}"
            assert script_type == "bash", f"Wrong script type for: {question}"
            assert filename.endswith(".sh"), f"Wrong extension for: {question}"
    
    def test_detect_non_script_request(self):
        """Test that non-script requests are not detected."""
        questions = [
            "What is my default shell?",
            "How do I configure zsh?",
            "List running processes",
            "Show me system information"
        ]
        
        for question in questions:
            is_script, script_type, filename = self.agent.detect_script_request(question)
            assert is_script == False, f"Incorrectly detected script in: {question}"
            assert script_type is None
            assert filename is None
    
    def test_write_python_script(self):
        """Test writing a Python script to filesystem."""
        content = "print('Hello from test')"
        filename = "test_script.py"
        
        success, filepath = self.agent.write_script(content, filename, "Test Python script")
        
        assert success == True, f"Failed to write script: {filepath}"
        
        # Verify file exists
        script_path = Path(filepath)
        assert script_path.exists(), f"Script not created at: {filepath}"
        
        # Verify content
        with open(script_path, 'r') as f:
            file_content = f.read()
        
        assert "Hello from test" in file_content
        assert "#!/usr/bin/env python3" in file_content  # Check header
        assert "Test Python script" in file_content  # Check description
    
    def test_write_bash_script(self):
        """Test writing a Bash script to filesystem."""
        content = "echo 'Hello from bash'"
        filename = "test_script.sh"
        
        success, filepath = self.agent.write_script(content, filename, "Test Bash script")
        
        assert success == True, f"Failed to write script: {filepath}"
        
        # Verify file exists
        script_path = Path(filepath)
        assert script_path.exists(), f"Script not created at: {filepath}"
        
        # Verify content
        with open(script_path, 'r') as f:
            file_content = f.read()
        
        assert "Hello from bash" in file_content
        assert "#!/bin/bash" in file_content  # Check header
        assert "Test Bash script" in file_content  # Check description
        
        # Check it's executable
        assert os.access(script_path, os.X_OK), "Bash script not executable"
    
    def test_safe_path_resolution(self):
        """Test that paths are resolved safely."""
        # Test simple filename goes to temp
        safe_path = self.agent.safe_path("test.txt")
        assert "tmp" in str(safe_path).lower() or "temp" in str(safe_path).lower()
        
        # Test relative path in current directory
        safe_path = self.agent.safe_path("./scripts/test.py")
        assert safe_path.is_absolute()
        
        # Test that unsafe paths are sandboxed
        safe_path = self.agent.safe_path("/etc/passwd")
        assert "/etc/passwd" not in str(safe_path)
        assert "baios_agents" in str(safe_path)
    
    def test_agent_handles_script_request_in_ask(self):
        """Test that ask() method properly handles script requests."""
        response = self.agent.ask("Write a Python script that prints 'Hello from Shelldon'")
        
        # Check response indicates success
        assert "created" in response.lower() or "script" in response.lower()
        assert "Location:" in response or "filepath" in response.lower()
        
        # Should include run instructions
        assert "python" in response.lower() or "run" in response.lower()
    
    def test_agent_handles_normal_question(self):
        """Test that normal questions still work."""
        response = self.agent.ask("What is my default shell?")
        
        # Should not create a script
        assert "created" not in response.lower() or "script created" not in response.lower()
        
        # Should answer the question
        assert "shell" in response.lower()
    
    def test_format_script_response(self):
        """Test response formatting for script creation."""
        # Test success response
        response = self.agent.format_script_response(True, "/tmp/test.py", "print('test')")
        assert "✅" in response
        assert "/tmp/test.py" in response
        assert "python /tmp/test.py" in response
        
        # Test failure response
        response = self.agent.format_script_response(False, "Permission denied")
        assert "❌" in response
        assert "Permission denied" in response


class TestShelldonSpecific:
    """Test Shelldon-specific script generation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.shelldon = Shelldon()
    
    def test_shelldon_hello_python_script(self):
        """Test Shelldon creates hello world Python script."""
        response = self.shelldon.ask("Write a Python script that prints hello")
        
        assert "Shelldon" in response
        assert "created" in response.lower()
        assert ".py" in response
        
        # Verify script was actually created
        # Extract filepath from response
        import re
        match = re.search(r'`([^`]*\.py)`', response)
        if match:
            filepath = match.group(1)
            assert Path(filepath).exists(), f"Script not found at {filepath}"
            
            # Check content
            with open(filepath, 'r') as f:
                content = f.read()
            assert "Hello from Shelldon" in content
    
    def test_shelldon_system_info_script(self):
        """Test Shelldon creates system info script."""
        response = self.shelldon.ask("Create a Python script for system info")
        
        assert "Shelldon" in response
        assert "created" in response.lower()
        
        # Extract filepath
        import re
        match = re.search(r'`([^`]*\.py)`', response)
        if match:
            filepath = match.group(1)
            script_path = Path(filepath)
            assert script_path.exists()
            
            # Check it has system info code
            with open(script_path, 'r') as f:
                content = f.read()
            assert "platform" in content or "system" in content.lower()


def test_checkpoint_3_requirements():
    """Validate that Checkpoint 3 requirements are met."""
    # Initialize agent
    shelldon = Shelldon()
    
    # Test 1: Agent can write scripts
    response = shelldon.ask("Write a simple Python script")
    assert "created" in response.lower() or "wrote" in response.lower()
    
    # Test 2: Agent responds to CLI ask queries  
    response = shelldon.ask("Is zsh my default shell?")
    assert len(response) > 0
    assert "shell" in response.lower()
    
    # Test 3: Agent has filesystem interaction capability
    content = "test content"
    success, filepath = shelldon.write_script(content, "test.txt")
    assert success == True
    assert Path(filepath).exists()
    
    print("✅ All Checkpoint 3 requirements validated!")
    print("  - Agent can write scripts/files")
    print("  - Agent responds to CLI ask queries")
    print("  - Agent has filesystem interaction capability")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])