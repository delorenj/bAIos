"""
Test Runner
===========

Simple test runner to verify the orchestrator system functionality.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from orchestrator.checklist_manager import ChecklistManager, ChecklistStatus
from agents.stub_agent import StubAgentFactory, StubAgent
from schemas import AgentRequest

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def test_stub_agents():
    """Test stub agent functionality."""
    print("🧪 Testing Stub Agents")
    print("-" * 40)
    
    try:
        # Create stub agent factory
        factory = StubAgentFactory(default_success_rate=0.9)
        
        # Test different agent types
        agent_types = ["researcher", "installer", "shell_master", "qa_expert"]
        
        for agent_type in agent_types:
            print(f"\n Testing {agent_type} agent...")
            
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
            
            if agent_type == "qa_expert":
                print(f"   ✅ QA Validation: {'PASSED' if result.validation_passed else 'FAILED'}")
                print(f"   📊 Confidence: {result.confidence_score:.2f}")
            else:
                print(f"   ✅ Task Success: {result.get('success', False)}")
                print(f"   📝 Message: {result.get('message', 'No message')}")
            
            # Get metrics
            metrics = agent.get_stub_metrics()
            print(f"   📈 Executions: {metrics['execution_count']}")
        
        print("\n✅ Stub agent tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Stub agent tests failed: {str(e)}")
        logging.error(f"Stub agent test error: {e}")
        return False


def test_checklist_manager():
    """Test checklist manager functionality."""
    print("\n🗂️  Testing Checklist Manager")
    print("-" * 40)
    
    try:
        # Create checklist manager
        manager = ChecklistManager("test_session")
        
        # Verify initialization
        print(f"   📋 Categories loaded: {len(manager.categories)}")
        print(f"   📝 Total items: {len(manager.items)}")
        print(f"   🔄 Execution order: {len(manager.execution_order)} items")
        
        # Get ready items
        ready_items = manager.get_ready_items()
        print(f"   ✅ Ready to execute: {len(ready_items)} items")
        
        if ready_items:
            # Test updating item status
            first_item = ready_items[0]
            print(f"   🎯 Testing item: {first_item.name}")
            
            manager.update_item_status(
                first_item.id,
                ChecklistStatus.COMPLETED,
                "Test completion"
            )
            
            # Verify update
            updated_item = manager.items[first_item.id]
            print(f"   📊 Status updated: {updated_item.status}")
        
        # Get progress summary
        progress = manager.get_progress_summary()
        print(f"   📈 Progress: {progress['progress_percentage']:.1f}%")
        
        # Test category progress
        for cat_id in manager.categories:
            cat_progress = manager.get_category_progress(cat_id)
            print(f"   📂 {cat_progress['name']}: {cat_progress['progress_percentage']:.1f}% complete")
        
        print("\n✅ Checklist manager tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Checklist manager tests failed: {str(e)}")
        logging.error(f"Checklist manager test error: {e}")
        return False


def test_system_integration():
    """Test basic system integration."""
    print("\n🔗 Testing System Integration")
    print("-" * 40)
    
    try:
        # Test imports
        from orchestrator import RootOrchestrator, AgentFactory, TaskScheduler, FailureTracker
        from agents import BaseSpecializedAgent, ResearcherAgent, QAExpertAgent
        from schemas import ProvisioningRequest, ProvisioningResponse
        
        print("   ✅ All imports successful")
        
        # Test schema creation
        request = ProvisioningRequest(
            environment_spec_path="/test/spec.md",
            user_preferences={"test": True},
            dry_run=True
        )
        print("   ✅ Schema creation successful")
        
        # Test checklist integration
        manager = ChecklistManager("integration_test")
        factory = StubAgentFactory()
        
        print(f"   ✅ Integration components created")
        print(f"      - Checklist items: {len(manager.items)}")
        print(f"      - Agent factory ready: {len(factory.agent_success_rates)} agent types")
        
        print("\n✅ System integration tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ System integration tests failed: {str(e)}")
        logging.error(f"System integration test error: {e}")
        return False


async def main():
    """Main test runner."""
    print("🚀 WSL Orchestrator System - Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Run tests
    test_results.append(await test_stub_agents())
    test_results.append(test_checklist_manager())
    test_results.append(test_system_integration())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("-" * 20)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        return True
    else:
        print("❌ Some tests failed. Please check the logs.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)