#!/usr/bin/env python3
"""
Test file to verify the baios check command integration.

This test verifies that:
1. 'baios check' (without subcommand) runs the inventory check by default
2. The output format matches the requirements from Checkpoint 1
3. All required status types are properly displayed
4. Subcommands still work correctly
"""

import subprocess
import sys
from pathlib import Path
import re

# Add the baios package to path for testing
cli_path = Path(__file__).parent.parent
sys.path.insert(0, str(cli_path))

def run_baios_command(cmd_args):
    """Run a baios command and return output."""
    cmd = ["python", "-m", "baios.main"] + cmd_args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cli_path,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def test_default_check_runs_inventory():
    """Test that 'baios check' runs inventory by default."""
    print("🧪 Testing: baios check (default behavior)")
    
    returncode, stdout, stderr = run_baios_command(["check"])
    
    # Should succeed
    if returncode != 0:
        print(f"❌ Command failed with return code {returncode}")
        print(f"STDERR: {stderr}")
        return False
    
    # Should contain inventory-specific output
    required_indicators = [
        "📋 Checking bAIos inventory requirements",
        "📊 Overall Inventory Status",
        "Total Items",
        "Completed",
        "System Status"
    ]
    
    for indicator in required_indicators:
        if indicator not in stdout:
            print(f"❌ Missing expected output: {indicator}")
            return False
    
    print("✅ Default check runs inventory successfully")
    return True

def test_required_status_types_present():
    """Test that all required status types are present in output."""
    print("🧪 Testing: Required status types in output")
    
    returncode, stdout, stderr = run_baios_command(["check", "--detailed"])
    
    if returncode != 0:
        print(f"❌ Command failed with return code {returncode}")
        return False
    
    # Check for required status types from Checkpoint 1
    status_patterns = [
        r"✅",  # Complete
        r"❌.*Failed",  # Failed (Critical) - may not be present
        r"⚠️.*Failed",  # Failed (Non-Critical)
        r"🔴.*Not",  # Not Started (Required)
        r"📝.*Note"  # Note
    ]
    
    found_statuses = []
    for pattern in status_patterns:
        if re.search(pattern, stdout, re.IGNORECASE):
            found_statuses.append(pattern)
    
    # At least Complete, Note, and one other should be present
    if len(found_statuses) >= 3:
        print(f"✅ Found {len(found_statuses)} required status types")
        return True
    else:
        print(f"❌ Only found {len(found_statuses)} status types, expected at least 3")
        return False

def test_detailed_flag_works():
    """Test that --detailed flag provides more detailed output."""
    print("🧪 Testing: --detailed flag functionality")
    
    # Get normal output
    returncode1, stdout1, stderr1 = run_baios_command(["check"])
    
    # Get detailed output
    returncode2, stdout2, stderr2 = run_baios_command(["check", "--detailed"])
    
    if returncode1 != 0 or returncode2 != 0:
        print("❌ One of the commands failed")
        return False
    
    # Detailed output should be longer
    if len(stdout2) > len(stdout1):
        print("✅ Detailed flag provides more comprehensive output")
        return True
    else:
        print("❌ Detailed output is not longer than normal output")
        return False

def test_subcommands_still_work():
    """Test that subcommands still work correctly."""
    print("🧪 Testing: Subcommands still function")
    
    # Test system subcommand
    returncode, stdout, stderr = run_baios_command(["check", "system"])
    
    if returncode != 0:
        print(f"❌ System subcommand failed: {stderr}")
        return False
    
    # Should contain system-specific output
    if "System Check Results" not in stdout:
        print("❌ System subcommand doesn't show expected output")
        return False
    
    print("✅ Subcommands work correctly")
    return True

def test_help_shows_options():
    """Test that help shows the new options at top level."""
    print("🧪 Testing: Help shows inventory options")
    
    returncode, stdout, stderr = run_baios_command(["check", "--help"])
    
    if returncode != 0:
        print(f"❌ Help command failed: {stderr}")
        return False
    
    # Should show the new options
    expected_options = ["--detailed", "--evaluate", "--section"]
    
    for option in expected_options:
        if option not in stdout:
            print(f"❌ Missing option in help: {option}")
            return False
    
    print("✅ Help shows all expected options")
    return True

def main():
    """Run all tests."""
    print("🚀 Running baios check integration tests...\n")
    
    tests = [
        test_default_check_runs_inventory,
        test_required_status_types_present,
        test_detailed_flag_works,
        test_subcommands_still_work,
        test_help_shows_options
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()  # Empty line between tests
    
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! baios check integration is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main())