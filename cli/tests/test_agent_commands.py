#!/usr/bin/env python3
"""
Comprehensive test suite for bAIos agent system functionality.

This test suite validates:
1. `baios agent list` shows all four agents as specified in Checkpoint 2
2. `baios agent ask Shelldon "Is zsh my default shell?"` returns proper response
3. All agents can respond to questions appropriately 
4. Integration testing for complete agent workflow
5. Error handling and edge cases
6. Performance and response time validation

Expected agents from Checkpoint 2:
- BillTheCoordinator
- MiseMaster  
- TzviTheWindowsWizard
- Shelldon

This test waits for implementation completion before executing tests.
"""

import subprocess
import sys
import time
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from unittest.mock import patch

# Add the baios package to path for testing
CLI_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(CLI_PATH))

class AgentTestSuite:
    """Comprehensive test suite for bAIos agent commands."""
    
    def __init__(self):
        self.required_agents = [
            "BillTheCoordinator",
            "MiseMaster", 
            "TzviTheWindowsWizard",
            "Shelldon"
        ]
        self.test_results = []
        self.performance_metrics = {}
        
    def run_baios_command(self, cmd_args: List[str], timeout: int = 30) -> Tuple[int, str, str]:
        """Run a baios command and return output with timing."""
        cmd = ["python", "-m", "baios.main"] + cmd_args
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=CLI_PATH,
                timeout=timeout
            )
            execution_time = time.time() - start_time
            self.performance_metrics[" ".join(cmd_args)] = execution_time
            
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            self.performance_metrics[" ".join(cmd_args)] = execution_time
            return -1, "", f"Command timed out after {timeout}s"
        except Exception as e:
            execution_time = time.time() - start_time
            self.performance_metrics[" ".join(cmd_args)] = execution_time
            return -1, "", str(e)

    def test_agent_list_command_exists(self) -> bool:
        """Test that the 'baios agent list' command exists and is accessible."""
        print("🧪 Testing: baios agent list command exists")
        
        # First check if 'agent' subcommand exists
        returncode, stdout, stderr = self.run_baios_command(["agent", "--help"])
        
        if returncode != 0:
            print(f"❌ 'baios agent' subcommand not implemented yet")
            print(f"   Return code: {returncode}")
            print(f"   STDERR: {stderr}")
            return False
        
        # Check if 'list' is mentioned in help
        if "list" not in stdout.lower():
            print(f"❌ 'list' command not found in agent help")
            return False
            
        print("✅ 'baios agent' subcommand exists and has list option")
        return True

    def test_agent_list_shows_all_agents(self) -> bool:
        """Test that 'baios agent list' shows all four required agents."""
        print("🧪 Testing: baios agent list shows all four agents")
        
        returncode, stdout, stderr = self.run_baios_command(["agent", "list"])
        
        if returncode != 0:
            print(f"❌ Command failed with return code {returncode}")
            print(f"   STDERR: {stderr}")
            return False
        
        # Check that all required agents are present
        missing_agents = []
        for agent in self.required_agents:
            if agent not in stdout:
                missing_agents.append(agent)
        
        if missing_agents:
            print(f"❌ Missing agents in output: {missing_agents}")
            print(f"   Available output:\n{stdout}")
            return False
        
        print(f"✅ All four required agents found: {', '.join(self.required_agents)}")
        return True

    def test_agent_ask_command_exists(self) -> bool:
        """Test that the 'baios agent ask' command exists."""
        print("🧪 Testing: baios agent ask command exists")
        
        # Check if 'ask' is in the agent help
        returncode, stdout, stderr = self.run_baios_command(["agent", "--help"])
        
        if returncode != 0:
            print(f"❌ Cannot access agent help")
            return False
            
        if "ask" not in stdout.lower():
            print(f"❌ 'ask' command not found in agent help")
            return False
            
        print("✅ 'baios agent ask' command exists")
        return True

    def test_shelldon_zsh_question(self) -> bool:
        """Test the specific Shelldon question from Checkpoint 2."""
        print("🧪 Testing: baios agent ask Shelldon 'Is zsh my default shell?'")
        
        returncode, stdout, stderr = self.run_baios_command([
            "agent", "ask", "Shelldon", "Is zsh my default shell?"
        ])
        
        if returncode != 0:
            print(f"❌ Command failed with return code {returncode}")
            print(f"   STDERR: {stderr}")
            return False
        
        # Should contain a response from Shelldon
        if "shelldon" not in stdout.lower():
            print(f"❌ No response from Shelldon found")
            print(f"   Output: {stdout}")
            return False
        
        # Should contain some shell-related information
        shell_keywords = ["zsh", "shell", "default", "yes", "no"]
        if not any(keyword in stdout.lower() for keyword in shell_keywords):
            print(f"❌ Response doesn't seem to be about shell information")
            print(f"   Output: {stdout}")
            return False
        
        print("✅ Shelldon responded appropriately to shell question")
        return True

    def test_all_agents_can_respond(self) -> bool:
        """Test that all agents can respond to questions."""
        print("🧪 Testing: All agents can respond to questions")
        
        test_questions = {
            "BillTheCoordinator": "What is your role?",
            "MiseMaster": "What tools do you manage?", 
            "TzviTheWindowsWizard": "What Windows tools can you help with?",
            "Shelldon": "What shell are we using?"
        }
        
        successful_responses = 0
        failed_agents = []
        
        for agent, question in test_questions.items():
            print(f"   Testing {agent}...")
            returncode, stdout, stderr = self.run_baios_command([
                "agent", "ask", agent, question
            ])
            
            if returncode != 0:
                print(f"   ❌ {agent} failed to respond (return code: {returncode})")
                failed_agents.append(agent)
                continue
                
            if not stdout.strip():
                print(f"   ❌ {agent} gave empty response")
                failed_agents.append(agent)
                continue
                
            if len(stdout.strip()) < 10:
                print(f"   ⚠️  {agent} gave very short response: {stdout.strip()}")
                
            successful_responses += 1
            print(f"   ✅ {agent} responded successfully")
        
        if failed_agents:
            print(f"❌ {len(failed_agents)} agents failed to respond: {failed_agents}")
            return False
            
        print(f"✅ All {successful_responses} agents responded successfully")
        return True

    def test_error_handling(self) -> bool:
        """Test error handling for invalid commands."""
        print("🧪 Testing: Error handling for invalid commands")
        
        test_cases = [
            # Invalid agent name
            (["agent", "ask", "NonExistentAgent", "Hello"], "Invalid agent"),
            # Missing question
            (["agent", "ask", "Shelldon"], "Missing question"),
            # Empty question
            (["agent", "ask", "Shelldon", ""], "Empty question"),
        ]
        
        successful_error_tests = 0
        
        for cmd_args, test_description in test_cases:
            print(f"   Testing: {test_description}")
            returncode, stdout, stderr = self.run_baios_command(cmd_args)
            
            # Should fail appropriately (non-zero return code)
            if returncode == 0:
                print(f"   ❌ Command should have failed but succeeded")
                continue
                
            # Should have informative error message
            error_output = stderr + stdout
            if len(error_output.strip()) < 5:
                print(f"   ⚠️  Error message very short: '{error_output.strip()}'")
                
            successful_error_tests += 1
            print(f"   ✅ {test_description} handled correctly")
        
        if successful_error_tests == len(test_cases):
            print(f"✅ All error handling tests passed")
            return True
        else:
            print(f"❌ {len(test_cases) - successful_error_tests} error handling tests failed")
            return False

    def test_agent_list_format(self) -> bool:
        """Test that agent list output is properly formatted."""
        print("🧪 Testing: Agent list output format")
        
        returncode, stdout, stderr = self.run_baios_command(["agent", "list"])
        
        if returncode != 0:
            print(f"❌ Command failed")
            return False
        
        # Should be clean, readable output
        lines = stdout.strip().split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if len(non_empty_lines) < len(self.required_agents):
            print(f"❌ Not enough content in output")
            return False
        
        # Each required agent should appear on its own line or in a clear format
        agents_found_in_lines = 0
        for line in non_empty_lines:
            for agent in self.required_agents:
                if agent in line:
                    agents_found_in_lines += 1
                    break
        
        if agents_found_in_lines >= len(self.required_agents):
            print(f"✅ Agent list format is clear and readable")
            return True
        else:
            print(f"❌ Agent list format unclear")
            return False

    def test_performance_requirements(self) -> bool:
        """Test that commands complete within reasonable time limits."""
        print("🧪 Testing: Performance requirements")
        
        # Agent list should be fast (< 5 seconds)
        list_time = self.performance_metrics.get("agent list", 0)
        if list_time > 5.0:
            print(f"❌ 'agent list' too slow: {list_time:.2f}s (should be < 5s)")
            return False
        
        # Agent ask should be reasonable (< 30 seconds)
        ask_times = [time for cmd, time in self.performance_metrics.items() 
                    if cmd.startswith("agent ask")]
        
        if ask_times:
            max_ask_time = max(ask_times)
            avg_ask_time = sum(ask_times) / len(ask_times)
            
            if max_ask_time > 30.0:
                print(f"❌ Agent ask too slow: {max_ask_time:.2f}s (should be < 30s)")
                return False
                
            print(f"✅ Performance OK - List: {list_time:.2f}s, Ask avg: {avg_ask_time:.2f}s")
        else:
            print(f"✅ Performance OK - List: {list_time:.2f}s")
        
        return True

    def test_integration_flow(self) -> bool:
        """Test complete integration flow: list agents, then ask questions."""
        print("🧪 Testing: Complete integration flow")
        
        # Step 1: List agents
        returncode, stdout, stderr = self.run_baios_command(["agent", "list"])
        if returncode != 0:
            print(f"❌ Step 1 failed: Cannot list agents")
            return False
        
        # Step 2: Extract first agent from list
        available_agents = []
        for agent in self.required_agents:
            if agent in stdout:
                available_agents.append(agent)
        
        if not available_agents:
            print(f"❌ Step 2 failed: No agents found in list")
            return False
        
        # Step 3: Ask question to first available agent
        test_agent = available_agents[0]
        returncode, stdout, stderr = self.run_baios_command([
            "agent", "ask", test_agent, "Can you help me?"
        ])
        
        if returncode != 0:
            print(f"❌ Step 3 failed: Cannot ask question to {test_agent}")
            return False
        
        if not stdout.strip():
            print(f"❌ Step 3 failed: Empty response from {test_agent}")
            return False
        
        print(f"✅ Integration flow successful with {test_agent}")
        return True

    def wait_for_implementation(self, max_wait_seconds: int = 300) -> bool:
        """Wait for agent commands to be implemented, with periodic checks."""
        print(f"⏳ Waiting for agent command implementation (max {max_wait_seconds}s)...")
        
        start_time = time.time()
        check_interval = 10  # Check every 10 seconds
        
        while time.time() - start_time < max_wait_seconds:
            # Check if agent subcommand exists
            returncode, stdout, stderr = self.run_baios_command(["agent", "--help"])
            
            if returncode == 0:
                print("✅ Agent commands are now available!")
                return True
            
            elapsed = int(time.time() - start_time)
            remaining = max_wait_seconds - elapsed
            print(f"   Still waiting... ({elapsed}s elapsed, {remaining}s remaining)")
            
            time.sleep(check_interval)
        
        print("❌ Timeout waiting for agent commands to be implemented")
        return False

    def run_all_tests(self, wait_for_implementation: bool = True) -> Dict:
        """Run all tests and return comprehensive results."""
        print("🚀 Starting comprehensive bAIos agent system tests...")
        print("=" * 60)
        
        # Wait for implementation if requested
        if wait_for_implementation:
            if not self.wait_for_implementation():
                return {
                    "success": False,
                    "error": "Agent commands not implemented within timeout",
                    "tests_run": 0,
                    "tests_passed": 0
                }
        
        # Define all tests
        tests = [
            ("Agent List Command Exists", self.test_agent_list_command_exists),
            ("Agent Ask Command Exists", self.test_agent_ask_command_exists), 
            ("Agent List Shows All Agents", self.test_agent_list_shows_all_agents),
            ("Agent List Format", self.test_agent_list_format),
            ("Shelldon Shell Question", self.test_shelldon_zsh_question),
            ("All Agents Respond", self.test_all_agents_can_respond),
            ("Error Handling", self.test_error_handling),
            ("Integration Flow", self.test_integration_flow),
            ("Performance Requirements", self.test_performance_requirements),
        ]
        
        # Run tests
        passed = 0
        failed = 0
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'=' * 60}")
            print(f"TEST: {test_name}")
            print('=' * 60)
            
            try:
                success = test_func()
                if success:
                    passed += 1
                    results.append({"name": test_name, "status": "PASSED"})
                else:
                    failed += 1
                    results.append({"name": test_name, "status": "FAILED"})
            except Exception as e:
                print(f"❌ Test {test_name} crashed: {e}")
                failed += 1
                results.append({"name": test_name, "status": "CRASHED", "error": str(e)})
        
        # Final results
        print(f"\n{'=' * 60}")
        print(f"🏁 FINAL RESULTS")
        print('=' * 60)
        print(f"📊 Tests: {len(tests)} total, {passed} passed, {failed} failed")
        print(f"🎯 Success Rate: {passed/len(tests)*100:.1f}%")
        
        if self.performance_metrics:
            print(f"\n📈 Performance Metrics:")
            for cmd, time_taken in self.performance_metrics.items():
                print(f"   {cmd}: {time_taken:.2f}s")
        
        print(f"\n📋 Test Details:")
        for result in results:
            status_emoji = "✅" if result["status"] == "PASSED" else "❌" if result["status"] == "FAILED" else "💥"
            print(f"   {status_emoji} {result['name']}: {result['status']}")
            if "error" in result:
                print(f"      Error: {result['error']}")
        
        return {
            "success": failed == 0,
            "tests_run": len(tests),
            "tests_passed": passed, 
            "tests_failed": failed,
            "success_rate": passed/len(tests)*100,
            "performance_metrics": self.performance_metrics,
            "detailed_results": results
        }


def main():
    """Main test execution."""
    test_suite = AgentTestSuite()
    results = test_suite.run_all_tests(wait_for_implementation=True)
    
    # Save results to file for later analysis
    results_file = CLI_PATH / "tests" / "agent_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    if results["success"]:
        print("🎉 All agent system tests passed!")
        return 0
    else:
        print("❌ Some agent system tests failed. Check output above.")
        return 1


if __name__ == "__main__":
    exit(main())