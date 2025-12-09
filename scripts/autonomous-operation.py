#!/usr/bin/env python3
"""
Autonomous 24/7 Operation Script
Runs CTO Agent continuously until project is gold-class complete

Usage:
    python3 scripts/autonomous-operation.py

This script:
1. Enables autonomous operation mode in knowledge base
2. Continuously invokes CTO Agent to work on tasks
3. Checks completion criteria after each cycle
4. Reports status periodically
5. Stops when project is gold-class complete
"""

import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent


def load_knowledge_base():
    """Load knowledge base from file"""
    kb_path = PROJECT_ROOT / ".ai-knowledge-base.json"
    with open(kb_path, "r") as f:
        return json.load(f)


def save_knowledge_base(kb):
    """Save knowledge base to file"""
    kb_path = PROJECT_ROOT / ".ai-knowledge-base.json"
    kb["last_updated"] = datetime.now().isoformat()
    with open(kb_path, "w") as f:
        json.dump(kb, f, indent=2)


def check_completion(kb):
    """Check if project is gold-class complete"""
    completion = kb.get("autonomous_operation", {}).get("completion_status", {})
    test_results = kb.get("test_results", {})
    requirements = kb.get("requirements_coverage", {})

    # Check all completion criteria
    phases_complete = completion.get("phases_complete", 0) >= completion.get("total_phases", 4)

    requirements_covered = requirements.get("overall_coverage_percentage", 0) >= 100

    test_coverage_ok = test_results.get("overall_coverage", 0) >= 80

    all_tests_passing = test_results.get("failing_tests", 0) == 0

    production_ready = completion.get("production_ready", False)

    return (
        phases_complete
        and requirements_covered
        and test_coverage_ok
        and all_tests_passing
        and production_ready
    )


def initialize_autonomous_operation(kb):
    """Initialize autonomous operation in knowledge base"""
    if "autonomous_operation" not in kb:
        kb["autonomous_operation"] = {}

    op = kb["autonomous_operation"]

    if not op.get("enabled", False):
        op["enabled"] = True
        op["mode"] = "24/7_until_complete"
        op["status"] = "running"
        op["started_at"] = datetime.now().isoformat()
        op["current_iteration"] = 0
        op["work_cycles_completed"] = 0
        op["tasks_completed"] = 0
        op["last_cycle_at"] = None
        op["next_cycle_at"] = None
        op["completion_estimate"] = None

        # Initialize completion status
        if "completion_status" not in op:
            op["completion_status"] = {
                "phases_complete": 0,
                "total_phases": 4,
                "requirements_covered": 0,
                "target_coverage": 100,
                "production_ready": False,
            }

        save_knowledge_base(kb)
        print("✅ Autonomous operation initialized")

    return op


def run_work_cycle(kb, iteration):
    """Execute one work cycle"""
    op = kb.get("autonomous_operation", {})

    print(f"\n🔄 Work Cycle {iteration}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Update cycle tracking
    op["current_iteration"] = iteration
    op["work_cycles_completed"] = op.get("work_cycles_completed", 0) + 1
    op["last_cycle_at"] = datetime.now().isoformat()
    op["next_cycle_at"] = (datetime.now() + timedelta(minutes=20)).isoformat()

    # In a real implementation, this would:
    # 1. Invoke CTO Agent via API or direct call
    # 2. CTO Agent selects next task
    # 3. CTO Agent executes task
    # 4. CTO Agent updates knowledge base
    # 5. CTO Agent checks quality gates

    # For now, we just update the knowledge base
    # The actual work is done by the CTO Agent when invoked

    print("📋 CTO Agent would execute next task here")
    print("   (In production, this invokes CTO Agent)")

    kb["autonomous_operation"] = op
    save_knowledge_base(kb)

    return True


def print_status_report(kb):
    """Print status report"""
    op = kb.get("autonomous_operation", {})
    completion = op.get("completion_status", {})
    test_results = kb.get("test_results", {})
    requirements = kb.get("requirements_coverage", {})

    print("\n" + "=" * 60)
    print("📊 AUTONOMOUS OPERATION STATUS REPORT")
    print("=" * 60)
    print(f"Started: {op.get('started_at', 'N/A')}")
    print(f"Iteration: {op.get('current_iteration', 0)}")
    print(f"Work Cycles: {op.get('work_cycles_completed', 0)}")
    print(f"Tasks Completed: {op.get('tasks_completed', 0)}")

    print("\n📈 Progress:")
    print(
        f"  Phases Complete: {completion.get('phases_complete', 0)}/{completion.get('total_phases', 4)}"
    )
    print(f"  Requirements Coverage: {requirements.get('overall_coverage_percentage', 0)}%")
    print(f"  Test Coverage: {test_results.get('overall_coverage', 0)}%")
    print(
        f"  Tests Passing: {test_results.get('passing_tests', 0)}/{test_results.get('total_tests', 0)}"
    )
    print(f"  Production Ready: {completion.get('production_ready', False)}")

    print("\n✅ Completion Criteria:")
    print(
        f"  All Phases Complete: {completion.get('phases_complete', 0) >= completion.get('total_phases', 4)}"
    )
    print(f"  Requirements 100%: {requirements.get('overall_coverage_percentage', 0) >= 100}")
    print(f"  Test Coverage 80%+: {test_results.get('overall_coverage', 0) >= 80}")
    print(f"  All Tests Passing: {test_results.get('failing_tests', 0) == 0}")
    print(f"  Production Ready: {completion.get('production_ready', False)}")

    print("=" * 60 + "\n")


def main():
    """Main autonomous operation loop"""
    print("🚀 Starting Autonomous 24/7 Operation")
    print("=" * 60)

    try:
        kb = load_knowledge_base()
        op = initialize_autonomous_operation(kb)

        print("✅ Autonomous operation enabled")
        print(f"📅 Started at: {op['started_at']}")
        print(f"🎯 Mode: {op['mode']}")
        print(f"📊 Status: {op['status']}")

        iteration = 0
        last_status_report = datetime.now()
        status_report_interval = timedelta(hours=2)

        print("\n🔄 Starting work cycles...")
        print("   (Press Ctrl+C to stop gracefully)\n")

        while True:
            iteration += 1

            # Check completion
            if check_completion(kb):
                print("\n" + "=" * 60)
                print("🎉 PROJECT IS GOLD-CLASS COMPLETE!")
                print("=" * 60)
                print_status_report(kb)
                print("✅ All completion criteria met")
                print("🛑 Stopping autonomous operation")
                break

            # Run work cycle
            run_work_cycle(kb, iteration)

            # Status report every 2 hours
            if datetime.now() - last_status_report >= status_report_interval:
                print_status_report(kb)
                last_status_report = datetime.now()

            # Wait before next cycle (20 minutes)
            wait_minutes = 20
            print(f"⏳ Waiting {wait_minutes} minutes before next cycle...")
            print(
                f"   Next cycle at: {(datetime.now() + timedelta(minutes=wait_minutes)).strftime('%H:%M:%S')}"
            )
            time.sleep(wait_minutes * 60)

    except KeyboardInterrupt:
        print("\n\n⚠️  Autonomous operation stopped by user")
        kb = load_knowledge_base()
        op = kb.get("autonomous_operation", {})
        op["status"] = "stopped"
        op["stopped_at"] = datetime.now().isoformat()
        save_knowledge_base(kb)
        print("✅ Status saved. Operation can be resumed.")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        kb = load_knowledge_base()
        op = kb.get("autonomous_operation", {})
        op["status"] = "error"
        op["error"] = str(e)
        op["error_at"] = datetime.now().isoformat()
        save_knowledge_base(kb)
        sys.exit(1)


if __name__ == "__main__":
    main()
