# Agent Coordination Visibility

## How to See Work Assignment and Multi-Agent Execution

**Date:** December 1, 2025
**Purpose:** Make agent coordination transparent and observable

---

## 🎯 The Problem

**User Question:** "How do I know when Product Manager/CTO Agent is assigning work vs. doing work itself? How can I see that work is being distributed to specialized agents?"

**Answer:** We need visibility into the agent coordination process. This document explains how to track and observe agent assignments and execution.

---

## 🔍 How Agent Coordination Works

### Current Flow (What Happens):

```
You: "@Product Manager/CTO Agent: Implement case management APIs"

Product Manager/CTO Agent:
1. Reads knowledge base
2. Breaks down into tasks:
   - Task 1: Create case model → Backend API Agent
   - Task 2: Implement CRUD APIs → Backend API Agent
   - Task 3: Add validation → Backend API Agent
   - Task 4: Write tests → QA Agent
3. Updates knowledge base with assignments
4. Coordinates execution
5. Reports status
```

**But you can't see this happening!**

---

## ✅ Solution: Visibility System

### 1. Knowledge Base Tracking

**Every assignment is logged in `.ai-knowledge-base.json`:**

```json
{
  "agent_coordination": {
    "active_assignments": [
      {
        "id": "ASSIGN_001",
        "assigned_by": "Product Manager/CTO Agent",
        "assigned_to": "Backend API Agent",
        "task": "Implement case management CRUD APIs",
        "assigned_at": "2025-12-01T10:00:00",
        "status": "in_progress",
        "started_at": "2025-12-01T10:01:00",
        "progress": 30,
        "files_modified": ["backend/app/api/routes/cases.py"],
        "estimated_completion": "2025-12-01T12:00:00"
      },
      {
        "id": "ASSIGN_002",
        "assigned_by": "Product Manager/CTO Agent",
        "assigned_to": "QA Agent",
        "task": "Write tests for case management APIs",
        "assigned_at": "2025-12-01T10:00:00",
        "status": "pending",
        "dependencies": ["ASSIGN_001"],
        "waiting_for": "Backend API Agent to complete CRUD APIs"
      }
    ],
    "recent_assignments": [
      // Last 20 assignments
    ],
    "coordination_log": [
      {
        "timestamp": "2025-12-01T10:00:00",
        "event": "assignment",
        "from": "Product Manager/CTO Agent",
        "to": "Backend API Agent",
        "task": "Implement case management CRUD APIs",
        "details": "Breaking down Phase 1 into specific tasks"
      },
      {
        "timestamp": "2025-12-01T10:01:00",
        "event": "work_started",
        "agent": "Backend API Agent",
        "task": "Implement case management CRUD APIs",
        "details": "Started implementing POST /api/cases endpoint"
      }
    ]
  }
}
```

---

## 📊 How to See Agent Coordination

### Method 1: Check Knowledge Base

**View Active Assignments:**

```bash
cat .ai-knowledge-base.json | jq '.agent_coordination.active_assignments'
```

**View Coordination Log:**

```bash
cat .ai-knowledge-base.json | jq '.agent_coordination.coordination_log[-10:]'
```

**View Agent Status:**

```bash
cat .ai-knowledge-base.json | jq '.agents'
```

---

### Method 2: Ask Product Manager/CTO Agent

**You say:**

```
@Product Manager/CTO Agent: Show me current agent assignments. Who is doing what?
```

**Agent reports:**

```
Current Agent Assignments:

1. Backend API Agent
   - Task: Implement case management CRUD APIs
   - Status: In Progress (30% complete)
   - Started: 10:01 AM
   - Files Modified: backend/app/api/routes/cases.py
   - Estimated Completion: 12:00 PM

2. QA Agent
   - Task: Write tests for case management APIs
   - Status: Pending (waiting for Backend API Agent)
   - Dependencies: Backend APIs must be complete

3. Frontend Agent
   - Task: Create case list page
   - Status: Pending (waiting for Backend APIs)
   - Dependencies: Backend APIs must be complete
```

---

### Method 3: Status Dashboard

**Run status script:**

```bash
python3 scripts/cto-status.py agents
```

**Output:**

```
Agent Coordination Status
==========================

Active Assignments: 3
In Progress: 1
Pending: 2

Backend API Agent
  Status: In Progress
  Task: Implement case management CRUD APIs
  Progress: 30%
  Started: 10:01 AM
  Files: backend/app/api/routes/cases.py

QA Agent
  Status: Pending
  Task: Write tests for case management APIs
  Waiting for: Backend API Agent

Frontend Agent
  Status: Pending
  Task: Create case list page
  Waiting for: Backend API Agent
```

---

## 🔄 Assignment vs. Execution

### How to Tell the Difference:

#### **Assignment (Product Manager/CTO Agent):**

- ✅ Updates knowledge base with task assignments
- ✅ Breaks down high-level goal into tasks
- ✅ Assigns tasks to specialized agents
- ✅ Sets up dependencies
- ✅ **Does NOT write code itself**

**Indicators:**

- Knowledge base shows new assignments
- No code files modified by Product Manager/CTO Agent
- Coordination log shows "assignment" events

#### **Execution (Specialized Agents):**

- ✅ Backend API Agent writes code
- ✅ Frontend Agent creates UI components
- ✅ QA Agent writes tests
- ✅ Updates knowledge base with progress
- ✅ **Actually implements the work**

**Indicators:**

- Code files are modified
- Knowledge base shows "work_started" events
- Progress updates in knowledge base
- Files created/modified by specialized agents

---

## 📋 Example: Complete Workflow Visibility

### Step 1: You Give Command

```
You: "@Product Manager/CTO Agent: Implement case management with full CRUD"
```

### Step 2: Product Manager/CTO Agent Assigns Work

**Knowledge Base Updated:**

```json
{
  "agent_coordination": {
    "coordination_log": [
      {
        "timestamp": "2025-12-01T10:00:00",
        "event": "assignment",
        "from": "Product Manager/CTO Agent",
        "to": "Backend API Agent",
        "task": "Implement case management CRUD APIs",
        "details": "Breaking down 'case management' into: POST, GET, PUT, DELETE endpoints"
      },
      {
        "timestamp": "2025-12-01T10:00:00",
        "event": "assignment",
        "from": "Product Manager/CTO Agent",
        "to": "QA Agent",
        "task": "Write tests for case management APIs",
        "details": "Waiting for Backend API Agent to complete"
      }
    ],
    "active_assignments": [
      {
        "id": "ASSIGN_001",
        "assigned_by": "Product Manager/CTO Agent",
        "assigned_to": "Backend API Agent",
        "task": "Implement case management CRUD APIs",
        "status": "assigned",
        "assigned_at": "2025-12-01T10:00:00"
      }
    ]
  }
}
```

**You can see:** Product Manager/CTO Agent assigned work, but hasn't written code yet.

---

### Step 3: Backend API Agent Starts Work

**Knowledge Base Updated:**

```json
{
  "agent_coordination": {
    "coordination_log": [
      {
        "timestamp": "2025-12-01T10:01:00",
        "event": "work_started",
        "agent": "Backend API Agent",
        "task": "Implement case management CRUD APIs",
        "details": "Started implementing POST /api/cases endpoint"
      }
    ],
    "active_assignments": [
      {
        "id": "ASSIGN_001",
        "status": "in_progress",
        "started_at": "2025-12-01T10:01:00",
        "progress": 10,
        "files_modified": ["backend/app/api/routes/cases.py"]
      }
    ]
  }
}
```

**You can see:** Backend API Agent started working, files are being modified.

---

### Step 4: Backend API Agent Updates Progress

**Knowledge Base Updated:**

```json
{
  "agent_coordination": {
    "coordination_log": [
      {
        "timestamp": "2025-12-01T10:15:00",
        "event": "progress_update",
        "agent": "Backend API Agent",
        "task": "Implement case management CRUD APIs",
        "details": "Completed POST endpoint, working on GET endpoints",
        "progress": 40
      }
    ],
    "active_assignments": [
      {
        "id": "ASSIGN_001",
        "progress": 40,
        "files_modified": [
          "backend/app/api/routes/cases.py",
          "backend/app/services/case.py"
        ]
      }
    ]
  }
}
```

**You can see:** Backend API Agent is making progress, more files modified.

---

### Step 5: Backend API Agent Completes Work

**Knowledge Base Updated:**

```json
{
  "agent_coordination": {
    "coordination_log": [
      {
        "timestamp": "2025-12-01T11:30:00",
        "event": "work_completed",
        "agent": "Backend API Agent",
        "task": "Implement case management CRUD APIs",
        "details": "All CRUD endpoints implemented and tested",
        "files_created": [
          "backend/app/api/routes/cases.py",
          "backend/app/services/case.py"
        ],
        "files_modified": []
      },
      {
        "timestamp": "2025-12-01T11:31:00",
        "event": "dependency_ready",
        "agent": "Backend API Agent",
        "task": "Implement case management CRUD APIs",
        "details": "Backend APIs ready, QA Agent can start testing"
      }
    ],
    "active_assignments": [
      {
        "id": "ASSIGN_001",
        "status": "completed",
        "completed_at": "2025-12-01T11:30:00",
        "progress": 100
      },
      {
        "id": "ASSIGN_002",
        "status": "in_progress",
        "started_at": "2025-12-01T11:31:00",
        "assigned_to": "QA Agent"
      }
    ]
  }
}
```

**You can see:** Backend API Agent completed, QA Agent started automatically.

---

## 🎯 Quick Commands to See Coordination

### Check Current Assignments:

```
@Product Manager/CTO Agent: Show me current agent assignments
```

### Check Agent Status:

```
@Product Manager/CTO Agent: What is each agent working on?
```

### Check Coordination Log:

```
@Product Manager/CTO Agent: Show me recent coordination activity
```

### Check Specific Agent:

```
@Product Manager/CTO Agent: What is Backend API Agent doing?
```

---

## 📊 Visual Indicators

### In Knowledge Base:

**Assignment Event:**

```json
{
  "event": "assignment",
  "from": "Product Manager/CTO Agent",
  "to": "Backend API Agent"
}
```

**Meaning:** Work assigned, not executed yet

**Work Started Event:**

```json
{
  "event": "work_started",
  "agent": "Backend API Agent",
  "files_modified": ["backend/app/api/routes/cases.py"]
}
```

**Meaning:** Agent started working, code being written

**Progress Update Event:**

```json
{
  "event": "progress_update",
  "agent": "Backend API Agent",
  "progress": 50
}
```

**Meaning:** Agent making progress

**Work Completed Event:**

```json
{
  "event": "work_completed",
  "agent": "Backend API Agent",
  "files_created": ["backend/app/api/routes/cases.py"]
}
```

**Meaning:** Agent finished work

---

## 🔧 Implementation: Enhanced Knowledge Base

### Add to `.ai-knowledge-base.json`:

```json
{
  "agent_coordination": {
    "active_assignments": [],
    "recent_assignments": [],
    "coordination_log": [],
    "agent_status": {
      "Product Manager/CTO Agent": {
        "current_role": "coordinator",
        "assignments_made": 5,
        "last_assignment": "2025-12-01T10:00:00"
      },
      "Backend API Agent": {
        "current_role": "executor",
        "current_task": "Implement case management APIs",
        "status": "in_progress",
        "progress": 30
      }
    }
  }
}
```

---

## ✅ Summary

### How to See Assignment vs. Execution:

1. **Assignment (Product Manager/CTO Agent):**

   - Check knowledge base for "assignment" events
   - No code files modified yet
   - Tasks appear in `active_assignments`

2. **Execution (Specialized Agents):**
   - Check knowledge base for "work_started" events
   - Code files are modified
   - Progress updates appear

### How to Track Multi-Agent Work:

1. **Check Knowledge Base:**

   ```bash
   cat .ai-knowledge-base.json | jq '.agent_coordination'
   ```

2. **Ask Product Manager/CTO Agent:**

   ```
   @Product Manager/CTO Agent: Show me current agent assignments
   ```

3. **Run Status Script:**
   ```bash
   python3 scripts/cto-status.py agents
   ```

### Key Indicators:

- **Assignment:** `event: "assignment"` in coordination log
- **Execution:** `event: "work_started"` + files modified
- **Progress:** `event: "progress_update"` + progress percentage
- **Completion:** `event: "work_completed"` + files created

---

**Now you can see exactly what each agent is doing! 🎯**
