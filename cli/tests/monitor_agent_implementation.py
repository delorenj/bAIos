#!/usr/bin/env python3
"""
Monitor script to detect when agent commands are implemented.

This script continuously monitors for the implementation of agent commands
and automatically triggers comprehensive testing when they become available.
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add the baios package to path
CLI_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(CLI_PATH))

def run_baios_command(cmd_args, timeout=10):
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

def check_agent_commands_available():
    """Check if agent commands are now available."""
    returncode, stdout, stderr = run_baios_command(["agent", "--help"])
    
    if returncode == 0:
        return True, stdout
    else:
        return False, stderr

def check_for_required_agents(help_output):
    """Check if all required agents are mentioned in help."""
    required_agents = ["BillTheCoordinator", "MiseMaster", "TzviTheWindowsWizard", "Shelldon"]
    
    # This is a basic check - actual implementation might vary
    return any(agent in help_output for agent in required_agents)

def run_comprehensive_tests():
    """Run the comprehensive test suite."""
    print("🚀 Agent commands detected! Running comprehensive test suite...")
    
    try:
        result = subprocess.run(
            [sys.executable, "tests/test_agent_commands.py"],
            cwd=CLI_PATH,
            timeout=600  # 10 minutes max
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Comprehensive tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running comprehensive tests: {e}")
        return False

def log_status(message):
    """Log status with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def monitor_implementation(check_interval=30, max_wait_minutes=60):
    """Monitor for implementation with periodic checks."""
    max_wait_seconds = max_wait_minutes * 60
    start_time = time.time()
    
    log_status("🔍 Starting agent implementation monitoring...")
    log_status(f"⏰ Will check every {check_interval}s for up to {max_wait_minutes} minutes")
    
    checks_performed = 0
    
    while time.time() - start_time < max_wait_seconds:
        checks_performed += 1
        
        # Check if agent commands are available
        available, output = check_agent_commands_available()
        
        if available:
            log_status("✅ Agent commands are now available!")
            log_status("🎯 Triggering comprehensive test suite...")
            
            # Run comprehensive tests
            success = run_comprehensive_tests()
            
            if success:
                log_status("🎉 All tests passed! Agent system is working correctly.")
                return True
            else:
                log_status("❌ Some tests failed. Check test output above.")
                return False
        
        # Calculate progress
        elapsed = int(time.time() - start_time)
        remaining = max_wait_seconds - elapsed
        progress = elapsed / max_wait_seconds * 100
        
        log_status(f"⏳ Check #{checks_performed}: Not ready yet ({elapsed}s elapsed, "
                  f"{remaining}s remaining, {progress:.1f}% complete)")
        
        # Wait before next check
        time.sleep(check_interval)
    
    log_status("⏰ Monitoring timeout reached")
    log_status("💡 Agent commands may need more time to be implemented")
    return False

def main():
    """Main monitoring function."""
    print("🤖 bAIos Agent Implementation Monitor")
    print("=" * 50)
    
    # First check current status
    available, output = check_agent_commands_available()
    
    if available:
        print("✅ Agent commands are already available!")
        print("🚀 Running comprehensive tests immediately...")
        success = run_comprehensive_tests()
        return 0 if success else 1
    else:
        print("⏳ Agent commands not yet implemented")
        print("🔍 Starting monitoring mode...")
        success = monitor_implementation()
        return 0 if success else 1

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring interrupted by user")
        print("💡 You can run this script again later to continue monitoring")
        exit(130)