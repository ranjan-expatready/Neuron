# Product Manager/CTO Agent Guide

## Your Single Interface for Requirements, Architecture, and IRCC Research

---

## 🎯 Who This Agent Is

The **Product Manager/CTO Agent** combines:

- **Product Manager** - Requirements, features, acceptance criteria
- **CTO/Architect** - Architecture review, technical decisions
- **Requirements Analyst** - Gap analysis, IRCC research

**This is your single person** for:

- ✅ Architecture review
- ✅ Requirement gap analysis
- ✅ IRCC website research
- ✅ Acceptance criteria
- ✅ Testing coordination
- ✅ End-to-end product management

---

## 📁 Single Source of Truth

**ONE FILE:** `.ai-knowledge-base.json`

This agent:

- ✅ Always reads this file first
- ✅ Always updates this file when work is done
- ✅ Uses it as the ONLY source of truth
- ✅ Never relies on memory from previous sessions

---

## 🔍 What This Agent Does

### 1. Architecture Review

**Reviews:**

- Current architecture vs. requirements
- Missing components
- Scalability issues
- Security gaps
- Compliance issues

**How to ask:**

```
@Product Manager/CTO Agent: Review the current architecture and identify gaps compared to docs/master_spec_refined.md
```

---

### 2. Requirement Gap Analysis

**Analyzes:**

- What's required vs. what's built
- Missing features
- Incomplete implementations
- Compliance gaps

**How to ask:**

```
@Product Manager/CTO Agent: Analyze requirement gaps. What's missing from the current implementation?
```

---

### 3. IRCC Research

**Researches:**

- IRCC website for official requirements
- Latest policy changes
- Case type requirements
- Document requirements
- Eligibility criteria

**How to ask:**

```
@Product Manager/CTO Agent: Research IRCC website for Express Entry requirements. Update the knowledge base with findings.
```

**Note:** Uses Browser MCP when available, or guides you to research manually.

---

### 4. Acceptance Criteria

**Defines:**

- Feature acceptance criteria
- Test requirements
- Quality standards
- Completion criteria

**Works with:**

- QA Agent for test plans
- Other agents for implementation

**How to ask:**

```
@Product Manager/CTO Agent: Define acceptance criteria for document upload feature. Work with QA Agent to create test plan.
```

---

### 5. Testing Coordination

**Coordinates:**

- With QA Agent for test coverage
- Test plan creation
- Acceptance validation
- Quality sign-off

**How to ask:**

```
@Product Manager/CTO Agent: Review test coverage with QA Agent. Ensure 80%+ coverage for authentication.
```

---

## 🔄 How It Works with Other Agents

### With QA Agent

**Product Manager/CTO Agent:**

- Defines acceptance criteria
- Reviews test plans
- Validates test coverage
- Signs off on quality

**QA Agent:**

- Creates test plans
- Writes tests
- Reports coverage
- Validates acceptance

**Communication:**

- Through `.ai-knowledge-base.json`
- CTO defines criteria → QA implements tests
- QA reports results → CTO validates

---

### With Backend/Frontend Agents

**Product Manager/CTO Agent:**

- Reviews architecture
- Validates implementations
- Ensures requirements met
- Guides technical direction

**Backend/Frontend Agents:**

- Implement features
- Follow architecture
- Meet requirements
- Update knowledge base

**Communication:**

- Through `.ai-knowledge-base.json`
- CTO reviews → Agents implement
- Agents complete → CTO validates

---

### With Law Intelligence Agent

**Product Manager/CTO Agent:**

- Coordinates IRCC research
- Validates legal requirements
- Ensures compliance
- Reviews rule proposals

**Law Intelligence Agent:**

- Scrapes IRCC website
- Extracts rules
- Proposes rule changes
- Updates knowledge base

**Communication:**

- Through `.ai-knowledge-base.json`
- CTO requests research → Law Agent researches
- Law Agent finds rules → CTO validates

---

## 📋 Example Workflows

### Workflow 1: Architecture Review

**You ask:**

```
@Product Manager/CTO Agent: Review architecture and find gaps
```

**Agent does:**

1. Reads `.ai-knowledge-base.json` for current state
2. Reads `docs/master_spec_refined.md` for requirements
3. Reads `docs/architecture/system_architecture.md` for target architecture
4. Compares current vs. target
5. Identifies gaps
6. Updates knowledge base with findings
7. Reports gaps to you

---

### Workflow 2: IRCC Research

**You ask:**

```
@Product Manager/CTO Agent: Research IRCC for Express Entry requirements
```

**Agent does:**

1. Identifies what needs research
2. Uses Browser MCP (if available) to navigate IRCC website
3. Extracts official requirements
4. Updates knowledge base with findings
5. Creates requirement proposals
6. Reports findings to you

**If Browser MCP not available:**

- Guides you to research manually
- Provides specific URLs to check
- Updates knowledge base with your findings

---

### Workflow 3: Acceptance Criteria

**You ask:**

```
@Product Manager/CTO Agent: Define acceptance criteria for document upload
```

**Agent does:**

1. Reviews feature requirements
2. Defines acceptance criteria
3. Works with QA Agent for test plan
4. Documents in knowledge base
5. Validates with stakeholders
6. Reports criteria to you

---

## 🎯 Key Questions This Agent Answers

### "What are the requirement gaps?"

- Reads knowledge base
- Compares with specification
- Researches IRCC if needed
- Lists all gaps
- Prioritizes

### "Is the architecture correct?"

- Reviews current architecture
- Compares with target
- Identifies missing components
- Validates against requirements
- Proposes improvements

### "What does IRCC require?"

- Researches IRCC website
- Extracts official requirements
- Updates knowledge base
- Creates requirement proposals
- Ensures compliance

### "What are the acceptance criteria?"

- Reviews feature requirements
- Defines criteria
- Works with QA Agent
- Documents in knowledge base
- Validates completion

---

## 🔧 Tools Available

### For IRCC Research

- **Browser MCP** - Navigate IRCC website (when available)
- **Manual Research** - Guides you to specific pages
- **Knowledge Base** - Stores findings

### For Architecture Review

- `docs/master_spec_refined.md` - Requirements
- `docs/architecture/system_architecture.md` - Target architecture
- `.ai-knowledge-base.json` - Current state

### For Requirements

- Master specification
- Gap analysis documents
- IRCC official sources
- Knowledge base

---

## 📊 How Memory is Shared

### With QA Agent

**Shared through:**

- `.ai-knowledge-base.json` - Task status, acceptance criteria
- Vector DB - Test patterns, best practices
- Direct coordination - When needed

**Example:**

1. CTO defines acceptance criteria → Updates knowledge base
2. QA Agent reads knowledge base → Sees criteria
3. QA Agent writes tests → Updates knowledge base
4. CTO validates → Signs off

---

### With All Agents

**Shared through:**

- `.ai-knowledge-base.json` - Primary (structured, human-readable)
- Vector DB - Semantic search (code patterns, knowledge)
- PostgreSQL - Application data (via APIs)

**All agents:**

- Read knowledge base before starting
- Update knowledge base when done
- Share context through file
- Coordinate through file

---

## 🚀 Quick Start

### Ask Architecture Review

```
@Product Manager/CTO Agent: Review architecture and identify gaps
```

### Ask Requirement Analysis

```
@Product Manager/CTO Agent: Analyze requirement gaps. Research IRCC if needed.
```

### Ask Acceptance Criteria

```
@Product Manager/CTO Agent: Define acceptance criteria for [feature]. Work with QA Agent.
```

### Ask IRCC Research

```
@Product Manager/CTO Agent: Research IRCC website for [case type] requirements
```

---

## 📚 Documentation

- **Agent Prompt:** `.cursor/agent-prompts/product-manager-cto-agent.md`
- **Operating Model:** `docs/AGENT_OPERATING_MODEL.md`
- **Communication Guide:** `docs/HOW_AGENTS_COMMUNICATE.md`
- **Knowledge Base:** `.ai-knowledge-base.json`

---

## 🎉 Summary

**Your Product Manager/CTO Agent:**

- ✅ Reviews architecture
- ✅ Finds requirement gaps
- ✅ Researches IRCC website
- ✅ Defines acceptance criteria
- ✅ Coordinates with QA Agent
- ✅ Uses `.ai-knowledge-base.json` as single source of truth
- ✅ Works across all sessions

**Memory Sharing:**

- ✅ `.ai-knowledge-base.json` - Primary (structured, human-readable)
- ✅ Vector DB - Semantic search (optional)
- ✅ PostgreSQL - Application data (via APIs)

**Communication:**

- ✅ File-based coordination (current)
- ✅ Event-driven (future)
- ✅ API-based (future)

---

**Your Product Manager/CTO Agent is ready! Just ask it anything about requirements, architecture, or IRCC research!**
