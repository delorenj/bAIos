"""
Simple Integration Test
=======================

Basic integration test that focuses on our custom components without external dependencies.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from orchestrator.checklist_manager import ChecklistManager, ChecklistStatus, ChecklistPriority
from agents.stub_agent import StubAgentFactory, StubAgent, StubQAExpertAgent
from schemas import AgentRequest, QAResult
from orchestrator.task_scheduler import TaskScheduler  
from orchestrator.failure_tracker import FailureTracker

logging.basicConfig(level=logging.INFO)


def test_checklist_manager():
    """Test checklist manager core functionality."""
    print("🗂️  Testing Checklist Manager")
    print("-" * 40)
    
    try:
        # Create checklist manager
        manager = ChecklistManager("test_session")
        
        print(f"   ✅ Categories: {len(manager.categories)}")
        print(f"   ✅ Items: {len(manager.items)}")
        print(f"   ✅ Execution order: {len(manager.execution_order)}")
        
        # Test ready items
        ready_items = manager.get_ready_items()
        print(f"   ✅ Ready items: {len(ready_items)}")
        
        # Test progress
        progress = manager.get_progress_summary()
        print(f"   ✅ Initial progress: {progress['progress_percentage']:.1f}%")
        
        # Update an item
        if ready_items:
            first_item = ready_items[0]
            manager.update_item_status(first_item.id, ChecklistStatus.COMPLETED)
            
            # Check progress after update
            new_progress = manager.get_progress_summary()
            print(f"   ✅ Updated progress: {new_progress['progress_percentage']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


async def test_stub_agents():
    """Test stub agent functionality."""
    print("\\n🤖 Testing Stub Agents")
    print("-" * 40)
    
    try:
        factory = StubAgentFactory(default_success_rate=0.9)
        
        # Test different agent types
        agent_types = ["researcher", "installer", "shell_master", "qa_expert"]
        results = []
        
        for agent_type in agent_types:
            print(f"   Testing {agent_type}...")
            
            agent = factory.create_stub_agent(agent_type)
            request = AgentRequest(
                agent_type=agent_type,
                task_description=f"Test {agent_type} task",
                context={"test": True}
            )
            
            result = await agent._execute_task(request)
            
            if agent_type == "qa_expert":
                success = result.validation_passed if isinstance(result, QAResult) else False
                print(f"      QA Result: {'PASS' if success else 'FAIL'}")
            else:
                success = result.get("success", False) if isinstance(result, dict) else False
                print(f"      Task Result: {'SUCCESS' if success else 'FAILED'}")
            
            results.append(success)
        
        success_rate = sum(results) / len(results)
        print(f"   ✅ Overall success rate: {success_rate:.1f}")
        
        return success_rate > 0.5
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_task_scheduler():
    """Test task scheduler."""
    print("\\n📅 Testing Task Scheduler")
    print("-" * 40)
    
    try:
        scheduler = TaskScheduler()
        
        # Create test tasks
        request1 = AgentRequest(
            agent_type="researcher",
            task_description="Research task",
            context={}
        )
        request1.task_id = "task1"
        
        request2 = AgentRequest(
            agent_type="installer", 
            task_description="Install task",
            context={}
        )
        request2.task_id = "task2"
        
        # Schedule tasks
        id1 = scheduler.schedule_task(request1)
        id2 = scheduler.schedule_task(request2, dependencies=[id1])
        
        print(f"   ✅ Scheduled tasks: {id1}, {id2}")
        
        # Check ready tasks
        ready = scheduler.get_ready_tasks()
        print(f"   ✅ Ready tasks: {len(ready)}")
        
        # Check dependencies
        deps = scheduler.dependency_graph[id2]
        print(f"   ✅ Task dependencies: {len(deps)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_failure_tracker():
    """Test failure tracker."""
    print("\\n📊 Testing Failure Tracker")
    print("-" * 40)
    
    try:
        tracker = FailureTracker(failure_threshold=3)
        
        # Record some failures
        for i in range(4):
            count = tracker.record_failure("test_task", "test_agent", f"Error {i}")
        
        print(f"   ✅ Recorded failures: {tracker.total_failures}")
        
        # Check if intervention is needed
        task_failure = tracker.task_failures["test_task"]
        print(f"   ✅ Intervention required: {task_failure.requires_human_intervention}")
        
        # Get failure report
        report = tracker.get_failure_report("test_task")
        print(f"   ✅ Failure report: {len(report.failure_reasons)} reasons")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


async def main():
    """Run all integration tests."""
    print("🚀 Simple Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Checklist Manager", test_checklist_manager()),
        ("Stub Agents", await test_stub_agents()),
        ("Task Scheduler", test_task_scheduler()),
        ("Failure Tracker", test_failure_tracker())
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        if result:
            passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED")
    
    print("\\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("⚠️  Some tests failed - check components above")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)