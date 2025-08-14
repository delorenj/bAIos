#!/usr/bin/env python3
"""
Bill The Coordinator - General coordination and orchestration agent.

Bill specializes in project coordination, task orchestration, and general
workflow management. He's the go-to agent for understanding how different
components work together and coordinating complex multi-step processes.
"""

from .base import Agent
from typing import Dict, Any
import json


class BillTheCoordinator(Agent):
    """
    Bill The Coordinator specializes in:
    - Project coordination and task orchestration
    - Workflow management and process optimization
    - Understanding system dependencies and relationships
    - Multi-agent coordination and communication
    - Resource allocation and priority management
    """
    
    def __init__(self):
        super().__init__(
            name="Bill The Coordinator",
            expertise="Project coordination, task orchestration, and workflow management",
            personality="Professional, organized, and strategic. Thinks in terms of dependencies, priorities, and efficient workflows."
        )
    
    def ask(self, question: str) -> str:
        """
        Answer coordination and orchestration questions.
        
        Bill can help with:
        - Task prioritization and dependency management
        - Workflow optimization
        - Resource coordination
        - Process documentation
        - Multi-step procedure guidance
        """
        question_lower = question.lower()
        
        # Workflow and process questions
        if any(word in question_lower for word in ["workflow", "process", "steps", "order", "sequence"]):
            return self._handle_workflow_question(question)
        
        # Coordination and dependency questions
        elif any(word in question_lower for word in ["coordinate", "manage", "organize", "dependency", "dependencies"]):
            return self._handle_coordination_question(question)
        
        # Priority and resource questions  
        elif any(word in question_lower for word in ["priority", "prioritize", "resource", "allocation", "schedule"]):
            return self._handle_priority_question(question)
        
        # Project structure questions
        elif any(word in question_lower for word in ["structure", "architecture", "organization", "layout"]):
            return self._handle_structure_question(question)
        
        # General coordination advice
        else:
            return self._handle_general_coordination(question)
    
    def _handle_workflow_question(self, question: str) -> str:
        """Handle questions about workflows and processes."""
        system_info = self.get_system_info()
        
        return f"""🎯 **Bill The Coordinator** here!

For workflow and process management, I recommend following these coordination principles:

**📋 Process Design:**
1. **Identify Dependencies** - Map out what needs what
2. **Define Clear Steps** - Break complex tasks into manageable pieces  
3. **Establish Checkpoints** - Verify completion before moving forward
4. **Plan for Failures** - Have rollback and recovery procedures

**🔄 Workflow Best Practices:**
- Start with the end goal and work backward
- Parallelize independent tasks when possible
- Use staging environments for validation
- Document each step for repeatability

**🖥️ Current System Context:**
- Platform: {system_info['platform']} ({system_info['architecture']})
- Working Directory: {system_info['current_dir']}
- User: {system_info['user']}

**💡 Specific to your question:** "{question}"

Based on your environment, I'd suggest breaking this into smaller, testable steps with clear success criteria. Would you like me to help you create a specific action plan?"""

    def _handle_coordination_question(self, question: str) -> str:
        """Handle coordination and dependency management questions."""
        return f"""🤝 **Bill The Coordinator** speaking!

For coordination and dependency management:

**🎯 Key Coordination Strategies:**
1. **Dependency Mapping** - Understand what depends on what
2. **Resource Inventory** - Know what you have available
3. **Communication Channels** - Establish clear information flow
4. **Conflict Resolution** - Handle competing requirements

**⚡ Management Techniques:**
- Use dependency graphs to visualize relationships
- Implement staged rollouts for complex changes
- Establish clear ownership and responsibility
- Create feedback loops for continuous improvement

**📊 For your specific question:** "{question}"

I can help you identify the key dependencies and create a coordination plan. What specific components or processes are you trying to coordinate?"""

    def _handle_priority_question(self, question: str) -> str:
        """Handle priority and resource allocation questions."""
        return f"""📈 **Bill The Coordinator** here to help with priorities!

**🎯 Priority Management Framework:**

**High Priority (🔴 Critical):**
- Security vulnerabilities
- System-breaking issues  
- Blocking dependencies for other work
- Customer-facing problems

**Medium Priority (🟡 Important):**
- Performance optimizations
- Feature enhancements
- Technical debt reduction
- Process improvements

**Low Priority (🟢 Nice to Have):**
- Documentation updates
- Code refactoring
- Experimental features
- Quality of life improvements

**📋 Resource Allocation Strategy:**
1. **Assess Available Resources** - Time, people, tools
2. **Map Resource Requirements** - What each task needs
3. **Optimize for Bottlenecks** - Address limiting factors first
4. **Plan for Contingencies** - Have backup options

**💡 Regarding:** "{question}"

Would you like me to help you create a specific prioritization matrix for your situation?"""

    def _handle_structure_question(self, question: str) -> str:
        """Handle project structure and organization questions."""
        system_info = self.get_system_info()
        
        return f"""🏗️ **Bill The Coordinator** on structure and organization!

**📁 Recommended Project Structure:**

```
project/
├── docs/              # Documentation and specifications
├── src/               # Source code
├── tests/             # Test suites
├── config/            # Configuration files
├── scripts/           # Utility and automation scripts
├── .github/           # CI/CD workflows
└── tools/             # Development tools and utilities
```

**🎯 Organizational Principles:**
1. **Separation of Concerns** - Each directory has a clear purpose
2. **Consistent Naming** - Use clear, descriptive names
3. **Logical Grouping** - Related items stay together
4. **Scalable Structure** - Can grow without reorganization

**💻 Your Current Environment:**
- Working in: {system_info['current_dir']}
- Platform: {system_info['platform']}
- Home: {system_info['home_dir']}

**🔍 For your question:** "{question}"

I can help you design a specific organizational structure for your project. What type of project are you working on?"""

    def _handle_general_coordination(self, question: str) -> str:
        """Handle general coordination questions."""
        return f"""🎪 **Bill The Coordinator** at your service!

I specialize in orchestrating complex processes and keeping projects on track. Here's my general coordination philosophy:

**🎯 Core Coordination Principles:**
- **Visibility** - Make status and progress transparent
- **Communication** - Keep all stakeholders informed
- **Flexibility** - Adapt to changing requirements
- **Documentation** - Record decisions and processes

**⚡ My Expertise Areas:**
- Task dependency management
- Resource allocation and scheduling  
- Process optimization
- Multi-team coordination
- Risk assessment and mitigation

**💭 Your Question:** "{question}"

I'd be happy to help you break this down into manageable, coordinated steps. Could you provide more context about what you're trying to accomplish?

**🤝 Working with Other Agents:**
- **Shelldon** - For command-line and scripting coordination
- **MiseMaster** - For development environment orchestration  
- **TzviTheWindowsWizard** - For Windows-specific coordination
- Together we can handle complex multi-domain challenges!"""