#!/usr/bin/env python3
"""
Validate .ai-knowledge-base.json structure
Pre-commit hook to ensure knowledge base integrity
"""
import json
import sys
from pathlib import Path


def validate_knowledge_base():
    """Validate knowledge base JSON structure"""
    kb_path = Path(".ai-knowledge-base.json")

    if not kb_path.exists():
        print("❌ .ai-knowledge-base.json not found")
        return False

    try:
        with open(kb_path, "r") as f:
            data = json.load(f)

        # Required fields
        required_fields = ["version", "last_updated", "project", "agents", "agent_coordination"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            print(f"❌ Missing required fields: {', '.join(missing_fields)}")
            return False

        # Validate version format
        if not isinstance(data.get("version"), str):
            print("❌ 'version' must be a string")
            return False

        # Validate agents structure
        if not isinstance(data.get("agents"), dict):
            print("❌ 'agents' must be a dictionary")
            return False

        print("✅ Knowledge base structure is valid")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating knowledge base: {e}")
        return False


if __name__ == "__main__":
    success = validate_knowledge_base()
    sys.exit(0 if success else 1)
