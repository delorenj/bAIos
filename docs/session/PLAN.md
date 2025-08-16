# Session Goal

**IMPORTANT**: Don't work too far ahead without regularly demonstrating progress. There will be a number of prescribed check-in points where you will be asked to demonstrate some specific functionality or progress.

- [x] Checkpoint 1

A typer CLI app is executed: `baios check`

It prints out a list of of all the items in the inventory file, with a status for each item. The status can be one of the following:

- Complete: This means it is done and you can move on to the next item.
- Failed (Critical): This means it failed and you need to fix it.
- Failed (Non-Critical): This means it failed but it's optional, so you can continue with the next item
- Not Started (Required): This means it has not been started yet, but it is required for the session to be complete.
- Note: This means it is not required for the session to be complete, but it is a note for the user.

- [x] Checkpoint 2

A typer CLI app is executed: `baios agent list`

There is a list of all the available agents. It doesn't matter which one we test, as long as there is at least one agent that is available.

```sh
baios agent list

BillTheCoordinator
MiseMaster
TzviTheWindowsWizard
Shelldon

baios agent ask Shelldon "Is zsh my default shell?"

Shelldon: Yes, zsh is your default shell.
```

- [ ] Checkpoint 3

We're gonna pause for this checkpoint to make sure we're on the same page in terms of our GDK agents. We need to ensure we build a solid base agent that can be extended to become the agents in this system. We should show the agent has the capability to interact with the filesystem by, let's say, writing a simple script or something in response to a cli `ask` query

- [ ] Checkpoint 4

There is now a complete list of agents that are available, and they are all working correctly. The agents are able to communicate with each other and with the coordinator agent. The coordinator agent is able to manage the overall process and ensure that everything is done in the correct order.

Every task is now associated with one and only one agent

The coordinator agent now have each step registered in the correct order dictated by the dependency graph

## Instructions

- [1] Do a deep analysis of the transcription of the live onboarding session to extract a comprehensive list of every single action done, app installed, configuration copied, etc. This should follow the format of the docs/INVENTORY.md file where I tried to recall everything by memory as well as fill in all the requirements we never even got to. When you have the list, combine it with the docs/INVENTORY.md file.

- [2] Once the list is complete, spawn a swarm of researchers in parallel to research each item in the list and find a link to the official installation instructions (if applicable. Some steps may just say `install python with mise` which would not require doc links). The link to instructions or extra data found by the researchers is to be noted in the inventory file and associated with the item.

> Both 3's **Can be done in paralell**

- [3] Next, the items in the list need to be divided up into non-overlapping groups - each group representing an agent responsible for items of that group. The agents will have deep knowledge of that particular domain. We need to be careful to not overload the agent with too many non-related domains, since the goal is to minimize context while we maximize utility. If a category becomes too large, we need to reanalyze the items to see where we can split it further.

- [3] An hierarchical swarm of agents should be spawned to build a dependency graph of the items that we need to ensure we execute the steps in the correct order. The agents will be responsible for analyzing the items in their group and determining if there are any dependencies between them. If there are, they will create a directed edge from the dependent item to the item it depends on.

- [3] Spawn a swarm of [google adk](https://github.com/google/adk-python) specialist agents to build one agent per non-overlapping group of items.
  - The agents will work in a hierarchical topology where they each have MCP tools that enable them manage the client's computer and install software, copy files, configure settings, etc.
  - Each agent will report back to the main coordinator agent that will be responsible for managing the overall process and ensuring that everything is done in the correct order.
  - The coordinator agent will also work with the client to ask for any passwords needed or questions that arise during the process.
  - Before the coordinator agent declares an item is complete, it will enlist the help of a QA agent that verifies against a strict set of acceptance criteria.
  - The coordinator will keep track of the progress with a simple checklist that will be updated by the agents as they complete their tasks.
  - When an agent declares all tasks and subtasks are complete the coordinator will ask the QA agent to do its verification and the coordinator makes the final decision on whether the item is complete or not.
  - If not satisfactory, the coordinator will hand it back to the agent for further work.
  - The coordinator will also be responsible for invoking the human-in-the-loop protocol if an agent has spent too long on a task or if the agent has questions that need answering.
