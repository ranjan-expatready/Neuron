# Your AI Agent Team - Complete Explanation

## How Everything Works Together

---

## 🎯 Your Questions Answered

### Q1: Who reviews architecture and finds requirement gaps?

**Answer: Product Manager/CTO Agent**

This agent combines:

- **Product Manager** - Requirements, features, acceptance criteria
- **CTO/Architect** - Architecture review, technical decisions
- **Requirements Analyst** - Gap analysis, IRCC research

**What it does:**

- ✅ Reviews architecture vs. requirements
- ✅ Finds requirement gaps
- ✅ Researches IRCC website (using Browser MCP)
- ✅ Defines acceptance criteria
- ✅ Coordinates with QA Agent for testing
- ✅ End-to-end product management

**How to use:**

```
@Product Manager/CTO Agent: Review architecture and find requirement gaps. Research IRCC if needed.
```

**Prompt:** `.cursor/agent-prompts/product-manager-cto-agent.md`

---

### Q2: How do agents communicate and share memory?

**Answer: Through ONE FILE - `.ai-knowledge-base.json`**

**Three types of memory:**

1. **`.ai-knowledge-base.json`** (PRIMARY)

   - Structured, human-readable
   - Tracks everything
   - Persists across sessions
   - Single source of truth

2. **Vector DB (Chroma)** (Semantic)

   - Code patterns
   - Legal knowledge
   - Best practices
   - Similarity search

3. **PostgreSQL** (Application Data)
   - User/case data
   - Production data
   - Via APIs

**How agents communicate:**

- Agent A updates `.ai-knowledge-base.json`
- Agent B reads `.ai-knowledge-base.json`
- Agent B sees Agent A's work
- Coordination happens automatically

**Full explanation:** See `docs/HOW_AGENTS_COMMUNICATE.md`

---

### Q3: What's the operating model?

**Answer: File-Based Coordination (Phase 1)**

**Current Model:**

- ✅ `.ai-knowledge-base.json` - Primary memory
- ✅ File-based coordination
- ✅ Version controlled (git)
- ✅ Persists across sessions
- ✅ Simple and effective

**Future Model (Phase 2+):**

- ✅ Event-driven communication
- ✅ API-based interfaces
- ✅ MCP server integration
- ✅ Still uses knowledge base

**Full explanation:** See `docs/AGENT_OPERATING_MODEL.md`

---

## 👥 Your Agent Team Structure

### 1. Product Manager/CTO Agent (YOUR MAIN INTERFACE)

**Role:** Single interface for requirements, architecture, IRCC research

**Responsibilities:**

- Architecture review
- Requirement gap analysis
- IRCC website research
- Acceptance criteria
- Testing coordination
- End-to-end product management

**How to use:**

```
@Product Manager/CTO Agent: [Your question]
```

**Memory:** Uses `.ai-knowledge-base.json` as single source of truth

---

### 2. CTO/Architect Agent (Status Reporting)

**Role:** Project status and coordination

**Responsibilities:**

- Project status reporting
- Agent coordination
- Task management
- Progress tracking

**How to use:**

```
@CTO/Architect Agent: What's the project status?
```

**Memory:** Uses `.ai-knowledge-base.json`

---

### 3. Backend API Agent

**Role:** REST API implementation

**Memory Sharing:**

- Updates `.ai-knowledge-base.json` when work done
- Stores code patterns in Vector DB
- Other agents see updates in knowledge base

---

### 4. QA Agent

**Role:** Testing and quality

**Memory Sharing:**

- Reads acceptance criteria from knowledge base (set by Product Manager/CTO)
- Updates knowledge base with test results
- Shares test patterns via Vector DB

**Communication with Product Manager/CTO:**

- CTO defines acceptance criteria → Updates knowledge base
- QA Agent reads knowledge base → Sees criteria
- QA Agent writes tests → Updates knowledge base
- CTO validates → Signs off

---

### 5. Law Intelligence Agent

**Role:** IRCC research and rule extraction

**Memory Sharing:**

- Stores legal knowledge in Vector DB
- Updates knowledge base with findings
- Product Manager/CTO Agent coordinates research

**Communication with Product Manager/CTO:**

- CTO requests IRCC research → Law Agent researches
- Law Agent finds rules → Updates knowledge base
- CTO validates → Ensures compliance

---

## 🔄 Complete Communication Flow

### Example: Architecture Review + IRCC Research

**Step 1: You ask Product Manager/CTO Agent**

```
@Product Manager/CTO Agent: Review architecture and research IRCC for Express Entry requirements
```

**Step 2: Product Manager/CTO Agent**

1. Reads `.ai-knowledge-base.json` (current state)
2. Reads `docs/master_spec_refined.md` (requirements)
3. Reads `docs/architecture/system_architecture.md` (target)
4. Compares and finds gaps
5. Uses Browser MCP to research IRCC (or guides you)
6. Updates `.ai-knowledge-base.json` with findings
7. Reports to you

**Step 3: Other Agents See Update**

- Law Intelligence Agent: "New IRCC requirements found"
- Backend API Agent: "Architecture gaps identified"
- QA Agent: "New requirements need tests"

**Step 4: Coordination**

- All agents read updated knowledge base
- Work gets assigned
- Progress tracked
- Memory persists

---

## 📊 Memory Sharing Diagram

```
┌─────────────────────────────────────────┐
│    .ai-knowledge-base.json            │
│    (Single Source of Truth)           │
│    - Project status                   │
│    - Agent status                     │
│    - Tasks                            │
│    - Decisions                        │
│    - Gaps                             │
└─────────────────────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Agent 1│ │ Agent 2│ │ Agent 3│
│ Reads  │ │ Reads  │ │ Reads  │
└────────┘ └────────┘ └────────┘
    │         │         │
    ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Works  │ │ Works  │ │ Works  │
└────────┘ └────────┘ └────────┘
    │         │         │
    └─────────┼─────────┘
              │
              ▼
    ┌──────────────────┐
    │  Updates File    │
    └──────────────────┘
              │
              ▼
    ┌──────────────────┐
    │  All See Updates │
    └──────────────────┘
```

---

## 🎯 Your Main Agents

### For Requirements & Architecture:

**Product Manager/CTO Agent** - Your single interface

### For Status & Coordination:

**CTO/Architect Agent** - Project status

### For Implementation:

- Backend API Agent
- Frontend Agent
- QA Agent
- DevOps Agent
- etc.

---

## 📋 How to Use

### Ask Product Manager/CTO Agent:

**Architecture Review:**

```
@Product Manager/CTO Agent: Review architecture and find gaps
```

**Requirement Analysis:**

```
@Product Manager/CTO Agent: Analyze requirement gaps. Research IRCC if needed.
```

**IRCC Research:**

```
@Product Manager/CTO Agent: Research IRCC website for Express Entry requirements
```

**Acceptance Criteria:**

```
@Product Manager/CTO Agent: Define acceptance criteria for document upload. Work with QA Agent.
```

### Ask CTO/Architect Agent:

**Status:**

```
@CTO/Architect Agent: What's the project status?
```

**What's Done:**

```
@CTO/Architect Agent: What's done and what's not done?
```

**Who's Doing What:**

```
@CTO/Architect Agent: Who's doing what right now?
```

---

## 🔍 Memory Storage Explained

### Where is Memory Stored?

**1. `.ai-knowledge-base.json` (PRIMARY)**

- **Location:** Root of project
- **Format:** JSON (human-readable)
- **Contains:** Everything (status, tasks, decisions, gaps)
- **Persistence:** ✅ Survives chat restarts
- **Version Control:** ✅ Tracked in git
- **Used By:** All agents

**2. Vector DB (Chroma) - OPTIONAL**

- **Location:** `.ai-memory/chroma/` (local) or cloud
- **Format:** Vector embeddings
- **Contains:** Code patterns, legal knowledge, best practices
- **Persistence:** ✅ Survives restarts
- **Used By:** Law Intelligence, Mastermind, Document Intelligence

**3. PostgreSQL - APPLICATION DATA**

- **Location:** Database
- **Format:** Relational database
- **Contains:** User data, cases, documents
- **Used By:** All backend services (via APIs)

---

## 💡 Simple Answer

**Q: How do agents share memory?**
**A: Through `.ai-knowledge-base.json` - ONE FILE that all agents read and write to.**

**Q: How do agents communicate?**
**A: Through `.ai-knowledge-base.json` - Agent A updates file, Agent B reads file, sees update.**

**Q: Is it ChromaDB or files?**
**A: BOTH:**

- `.ai-knowledge-base.json` - Primary (structured, human-readable)
- ChromaDB - Semantic search (optional, for similarity)
- PostgreSQL - Application data (via APIs)

**Q: Who reviews architecture and finds gaps?**
**A: Product Manager/CTO Agent - Your single interface for everything.**

---

## 🚀 Quick Reference

### Your Main Interface

**Product Manager/CTO Agent** - For requirements, architecture, IRCC research

### Status Interface

**CTO/Architect Agent** - For project status and coordination

### Memory

**`.ai-knowledge-base.json`** - Single source of truth

### Communication

**File-based** - Agents read/write same file

### Operating Model

**Simple coordination** - Through shared knowledge base

---

## 📚 Documentation

- **Product Manager/CTO Guide:** `docs/PRODUCT_MANAGER_CTO_GUIDE.md`
- **Operating Model:** `docs/AGENT_OPERATING_MODEL.md`
- **Communication Guide:** `docs/HOW_AGENTS_COMMUNICATE.md`
- **Agent Prompts:** `.cursor/agent-prompts/`

---

## 🎉 Summary

**Your Questions Answered:**

1. ✅ **Who reviews architecture?** → Product Manager/CTO Agent
2. ✅ **Who finds requirement gaps?** → Product Manager/CTO Agent
3. ✅ **Who researches IRCC?** → Product Manager/CTO Agent (with Browser MCP)
4. ✅ **Who coordinates testing?** → Product Manager/CTO Agent (with QA Agent)
5. ✅ **How do agents share memory?** → Through `.ai-knowledge-base.json`
6. ✅ **How do agents communicate?** → Through `.ai-knowledge-base.json`
7. ✅ **Is it ChromaDB or files?** → Both: `.ai-knowledge-base.json` (primary) + ChromaDB (semantic)

**Your Setup:**

- ✅ Product Manager/CTO Agent - Your main interface
- ✅ CTO/Architect Agent - Status reporting
- ✅ `.ai-knowledge-base.json` - Single source of truth
- ✅ All agents coordinate through this file
- ✅ Memory persists across sessions

---

**Everything is set up! Just ask your Product Manager/CTO Agent anything! 🚀**
