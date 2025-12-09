#!/usr/bin/env python3
"""
CTO/Architect Agent Status Tool
Single interface to query project status from .ai-knowledge-base.json
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def load_kb():
    """Load knowledge base"""
    kb_file = Path(".ai-knowledge-base.json")
    if not kb_file.exists():
        print("❌ Knowledge base not found. Creating initial file...")
        create_initial_kb()
        return load_kb()

    with open(kb_file, "r") as f:
        return json.load(f)


def create_initial_kb():
    """Create initial knowledge base"""
    kb = {
        "version": "1.0",
        "last_updated": datetime.now().isoformat(),
        "project": {
            "name": "Canada Immigration OS",
            "status": "Phase 1 - Foundation Hardening",
            "completion_percentage": 15,
            "current_phase": "Phase 1",
        },
        "agents": {},
        "tasks": {"completed": [], "in_progress": [], "pending": [], "blocked": []},
        "decisions": [],
        "architecture": {"current_state": "Phase 1 foundation", "gaps": []},
        "metrics": {},
    }
    with open(".ai-knowledge-base.json", "w") as f:
        json.dump(kb, f, indent=2)


def show_status():
    """Show overall project status"""
    kb = load_kb()
    project = kb["project"]
    tasks = kb["tasks"]

    print("=" * 60)
    print(f"📊 {project['name']} - Project Status")
    print("=" * 60)
    print(f"\nPhase: {project['status']}")
    print(f"Completion: {project['completion_percentage']}%")
    print(f"\n✅ Completed Tasks: {len(tasks['completed'])}")
    print(f"🔄 In Progress: {len(tasks['in_progress'])}")
    print(f"📋 Pending: {len(tasks['pending'])}")
    print(f"⏸️  Blocked: {len(tasks['blocked'])}")

    if tasks["completed"]:
        print("\n✅ Recently Completed:")
        for task in tasks["completed"][-5:]:
            print(f"  - {task.get('title', 'Unknown')} ({task.get('agent', 'Unknown')})")

    if tasks["in_progress"]:
        print("\n🔄 In Progress:")
        for task in tasks["in_progress"]:
            print(f"  - {task.get('title', 'Unknown')} ({task.get('agent', 'Unknown')})")

    if tasks["pending"]:
        print("\n📋 Next Priority Tasks:")
        p0_tasks = [t for t in tasks["pending"] if t.get("priority") == "P0"]
        for task in p0_tasks[:5]:
            print(f"  - {task.get('title', 'Unknown')} ({task.get('agent', 'Unknown')})")


def show_agents():
    """Show agent status"""
    kb = load_kb()
    agents = kb["agents"]

    print("=" * 60)
    print("👥 Agent Status")
    print("=" * 60)

    for name, data in agents.items():
        status_icon = "🟢" if data.get("status") == "active" else "🔴"
        current_task = data.get("current_task", "None")
        completed = len(data.get("completed_tasks", []))

        print(f"\n{status_icon} {name}")
        print(f"   Role: {data.get('role', 'Unknown')}")
        print(f"   Status: {data.get('status', 'unknown')}")
        print(f"   Current Task: {current_task}")
        print(f"   Completed Tasks: {completed}")
        if data.get("last_activity"):
            print(f"   Last Activity: {data['last_activity']}")


def show_tasks():
    """Show all tasks"""
    kb = load_kb()
    tasks = kb["tasks"]

    print("=" * 60)
    print("📋 All Tasks")
    print("=" * 60)

    if tasks["completed"]:
        print("\n✅ Completed:")
        for task in tasks["completed"]:
            print(f"  - {task.get('title', 'Unknown')} ({task.get('agent', 'Unknown')})")

    if tasks["in_progress"]:
        print("\n🔄 In Progress:")
        for task in tasks["in_progress"]:
            print(f"  - {task.get('title', 'Unknown')} ({task.get('agent', 'Unknown')})")

    if tasks["pending"]:
        print("\n📋 Pending:")
        for task in tasks["pending"]:
            priority = task.get("priority", "medium")
            print(
                f"  - [{priority}] {task.get('title', 'Unknown')} ({task.get('agent', 'Unknown')})"
            )

    if tasks["blocked"]:
        print("\n⏸️  Blocked:")
        for task in tasks["blocked"]:
            print(f"  - {task.get('title', 'Unknown')} ({task.get('agent', 'Unknown')})")


def show_gaps():
    """Show project gaps"""
    kb = load_kb()
    gaps = kb.get("architecture", {}).get("gaps", [])

    print("=" * 60)
    print("🔍 Project Gaps")
    print("=" * 60)

    if gaps:
        for i, gap in enumerate(gaps, 1):
            print(f"{i}. {gap}")
    else:
        print("No gaps identified.")


def update_task_status(task_id, status, agent=None):
    """Update task status in knowledge base"""
    kb = load_kb()

    # Find task in any list
    task = None
    source_list = None

    for list_name in ["completed", "in_progress", "pending", "blocked"]:
        for t in kb["tasks"][list_name]:
            if t.get("id") == task_id:
                task = t
                source_list = list_name
                break
        if task:
            break

    if not task:
        print(f"❌ Task {task_id} not found")
        return

    # Remove from current list
    kb["tasks"][source_list].remove(task)

    # Update task
    task["status"] = status
    task["updated_at"] = datetime.now().isoformat()

    # Add to appropriate list
    if status == "completed":
        task["completed_at"] = datetime.now().isoformat()
        kb["tasks"]["completed"].append(task)
        # Update agent
        if agent and agent in kb["agents"]:
            if "completed_tasks" not in kb["agents"][agent]:
                kb["agents"][agent]["completed_tasks"] = []
            kb["agents"][agent]["completed_tasks"].append(task_id)
            kb["agents"][agent]["current_task"] = None
            kb["agents"][agent]["last_activity"] = datetime.now().isoformat()
    elif status == "in_progress":
        kb["tasks"]["in_progress"].append(task)
        if agent and agent in kb["agents"]:
            kb["agents"][agent]["current_task"] = task_id
            kb["agents"][agent]["last_activity"] = datetime.now().isoformat()
    elif status == "blocked":
        kb["tasks"]["blocked"].append(task)
    else:
        kb["tasks"]["pending"].append(task)

    # Update metrics
    kb["metrics"]["tasks_completed"] = len(kb["tasks"]["completed"])
    kb["last_updated"] = datetime.now().isoformat()

    # Save
    with open(".ai-knowledge-base.json", "w") as f:
        json.dump(kb, f, indent=2)

    print(f"✅ Updated task {task_id} to {status}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_status()
    elif sys.argv[1] == "status":
        show_status()
    elif sys.argv[1] == "agents":
        show_agents()
    elif sys.argv[1] == "tasks":
        show_tasks()
    elif sys.argv[1] == "gaps":
        show_gaps()
    elif sys.argv[1] == "update" and len(sys.argv) >= 4:
        task_id = sys.argv[2]
        status = sys.argv[3]
        agent = sys.argv[4] if len(sys.argv) > 4 else None
        update_task_status(task_id, status, agent)
    else:
        print("Usage:")
        print("  python3 scripts/cto-status.py          # Show status")
        print("  python3 scripts/cto-status.py status    # Show status")
        print("  python3 scripts/cto-status.py agents    # Show agents")
        print("  python3 scripts/cto-status.py tasks    # Show tasks")
        print("  python3 scripts/cto-status.py gaps      # Show gaps")
        print("  python3 scripts/cto-status.py update <task_id> <status> [agent]  # Update task")
