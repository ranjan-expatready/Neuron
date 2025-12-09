# Agent Operating Model

## How AI Agents Communicate, Share Memory, and Work Together

**Document Version:** 1.0
**Date:** December 2025
**Based on:** Master Specification and System Architecture

---

## 🎯 Overview

This document explains how AI agents in Canada Immigration OS communicate, share memory, and coordinate work. This is the **operating model** that all agents follow.

---

## 📁 Memory Architecture

### Three Types of Memory Storage

#### 1. **Structured Memory** - `.ai-knowledge-base.json` (PRIMARY)

**Purpose:** Human-readable, version-controlled knowledge base

**Contains:**

- Project status and progress
- Agent status and tasks
- Completed work
- Architectural decisions
- Requirements and gaps
- Metrics and KPIs

**Characteristics:**

- ✅ JSON format (human-readable)
- ✅ Version controlled in git
- ✅ Single source of truth
- ✅ Persists across all sessions
- ✅ Updated by all agents
- ✅ No context loss

**Location:** Root of project (`.ai-knowledge-base.json`)

**Used By:** All agents, especially CTO/Product Manager Agent

---

#### 2. **Semantic Memory** - Vector Database (Chroma/Qdrant)

**Purpose:** Semantic search and similarity matching

**Contains:**

- Code embeddings
- Document embeddings
- Legal knowledge (IRCC rules)
- Case precedents
- Best practices
- Agent decisions and patterns

**Characteristics:**

- ✅ Vector embeddings (semantic search)
- ✅ Fast similarity matching
- ✅ Stores unstructured knowledge
- ✅ Used for RAG (Retrieval Augmented Generation)
- ✅ Shared across all agents

**Location:** `.ai-memory/chroma/` (local) or cloud vector DB

**Used By:**

- Law Intelligence Agent (legal knowledge)
- Mastermind Agent (expert knowledge)
- Document Intelligence Agent (document patterns)
- All agents (for semantic search)

---

#### 3. **Structured Database** - PostgreSQL

**Purpose:** Application data and structured records

**Contains:**

- User data
- Case data
- Documents
- Tasks
- Audit logs
- AI session history

**Characteristics:**

- ✅ Relational database
- ✅ ACID transactions
- ✅ Multi-tenant isolation
- ✅ Production data

**Location:** PostgreSQL database

**Used By:** All backend services and agents (via APIs)

---

## 🔄 Agent Communication Model

### Current Implementation (Phase 1)

**File-Based Coordination:**

- `.ai-knowledge-base.json` - Shared knowledge base
- Agents read/write to this file
- Simple, effective, version-controlled

**How It Works:**

1. Agent reads `.ai-knowledge-base.json`
2. Agent performs work
3. Agent updates `.ai-knowledge-base.json`
4. Other agents see updates
5. Coordination happens through file

---

### Future Implementation (Phase 2+)

**Event-Driven Architecture:**

- Message queues (Redis/RabbitMQ)
- Event bus for agent communication
- Async communication
- Pub/sub pattern

**API-Based Communication:**

- Agents communicate via APIs
- RESTful agent interfaces
- Standardized protocols
- Service mesh for security

**MCP Servers:**

- GitHub MCP - Code management
- DB MCP - Database access
- Vector DB MCP - Semantic search
- Browser MCP - IRCC research
- K8s MCP - Deployment
- Observability MCP - Monitoring

---

## 🤝 How Agents Share Memory

### Scenario 1: Agent Completes Work

**Backend API Agent completes authentication fix:**

1. **Agent updates knowledge base:**

   ```json
   {
     "tasks": {
       "completed": [
         {
           "id": "AUTH_BUG_FIX",
           "title": "Fix authentication bug",
           "agent": "Backend API Agent",
           "status": "completed"
         }
       ]
     },
     "agents": {
       "Backend API Agent": {
         "completed_tasks": ["AUTH_BUG_FIX"],
         "last_activity": "2025-12-01T..."
       }
     }
   }
   ```

2. **Other agents see update:**

   - QA Agent: "Authentication fix complete, I can write tests"
   - Frontend Agent: "Backend fixed, I can test frontend"
   - CTO Agent: "One task completed, project at 15%"

3. **Memory persists:**
   - File saved to disk
   - Version controlled in git
   - Available in next session

---

### Scenario 2: Agent Needs Information

**QA Agent needs to know what to test:**

1. **QA Agent reads knowledge base:**

   ```python
   with open('.ai-knowledge-base.json', 'r') as f:
       kb = json.load(f)

   # Find completed tasks that need tests
   completed = kb['tasks']['completed']
   # Find what Backend API Agent did
   backend_tasks = [t for t in completed if t['agent'] == 'Backend API Agent']
   ```

2. **QA Agent gets context:**

   - What was implemented
   - What files were changed
   - What the fix does
   - What needs testing

3. **QA Agent writes tests:**
   - Based on knowledge base info
   - Updates knowledge base when done

---

### Scenario 3: Semantic Search

**Mastermind Agent needs legal knowledge:**

1. **Agent queries vector DB:**

   ```python
   # Search for similar legal requirements
   results = vector_db.query(
       query_text="Express Entry eligibility requirements",
       n_results=5
   )
   ```

2. **Gets relevant context:**

   - Similar legal rules
   - Past decisions
   - Best practices
   - Case precedents

3. **Uses context for decision:**
   - Makes informed recommendation
   - Stores decision in knowledge base

---

## 📊 Memory Sharing Flow

```
┌─────────────────────────────────────────────────┐
│         .ai-knowledge-base.json                 │
│  (Structured, Human-Readable, Version-Controlled)│
└─────────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   Agent 1      Agent 2      Agent 3
   (Reads)      (Reads)      (Reads)
        │           │           │
        │           │           │
        ▼           ▼           ▼
   (Works)      (Works)      (Works)
        │           │           │
        │           │           │
        └───────────┼───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Updates Knowledge    │
        │       Base            │
        └───────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  All Agents See        │
        │      Updates           │
        └───────────────────────┘
```

---

## 🔍 How Agents Query Memory

### Querying Structured Memory (Knowledge Base)

```python
# Read knowledge base
import json
with open('.ai-knowledge-base.json', 'r') as f:
    kb = json.load(f)

# Query project status
status = kb['project']['status']
completion = kb['project']['completion_percentage']

# Query agent status
agent_status = kb['agents']['Backend API Agent']

# Query tasks
completed_tasks = kb['tasks']['completed']
pending_tasks = kb['tasks']['pending']

# Query decisions
decisions = kb['decisions']
```

### Querying Semantic Memory (Vector DB)

```python
# Query vector database for semantic search
from ai_memory_manager import AgentMemory

memory = AgentMemory()

# Search for similar code/decisions
results = memory.retrieve_context(
    agent_name="Backend API Agent",
    query="authentication implementation",
    n_results=5
)

# Get related context
related = memory.get_related_context(
    query="password hashing",
    n_results=10
)
```

### Querying Database (PostgreSQL)

```python
# Query structured database via API
# (Agents use APIs, not direct DB access)

# Example: Get case data
response = requests.get('/api/v1/cases/123')
case_data = response.json()
```

---

## 🎯 Agent Coordination Protocol

### Step 1: Agent Reads Knowledge Base

```python
# Agent starts work
kb = load_knowledge_base()

# Check current state
current_tasks = kb['tasks']['in_progress']
my_tasks = [t for t in current_tasks if t['agent'] == 'My Agent Name']

# Check dependencies
for task in my_tasks:
    deps = task.get('dependencies', [])
    # Verify dependencies are complete
```

### Step 2: Agent Performs Work

```python
# Agent does work
# - Implements feature
# - Writes code
# - Creates tests
# - Updates documentation
```

### Step 3: Agent Updates Knowledge Base

```python
# Agent updates knowledge base
kb = load_knowledge_base()

# Mark task complete
task['status'] = 'completed'
task['completed_at'] = datetime.now().isoformat()

# Move from in_progress to completed
kb['tasks']['in_progress'].remove(task)
kb['tasks']['completed'].append(task)

# Update agent status
kb['agents']['My Agent']['completed_tasks'].append(task_id)
kb['agents']['My Agent']['current_task'] = None
kb['agents']['My Agent']['last_activity'] = datetime.now().isoformat()

# Update metrics
kb['metrics']['tasks_completed'] += 1
kb['last_updated'] = datetime.now().isoformat()

# Save
save_knowledge_base(kb)
```

### Step 4: Other Agents See Update

```python
# Other agents read updated knowledge base
kb = load_knowledge_base()

# See new completed task
new_completion = kb['tasks']['completed'][-1]

# Can now work on dependent tasks
if my_task['dependencies'] == [new_completion['id']]:
    # Dependencies met, can start work
    start_work()
```

---

## 🔗 Agent Communication Patterns

### Pattern 1: Direct Coordination (Current)

**Through Knowledge Base:**

- Agent A completes work → Updates `.ai-knowledge-base.json`
- Agent B reads knowledge base → Sees Agent A's work
- Agent B starts dependent work

**Example:**

- Backend API Agent fixes auth → Updates knowledge base
- QA Agent reads knowledge base → Sees fix complete
- QA Agent writes tests → Updates knowledge base

---

### Pattern 2: Event-Driven (Future)

**Through Message Queue:**

- Agent A completes work → Publishes event
- Event bus routes to interested agents
- Agent B receives event → Starts work

**Example:**

- Backend API Agent completes feature → Publishes "feature_completed" event
- QA Agent subscribes to events → Receives notification
- QA Agent starts testing → Publishes "testing_started" event

---

### Pattern 3: API-Based (Future)

**Through REST APIs:**

- Agent A calls Agent B's API
- Agent B processes request
- Agent B returns response

**Example:**

- Mastermind Agent calls Law Intelligence API
- Law Intelligence Agent returns current rules
- Mastermind Agent uses rules for decision

---

## 🧠 Memory Types (From Specification)

Based on `docs/master_spec.md` Section 15:

### 1. Session Memory (Short-term)

- Current chat session
- Temporary context
- Not persisted

### 2. Case Memory (Per Case)

- Case history
- Case actions
- Case decisions
- Stored in: PostgreSQL

### 3. Client Memory (Per Client)

- Client preferences
- Communication history
- Client data
- Stored in: PostgreSQL

### 4. Firm Memory (Per Organization)

- Templates
- Tone and style
- Configurations
- Stored in: PostgreSQL + `.ai-knowledge-base.json`

### 5. Domain Memory (Shared)

- Law and rules
- Best practices
- Expert knowledge
- Stored in: Vector DB + PostgreSQL

---

## 📋 Current Operating Model (Phase 1)

### Memory Sharing

- **Primary:** `.ai-knowledge-base.json` (structured, human-readable)
- **Semantic:** Vector DB (Chroma) for semantic search (optional)
- **Database:** PostgreSQL for application data

### Communication

- **File-based:** Agents coordinate through `.ai-knowledge-base.json`
- **Direct:** Agents read/write knowledge base
- **Version Control:** Git tracks all changes

### Coordination

- **Tasks:** Tracked in knowledge base
- **Dependencies:** Tracked in knowledge base
- **Status:** Updated in knowledge base
- **Progress:** Visible in knowledge base

---

## 🚀 Future Operating Model (Phase 2+)

### Memory Sharing

- **Structured:** PostgreSQL (AI sessions, messages, actions)
- **Semantic:** Vector DB (Chroma/Qdrant) for embeddings
- **Knowledge Base:** `.ai-knowledge-base.json` (still primary)

### Communication

- **Event-Driven:** Message queues (Redis/RabbitMQ)
- **API-Based:** RESTful agent APIs
- **MCP Servers:** Tool integration (GitHub, DB, Browser, etc.)

### Coordination

- **AI Gateway:** Routes requests to agents
- **Event Bus:** Publishes/subscribes to events
- **Service Mesh:** Secure inter-service communication

---

## 🎯 Key Principles

1. **Single Source of Truth:** `.ai-knowledge-base.json` is primary
2. **Persistent Memory:** Survives chat restarts
3. **Version Controlled:** Git tracks all changes
4. **Human Readable:** JSON format, easy to read/edit
5. **Agent Coordination:** Through shared knowledge base
6. **Semantic Search:** Vector DB for similarity matching
7. **Structured Data:** PostgreSQL for application data

---

## 📚 Summary

**Current Model (Phase 1):**

- ✅ `.ai-knowledge-base.json` - Primary memory (structured)
- ✅ Vector DB (Chroma) - Semantic memory (optional)
- ✅ PostgreSQL - Application data
- ✅ File-based coordination
- ✅ Version controlled

**Future Model (Phase 2+):**

- ✅ All of Phase 1, plus:
- ✅ Event-driven communication
- ✅ API-based agent interfaces
- ✅ MCP server integration
- ✅ Service mesh for security

**Key Point:** All agents share memory through `.ai-knowledge-base.json`. This file persists across sessions and is the single source of truth.

---

**This is your operating model. All agents follow this protocol.**
