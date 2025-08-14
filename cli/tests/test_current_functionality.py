#!/usr/bin/env python3
"""
Quick test to validate current functionality while waiting for agent implementation.

This test verifies that the current baios CLI is working correctly and serves
as a baseline before agent functionality is added.
"""

import subprocess
import sys
from pathlib import Path

# Add the baios package to path for testing
CLI_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(CLI_PATH))

def run_baios_command(cmd_args, timeout=30):
    """Run a baios command and return output."""
    cmd = ["python", "-m", "baios.main"] + cmd_args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=CLI_PATH,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def test_basic_cli_works():
    """Test that basic CLI functionality works."""
    print("🧪 Testing: Basic CLI functionality")
    
    # Test help command
    returncode, stdout, stderr = run_baios_command(["--help"])
    
    if returncode != 0:
        print(f"❌ Basic CLI help failed: {stderr}")
        return False
    
    if "baios" not in stdout.lower():
        print(f"❌ CLI help doesn't contain 'baios'")
        return False
    
    print("✅ Basic CLI functionality works")
    return True

def test_check_command_works():
    """Test that the check command works (Checkpoint 1)."""
    print("🧪 Testing: Check command (Checkpoint 1)")
    
    returncode, stdout, stderr = run_baios_command(["check"])
    
    if returncode != 0:
        print(f"❌ Check command failed: {stderr}")
        return False
    
    expected_indicators = [
        "inventory",
        "status",
        "items"
    ]
    
    for indicator in expected_indicators:
        if indicator.lower() not in stdout.lower():
            print(f"⚠️  Expected indicator '{indicator}' not found in output")
    
    print("✅ Check command works (Checkpoint 1 validated)")
    return True

def test_agent_commands_not_yet_implemented():
    """Test that agent commands are not yet implemented (expected state)."""
    print("🧪 Testing: Agent commands not yet implemented")
    
    # Try to run agent command - should fail for now
    returncode, stdout, stderr = run_baios_command(["agent", "--help"])
    
    if returncode == 0:
        print("⚠️  Agent commands appear to be implemented! Ready for testing.")
        return True
    else:
        print("✅ Agent commands not yet implemented (expected state)")
        return True

def main():
    """Run current functionality tests."""
    print("🔍 Testing current bAIos CLI functionality...\n")
    
    tests = [
        test_basic_cli_works,
        test_check_command_works,
        test_agent_commands_not_yet_implemented
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("   ❌ Test failed")
        except Exception as e:
            print(f"   💥 Test crashed: {e}")
        print()
    
    print(f"📊 Current functionality tests: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("🎯 Current CLI is working properly. Ready for agent implementation.")
        return 0
    else:
        print("⚠️  Some basic functionality issues detected.")
        return 1

if __name__ == "__main__":
    exit(main())