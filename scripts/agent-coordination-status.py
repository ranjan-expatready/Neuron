#!/usr/bin/env python3
"""
Agent Coordination Status Script
Shows current agent assignments, work status, and coordination activity
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def load_knowledge_base():
    """Load the knowledge base file"""
    kb_path = Path(__file__).parent.parent / ".ai-knowledge-base.json"
    if not kb_path.exists():
        print("Error: .ai-knowledge-base.json not found")
        sys.exit(1)

    with open(kb_path, "r") as f:
        return json.load(f)


def format_timestamp(ts):
    """Format ISO timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ts


def show_active_assignments(kb):
    """Show currently active agent assignments"""
    coordination = kb.get("agent_coordination", {})
    assignments = coordination.get("active_assignments", [])

    if not assignments:
        print("No active assignments")
        return

    print("\n" + "=" * 70)
    print("ACTIVE AGENT ASSIGNMENTS")
    print("=" * 70)

    for assign in assignments:
        print(f"\n📋 Assignment ID: {assign.get('id', 'N/A')}")
        print(f"   Assigned By: {assign.get('assigned_by', 'N/A')}")
        print(f"   Assigned To: {assign.get('assigned_to', 'N/A')}")
        print(f"   Task: {assign.get('task', 'N/A')}")
        print(f"   Status: {assign.get('status', 'N/A').upper()}")

        if assign.get("progress"):
            print(f"   Progress: {assign.get('progress')}%")

        if assign.get("started_at"):
            print(f"   Started: {format_timestamp(assign.get('started_at'))}")

        if assign.get("assigned_at"):
            print(f"   Assigned: {format_timestamp(assign.get('assigned_at'))}")

        if assign.get("files_modified"):
            print(f"   Files Modified: {', '.join(assign.get('files_modified', []))}")

        if assign.get("dependencies"):
            print(f"   Dependencies: {', '.join(assign.get('dependencies', []))}")

        if assign.get("waiting_for"):
            print(f"   ⏳ Waiting For: {assign.get('waiting_for')}")


def show_coordination_log(kb, limit=10):
    """Show recent coordination activity"""
    coordination = kb.get("agent_coordination", {})
    log = coordination.get("coordination_log", [])

    if not log:
        print("\nNo coordination activity logged")
        return

    print("\n" + "=" * 70)
    print(f"RECENT COORDINATION ACTIVITY (Last {min(limit, len(log))} events)")
    print("=" * 70)

    for event in log[-limit:]:
        event_type = event.get("event", "unknown")
        timestamp = format_timestamp(event.get("timestamp", ""))

        if event_type == "assignment":
            print(f"\n📤 {timestamp} - ASSIGNMENT")
            print(f"   From: {event.get('from', 'N/A')}")
            print(f"   To: {event.get('to', 'N/A')}")
            print(f"   Task: {event.get('task', 'N/A')}")
            if event.get("details"):
                print(f"   Details: {event.get('details')}")

        elif event_type == "work_started":
            print(f"\n▶️  {timestamp} - WORK STARTED")
            print(f"   Agent: {event.get('agent', 'N/A')}")
            print(f"   Task: {event.get('task', 'N/A')}")
            if event.get("details"):
                print(f"   Details: {event.get('details')}")
            if event.get("files_modified"):
                print(f"   Files: {', '.join(event.get('files_modified', []))}")

        elif event_type == "progress_update":
            print(f"\n📊 {timestamp} - PROGRESS UPDATE")
            print(f"   Agent: {event.get('agent', 'N/A')}")
            print(f"   Task: {event.get('task', 'N/A')}")
            print(f"   Progress: {event.get('progress', 0)}%")
            if event.get("details"):
                print(f"   Details: {event.get('details')}")

        elif event_type == "work_completed":
            print(f"\n✅ {timestamp} - WORK COMPLETED")
            print(f"   Agent: {event.get('agent', 'N/A')}")
            print(f"   Task: {event.get('task', 'N/A')}")
            if event.get("files_created"):
                print(f"   Files Created: {', '.join(event.get('files_created', []))}")

        elif event_type == "dependency_ready":
            print(f"\n🔓 {timestamp} - DEPENDENCY READY")
            print(f"   Agent: {event.get('agent', 'N/A')}")
            print(f"   Task: {event.get('task', 'N/A')}")
            print(f"   Details: {event.get('details', 'N/A')}")


def show_agent_status(kb):
    """Show current status of all agents"""
    agents = kb.get("agents", {})
    coordination = kb.get("agent_coordination", {})
    agent_status = coordination.get("agent_status", {})

    print("\n" + "=" * 70)
    print("AGENT STATUS")
    print("=" * 70)

    for agent_name, agent_info in agents.items():
        print(f"\n🤖 {agent_name}")
        print(f"   Role: {agent_info.get('role', 'N/A')}")
        print(f"   Status: {agent_info.get('status', 'N/A').upper()}")

        if agent_info.get("current_task"):
            print(f"   Current Task: {agent_info.get('current_task')}")

        # Check coordination status
        coord_status = agent_status.get(agent_name, {})
        if coord_status.get("current_role"):
            print(f"   Coordination Role: {coord_status.get('current_role')}")

        if coord_status.get("progress"):
            print(f"   Progress: {coord_status.get('progress')}%")

        if agent_info.get("last_activity"):
            print(f"   Last Activity: {format_timestamp(agent_info.get('last_activity'))}")


def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = "all"

    kb = load_knowledge_base()

    if command == "assignments" or command == "all":
        show_active_assignments(kb)

    if command == "log" or command == "all":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 10
        show_coordination_log(kb, limit)

    if command == "agents" or command == "all":
        show_agent_status(kb)

    if command not in ["assignments", "log", "agents", "all"]:
        print(
            "Usage: python3 agent-coordination-status.py [assignments|log|agents|all] [log_limit]"
        )
        print("\nCommands:")
        print("  assignments - Show active agent assignments")
        print("  log [limit] - Show coordination log (default: 10)")
        print("  agents      - Show agent status")
        print("  all         - Show everything (default)")


if __name__ == "__main__":
    main()
