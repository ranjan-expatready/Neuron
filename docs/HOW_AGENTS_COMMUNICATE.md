# How Agents Communicate and Share Memory

## Simple Explanation for Non-Technical Users

---

## 🎯 The Simple Answer

**Agents share memory through ONE FILE: `.ai-knowledge-base.json`**

This file:

- ✅ Contains everything agents know
- ✅ Persists across all sessions
- ✅ Never loses context
- ✅ Human-readable (you can read it)
- ✅ Version controlled (git tracks changes)

---

## 📁 Three Types of Memory

### 1. Knowledge Base (PRIMARY) - `.ai-knowledge-base.json`

**What it is:** One JSON file that tracks everything

**Contains:**

- What's done
- What's not done
- Who's doing what
- All decisions
- Project status

**How agents use it:**

1. Agent reads file → Knows current state
2. Agent does work
3. Agent updates file → Other agents see update
4. File persists → Available in next session

**Location:** `.ai-knowledge-base.json` (root of project)

---

### 2. Vector Database (Semantic Memory) - Chroma/Qdrant

**What it is:** Stores code patterns, legal knowledge, best practices

**Contains:**

- Code embeddings (for similarity search)
- Legal knowledge (IRCC rules)
- Best practices
- Past decisions

**How agents use it:**

- Search for similar code
- Find relevant legal rules
- Get best practices
- Learn from past work

**Location:** `.ai-memory/chroma/` (local) or cloud

**Used by:** Law Intelligence Agent, Mastermind Agent, etc.

---

### 3. Database (Application Data) - PostgreSQL

**What it is:** Production database with user/case data

**Contains:**

- User accounts
- Cases
- Documents
- Tasks
- Audit logs

**How agents use it:**

- Via APIs (not direct access)
- For application data
- For production use

**Location:** PostgreSQL database

---

## 🔄 How Agents Communicate

### Current Model (Simple)

```
Agent 1 → Updates .ai-knowledge-base.json
         ↓
Agent 2 → Reads .ai-knowledge-base.json
         ↓
Agent 2 → Sees Agent 1's work
         ↓
Agent 2 → Does dependent work
         ↓
Agent 2 → Updates .ai-knowledge-base.json
```

**It's that simple!** Agents communicate by reading/writing the same file.

---

### Example: Authentication Bug Fix

1. **Backend API Agent:**

   - Reads knowledge base
   - Sees task: "Fix authentication bug"
   - Fixes bug
   - Updates knowledge base: "Task completed"

2. **QA Agent:**

   - Reads knowledge base
   - Sees: "Authentication bug fixed"
   - Writes tests
   - Updates knowledge base: "Tests written"

3. **CTO Agent:**
   - Reads knowledge base
   - Sees: "Auth bug fixed, tests written"
   - Reports: "Authentication complete"

**All through one file!**

---

## 🧠 Memory Sharing Explained

### Scenario: Agent Needs Information

**QA Agent needs to know what to test:**

1. **Reads knowledge base:**

   ```json
   {
     "tasks": {
       "completed": [
         {
           "title": "Fix authentication bug",
           "files_modified": ["backend/app/services/auth.py"]
         }
       ]
     }
   }
   ```

2. **Gets context:**

   - What was fixed
   - What files changed
   - What needs testing

3. **Writes tests:**
   - Based on knowledge base info
   - Updates knowledge base when done

---

### Scenario: Agent Completes Work

**Backend API Agent completes feature:**

1. **Updates knowledge base:**

   ```json
   {
     "tasks": {
       "completed": [
         {
           "id": "FEATURE_X",
           "title": "Implement feature X",
           "agent": "Backend API Agent",
           "status": "completed"
         }
       ]
     },
     "agents": {
       "Backend API Agent": {
         "completed_tasks": ["FEATURE_X"],
         "last_activity": "2025-12-01T..."
       }
     }
   }
   ```

2. **Other agents see update:**

   - QA Agent: "Feature complete, I can test"
   - Frontend Agent: "Backend ready, I can integrate"
   - CTO Agent: "Progress updated"

3. **Memory persists:**
   - Saved to disk
   - In git
   - Available next session

---

## 🤝 Agent Coordination

### How Agents Work Together

**Through Knowledge Base:**

1. **Task Assignment:**

   - Task added to knowledge base
   - Agent sees task
   - Agent starts work

2. **Dependency Tracking:**

   - Task has dependencies
   - Agent checks if dependencies complete
   - Starts work when ready

3. **Progress Updates:**

   - Agent updates status
   - Other agents see progress
   - Coordination happens automatically

4. **Completion:**
   - Agent marks task complete
   - Dependent tasks can start
   - Knowledge base updated

---

## 📊 Visual Flow

```
┌─────────────────────────────────────┐
│   .ai-knowledge-base.json          │
│   (Single Source of Truth)         │
└─────────────────────────────────────┘
           │         │         │
           │         │         │
      ┌────┘         │         └────┐
      │              │              │
      ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Agent 1  │   │ Agent 2  │   │ Agent 3  │
│ (Reads)  │   │ (Reads)  │   │ (Reads)  │
└──────────┘   └──────────┘   └──────────┘
      │              │              │
      │              │              │
      ▼              ▼              ▼
   (Works)        (Works)        (Works)
      │              │              │
      └──────────────┼──────────────┘
                     │
                     ▼
          ┌──────────────────┐
          │  Updates File    │
          └──────────────────┘
                     │
                     ▼
          ┌──────────────────┐
          │  All Agents See   │
          │     Updates       │
          └──────────────────┘
```

---

## 🎯 Key Points

1. **One File:** `.ai-knowledge-base.json` is everything
2. **Persistent:** Survives chat restarts
3. **Shared:** All agents read/write same file
4. **Version Controlled:** Git tracks changes
5. **Human Readable:** You can read/edit it
6. **Simple:** File-based coordination (no complex setup)

---

## 🔍 How to See Agent Communication

### View Knowledge Base

```bash
cat .ai-knowledge-base.json
```

### View Agent Status

```bash
python3 scripts/cto-status.py agents
```

### View Tasks

```bash
python3 scripts/cto-status.py tasks
```

---

## 💡 Summary

**Agents communicate through:**

- ✅ `.ai-knowledge-base.json` - Primary (structured, human-readable)
- ✅ Vector DB - Semantic search (optional, for similarity)
- ✅ PostgreSQL - Application data (via APIs)

**Current model:**

- File-based coordination
- Simple and effective
- Works across sessions
- No context loss

**Future model (Phase 2+):**

- Event-driven communication
- API-based interfaces
- MCP server integration
- Still uses knowledge base as primary

---

**Bottom Line: One file (`.ai-knowledge-base.json`) is your single source of truth. All agents read and write to it. It persists across sessions. Simple and effective!**
