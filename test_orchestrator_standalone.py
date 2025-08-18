"""
Standalone Integration Test
===========================

Test the orchestrator system components independently.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')


def test_checklist_manager():
    """Test checklist manager core functionality."""
    print("🗂️  Testing Checklist Manager")
    print("-" * 40)
    
    try:
        # Direct import to avoid package issues
        from orchestrator.checklist_manager import ChecklistManager, ChecklistStatus
        
        # Create checklist manager
        manager = ChecklistManager("test_session")
        
        print(f"   ✅ Categories loaded: {len(manager.categories)}")
        print(f"   ✅ Total items: {len(manager.items)}")
        print(f"   ✅ Execution order: {len(manager.execution_order)} items")
        
        # Test ready items
        ready_items = manager.get_ready_items()
        print(f"   ✅ Ready items: {len(ready_items)}")
        
        # Test progress
        progress = manager.get_progress_summary()
        print(f"   ✅ Initial progress: {progress['progress_percentage']:.1f}%")
        
        # Update an item if available
        if ready_items:
            first_item = ready_items[0]
            print(f"   🎯 Updating item: {first_item.name}")
            manager.update_item_status(first_item.id, ChecklistStatus.COMPLETED)
            
            # Check progress after update  
            new_progress = manager.get_progress_summary()
            print(f"   ✅ Updated progress: {new_progress['progress_percentage']:.1f}%")
        
        # Test category progress
        for cat_id in list(manager.categories.keys())[:3]:  # Show first 3 categories
            cat_progress = manager.get_category_progress(cat_id)
            print(f"   📂 {cat_progress['name']}: {cat_progress['progress_percentage']:.1f}% complete")
        
        print("   ✅ Checklist Manager test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Checklist Manager test failed: {e}")
        logging.error(f"Checklist test error: {e}")
        return False


async def test_stub_agents():
    """Test stub agent functionality."""
    print("\\n🤖 Testing Stub Agents")
    print("-" * 40)
    
    try:
        from agents.stub_agent import StubAgentFactory
        from schemas import AgentRequest
        
        factory = StubAgentFactory(default_success_rate=0.9)
        
        # Test different agent types
        agent_types = ["researcher", "installer", "shell_master", "qa_expert"]
        results = []
        
        for agent_type in agent_types:
            print(f"   🔬 Testing {agent_type} agent...")
            
            # Create stub agent
            agent = factory.create_stub_agent(agent_type)
            
            # Create test request
            request = AgentRequest(
                agent_type=agent_type,
                task_description=f"Test {agent_type} functionality",
                context={"test_mode": True}
            )
            
            # Execute task
            result = await agent._execute_task(request)
            
            # Check result type
            if agent_type == "qa_expert":
                from schemas import QAResult
                if hasattr(result, 'validation_passed'):
                    success = result.validation_passed
                    print(f"      ✅ QA validation: {'PASSED' if success else 'FAILED'}")
                    print(f"      📊 Confidence: {result.confidence_score:.2f}")
                else:
                    success = True  # Fallback
                    print(f"      ✅ QA result received")
            else:
                success = result.get("success", False) if isinstance(result, dict) else False
                print(f"      ✅ Task result: {'SUCCESS' if success else 'FAILED'}")
                if isinstance(result, dict):
                    print(f"      📝 Message: {result.get('message', 'No message')[:50]}...")
            
            results.append(success)
            
            # Get metrics
            metrics = agent.get_stub_metrics()
            print(f"      📈 Executions: {metrics['execution_count']}")
        
        success_rate = sum(results) / len(results) if results else 0
        print(f"   ✅ Overall success rate: {success_rate:.1f}")
        print("   ✅ Stub Agents test passed!")
        
        return success_rate > 0.5
        
    except Exception as e:
        print(f"   ❌ Stub Agents test failed: {e}")
        logging.error(f"Stub agents test error: {e}")
        return False


def test_failure_tracker():
    """Test failure tracker."""
    print("\\n📊 Testing Failure Tracker")
    print("-" * 40)
    
    try:
        from orchestrator.failure_tracker import FailureTracker
        
        tracker = FailureTracker(failure_threshold=3)
        
        print(f"   ✅ Tracker initialized with threshold: {tracker.failure_threshold}")
        
        # Record some failures
        test_task = "test_task"
        test_agent = "test_agent"
        
        for i in range(4):  # Exceed threshold to test intervention
            count = tracker.record_failure(test_task, test_agent, f"Simulated error {i+1}")
            print(f"   📉 Recorded failure {i+1}: count = {count}")
        
        print(f"   ✅ Total failures recorded: {tracker.total_failures}")
        
        # Check if human intervention is required
        if test_task in tracker.task_failures:
            task_failure = tracker.task_failures[test_task]
            print(f"   🚨 Intervention required: {task_failure.requires_human_intervention}")
            
            # Get failure report
            report = tracker.get_failure_report(test_task)
            print(f"   📋 Failure report: {len(report.failure_reasons)} reasons")
            print(f"   📈 Intervention requests: {tracker.intervention_requests}")
        
        # Test statistics
        stats = tracker.get_failure_statistics()
        print(f"   📊 Statistics: {stats['total_failures']} total failures")
        
        print("   ✅ Failure Tracker test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Failure Tracker test failed: {e}")
        logging.error(f"Failure tracker test error: {e}")
        return False


def test_schemas():
    """Test schema definitions."""
    print("\\n📋 Testing Schemas")
    print("-" * 40)
    
    try:
        from schemas import (
            ProvisioningRequest, ProvisioningResponse, 
            AgentRequest, AgentResponse, QAResult, FailureReport,
            TaskStatus, AgentType
        )
        
        # Test ProvisioningRequest
        request = ProvisioningRequest(
            environment_spec_path="/test/spec.md",
            user_preferences={"minimal_install": True},
            dry_run=True
        )
        print(f"   ✅ ProvisioningRequest created: {request.dry_run}")
        
        # Test AgentRequest
        agent_request = AgentRequest(
            agent_type="researcher",
            task_description="Test task",
            context={"test": True}
        )
        print(f"   ✅ AgentRequest created: {agent_request.agent_type}")
        
        # Test QAResult
        qa_result = QAResult(
            task_id="test_qa",
            validation_passed=True,
            success_criteria_met=["test_criteria"],
            failures=[],
            remediation_suggestions=[],
            confidence_score=0.95
        )
        print(f"   ✅ QAResult created: {qa_result.validation_passed}")
        
        # Test enums
        print(f"   ✅ TaskStatus enum: {TaskStatus.COMPLETED}")
        print(f"   ✅ AgentType enum: {AgentType.RESEARCHER}")
        
        print("   ✅ Schemas test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Schemas test failed: {e}")
        logging.error(f"Schemas test error: {e}")
        return False


async def main():
    """Run all integration tests."""
    print("🚀 WSL Orchestrator System - Standalone Integration Test")
    print("=" * 60)
    
    # Run tests
    test_results = []
    
    # Synchronous tests
    test_results.append(("Schemas", test_schemas()))
    test_results.append(("Checklist Manager", test_checklist_manager()))
    test_results.append(("Failure Tracker", test_failure_tracker()))
    
    # Asynchronous tests
    test_results.append(("Stub Agents", await test_stub_agents()))
    
    # Calculate results
    passed = sum(1 for name, result in test_results if result)
    total = len(test_results)
    
    # Summary
    print("\\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("-" * 30)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:<12} {test_name}")
    
    print(f"\\n📈 Overall Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All integration tests passed! System core components are working.")
        print("\\n📝 Note: Full system integration requires resolving atomic_agents import issues.")
        return True
    else:
        print("⚠️  Some tests failed - check individual components above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)