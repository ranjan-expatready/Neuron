# How to See Agent Coordination

## Quick Guide: Assignment vs. Execution

**Date:** December 1, 2025

---

## 🎯 The Question

**"How do I know when Product Manager/CTO Agent is assigning work vs. doing work itself? How can I see that specialized agents are working?"**

---

## ✅ Quick Answer

### Method 1: Ask Product Manager/CTO Agent

```
@Product Manager/CTO Agent: Show me current agent assignments. Who is doing what?
```

### Method 2: Check Knowledge Base

```bash
cat .ai-knowledge-base.json | jq '.agent_coordination'
```

### Method 3: Run Status Script

```bash
python3 scripts/agent-coordination-status.py
```

---

## 🔍 How to Tell Assignment vs. Execution

### Assignment (Product Manager/CTO Agent):

**Indicators:**

- ✅ Knowledge base shows `event: "assignment"` in coordination log
- ✅ Task appears in `active_assignments` with `status: "assigned"`
- ✅ No code files modified yet
- ✅ Product Manager/CTO Agent logged the assignment

**Example:**

```json
{
  "event": "assignment",
  "from": "Product Manager/CTO Agent",
  "to": "Backend API Agent",
  "task": "Implement case management APIs"
}
```

---

### Execution (Specialized Agent):

**Indicators:**

- ✅ Knowledge base shows `event: "work_started"` in coordination log
- ✅ Task status changes to `"in_progress"`
- ✅ Code files are modified
- ✅ Progress updates appear

**Example:**

```json
{
  "event": "work_started",
  "agent": "Backend API Agent",
  "task": "Implement case management APIs",
  "files_modified": ["backend/app/api/routes/cases.py"]
}
```

---

## 📊 Visual Indicators

| Event             | Meaning               | Who Did It                |
| ----------------- | --------------------- | ------------------------- |
| `assignment`      | Work assigned         | Product Manager/CTO Agent |
| `work_started`    | Agent started working | Specialized Agent         |
| `progress_update` | Agent making progress | Specialized Agent         |
| `work_completed`  | Agent finished work   | Specialized Agent         |

---

## 🚀 Quick Commands

### See All Assignments:

```
@Product Manager/CTO Agent: Show me current agent assignments
```

### See Who's Working:

```
@Product Manager/CTO Agent: What is each agent working on?
```

### See Coordination Activity:

```
@Product Manager/CTO Agent: Show me recent coordination activity
```

### Check Specific Agent:

```
@Product Manager/CTO Agent: What is Backend API Agent doing?
```

---

## 📋 Example Output

**When you ask: "Show me current agent assignments"**

**Product Manager/CTO Agent reports:**

```
Current Agent Assignments:

1. Backend API Agent
   - Task: Implement case management CRUD APIs
   - Status: In Progress (30% complete)
   - Started: 10:01 AM
   - Files Modified: backend/app/api/routes/cases.py
   - Assigned By: Product Manager/CTO Agent (10:00 AM)

2. QA Agent
   - Task: Write tests for case management APIs
   - Status: Pending (waiting for Backend API Agent)
   - Dependencies: Backend APIs must be complete
   - Assigned By: Product Manager/CTO Agent (10:00 AM)
```

**You can see:**

- ✅ Product Manager/CTO Agent assigned work (10:00 AM)
- ✅ Backend API Agent started working (10:01 AM)
- ✅ Backend API Agent is making progress (30%)
- ✅ QA Agent is waiting (dependency)

---

## ✅ Summary

**How to See Assignment:**

- Check coordination log for `event: "assignment"`
- See `active_assignments` with `status: "assigned"`
- No files modified yet

**How to See Execution:**

- Check coordination log for `event: "work_started"`
- See `active_assignments` with `status: "in_progress"`
- Files are being modified
- Progress updates appear

**Quick Command:**

```
@Product Manager/CTO Agent: Show me current agent assignments
```

---

**Now you can see exactly what's happening! 🎯**
