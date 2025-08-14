#!/usr/bin/env python3
"""
Manual validation checklist for bAIos agent system.

This provides a step-by-step checklist for manual validation of the agent system
as outlined in Checkpoint 2 requirements.
"""

import subprocess
import sys
from pathlib import Path

# Add the baios package to path
CLI_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(CLI_PATH))

def run_command_interactive(cmd_args, description):
    """Run a command and show the results interactively."""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {description}")
    print('='*60)
    
    cmd_str = "baios " + " ".join(cmd_args)
    print(f"💻 Running: {cmd_str}")
    
    cmd = ["python", "-m", "baios.main"] + cmd_args
    
    try:
        result = subprocess.run(cmd, cwd=CLI_PATH, timeout=30)
        
        if result.returncode == 0:
            print("✅ Command completed successfully")
            return True
        else:
            print(f"❌ Command failed with return code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out")
        return False
    except Exception as e:
        print(f"💥 Command crashed: {e}")
        return False

def interactive_checklist():
    """Run the interactive validation checklist."""
    print("🤖 bAIos Agent System Manual Validation Checklist")
    print("=" * 60)
    print("\nThis checklist will help you manually validate the agent system")
    print("according to Checkpoint 2 requirements.\n")
    
    input("Press Enter to begin validation...")
    
    checklist_items = [
        {
            "id": "1",
            "description": "Check that 'baios agent list' command exists",
            "cmd": ["agent", "list"],
            "expected": "Should show list of agents without errors"
        },
        {
            "id": "2", 
            "description": "Verify all four required agents are listed",
            "cmd": ["agent", "list"],
            "expected": "Should show: BillTheCoordinator, MiseMaster, TzviTheWindowsWizard, Shelldon"
        },
        {
            "id": "3",
            "description": "Test Shelldon shell question (exact Checkpoint 2 test)",
            "cmd": ["agent", "ask", "Shelldon", "Is zsh my default shell?"],
            "expected": "Shelldon should respond with shell information"
        },
        {
            "id": "4",
            "description": "Test BillTheCoordinator responds to questions",
            "cmd": ["agent", "ask", "BillTheCoordinator", "What is your role?"],
            "expected": "Should get a response about coordination/management"
        },
        {
            "id": "5",
            "description": "Test MiseMaster responds to questions",
            "cmd": ["agent", "ask", "MiseMaster", "What tools do you manage?"],
            "expected": "Should respond about mise/tool management"
        },
        {
            "id": "6",
            "description": "Test TzviTheWindowsWizard responds",
            "cmd": ["agent", "ask", "TzviTheWindowsWizard", "What Windows tools can you help with?"],
            "expected": "Should respond about Windows-specific tools"
        },
        {
            "id": "7",
            "description": "Test error handling with invalid agent",
            "cmd": ["agent", "ask", "NonExistentAgent", "Hello"],
            "expected": "Should fail gracefully with helpful error message"
        }
    ]
    
    results = []
    
    for item in checklist_items:
        print(f"\n📋 Step {item['id']}: {item['description']}")
        print(f"📝 Expected: {item['expected']}")
        
        input(f"\nPress Enter to run: baios {' '.join(item['cmd'])}")
        
        success = run_command_interactive(item['cmd'], item['description'])
        
        # Ask user for manual validation
        print(f"\n❓ Did the command work as expected?")
        print(f"   Expected: {item['expected']}")
        
        while True:
            user_input = input("   (y)es / (n)o / (s)kip: ").lower().strip()
            if user_input in ['y', 'yes']:
                manual_success = True
                break
            elif user_input in ['n', 'no']:
                manual_success = False
                break
            elif user_input in ['s', 'skip']:
                manual_success = None
                break
            else:
                print("   Please enter 'y', 'n', or 's'")
        
        results.append({
            "id": item['id'],
            "description": item['description'], 
            "command_success": success,
            "manual_validation": manual_success
        })
        
        if manual_success is True:
            print("   ✅ Manual validation: PASSED")
        elif manual_success is False:
            print("   ❌ Manual validation: FAILED")
        else:
            print("   ⏭️  Manual validation: SKIPPED")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 VALIDATION SUMMARY")
    print('='*60)
    
    passed = sum(1 for r in results if r['manual_validation'] is True)
    failed = sum(1 for r in results if r['manual_validation'] is False)
    skipped = sum(1 for r in results if r['manual_validation'] is None)
    
    print(f"Total checks: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")  
    print(f"⏭️  Skipped: {skipped}")
    
    if failed == 0 and passed > 0:
        print(f"\n🎉 All validated checks passed! Agent system appears to be working.")
        success_rate = 100.0
    else:
        success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        print(f"\n⚠️  Success rate: {success_rate:.1f}% - Some issues may need attention.")
    
    print(f"\n📋 Detailed Results:")
    for result in results:
        status = "✅ PASS" if result['manual_validation'] is True else "❌ FAIL" if result['manual_validation'] is False else "⏭️  SKIP"
        print(f"   {result['id']}. {status} - {result['description']}")
    
    return failed == 0 and passed > 0

def main():
    """Main function."""
    try:
        success = interactive_checklist()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        return 130

if __name__ == "__main__":
    exit(main())