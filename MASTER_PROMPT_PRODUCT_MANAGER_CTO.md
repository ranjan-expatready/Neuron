# Master Prompt for Product Manager/CTO Agent

## Use This Prompt Anytime to Get Work Done

**Purpose:** Single prompt that ensures FAANG-level development with multi-agent coordination and persistent memory

---

## 🎯 Master Prompt (Copy & Paste)

```
@Product Manager/CTO Agent:

I need you to [DESCRIBE YOUR GOAL/TASK HERE].

Please ensure:

1. **Read Knowledge Base First:**
   - Read `.ai-knowledge-base.json` to understand current state
   - Check what's done, what's in progress, what's next
   - Review agent coordination status
   - Check test results and coverage

2. **Follow FAANG-Style Development:**
   - Use ATDD (Acceptance Test-Driven Development) for features
   - Use Contract Testing for APIs
   - Use TDD for implementation
   - Use Property-Based Testing for complex logic
   - Ensure 80%+ test coverage

3. **Coordinate Multi-Agent System:**
   - Break down task into specific assignments
   - Assign to appropriate agents:
     * TestSprite Agent → Generate test plans first (TDD)
     * Backend API Agent → Implement backend APIs
     * Frontend Agent → Implement frontend UI
     * TestSprite Agent → Test after completion
   - Log all assignments in knowledge base `agent_coordination` section
   - Track progress and report status

4. **Use Persistent Memory:**
   - Update `.ai-knowledge-base.json` with:
     * Current task status
     * Agent assignments
     * Progress updates
     * Test results
     * Decisions made
   - Log all discussions in `cto_notes` section
   - Never rely on memory from previous sessions

5. **Follow Best Practices:**
   - Pre-commit hooks will run automatically (code quality)
   - All tests must pass before completion
   - Coverage must be 80%+
   - Security scans must pass
   - Code review checklist followed
   - Architecture compliance maintained

6. **Quality Gates:**
   - TestSprite Agent must approve before marking complete
   - All tests must pass
   - Coverage 80%+
   - No critical issues
   - All quality checks passed

7. **Report Status:**
   - What's assigned
   - What's in progress
   - What's completed
   - What's next
   - Any blockers

Please proceed with this task following all best practices and using the multi-agent system.
```

---

## 📋 Quick Use Examples

### Example 1: Implement New Feature

```
@Product Manager/CTO Agent:

I need you to implement document upload feature with OCR processing.

Please ensure:
1. Read knowledge base first
2. Use FAANG-style development (ATDD + Contract Testing + TDD)
3. Coordinate with TestSprite Agent for test plans
4. Assign to Backend API Agent and Frontend Agent
5. Update knowledge base with progress
6. Ensure 80%+ coverage
7. Report status

Please proceed.
```

---

### Example 2: Fix Bug

```
@Product Manager/CTO Agent:

I need you to fix the authentication bug where users can't login with long passwords.

Please ensure:
1. Read knowledge base first
2. Use TDD approach
3. TestSprite Agent generates tests first
4. Backend API Agent fixes the issue
5. TestSprite Agent tests and approves
6. Update knowledge base
7. Report status

Please proceed.
```

---

### Example 3: Check Status

```
@Product Manager/CTO Agent:

What's the current status? What's done, what's in progress, and what's next?

Please:
1. Read knowledge base
2. Check agent coordination
3. Check test results
4. Report comprehensive status
5. Recommend next steps

Please proceed.
```

---

### Example 4: Complete Phase 1

```
@Product Manager/CTO Agent:

Complete Phase 1 implementation with gold-class quality.

Please ensure:
1. Read knowledge base to see what's remaining
2. Break down into tasks
3. Use FAANG-style development
4. Coordinate all agents
5. Ensure all tests pass
6. Coverage 80%+
7. Update knowledge base
8. Report final status

Please proceed.
```

---

## 🎯 Master Prompt Template (Simplified)

```
@Product Manager/CTO Agent:

[YOUR TASK/GOAL]

Follow these steps:
1. Read `.ai-knowledge-base.json` first
2. Use FAANG-style development (ATDD + Contract + TDD)
3. Coordinate with TestSprite Agent and other agents
4. Update knowledge base with progress
5. Ensure 80%+ coverage and all tests pass
6. Report status

Proceed.
```

---

## 📋 Key Elements Always Include

### 1. Knowledge Base First:

Always start with: "Read `.ai-knowledge-base.json` first"

### 2. FAANG-Style Development:

- ATDD for features
- Contract Testing for APIs
- TDD for implementation

### 3. Multi-Agent Coordination:

- TestSprite Agent for testing
- Backend/Frontend Agents for implementation
- Log assignments in knowledge base

### 4. Persistent Memory:

- Update knowledge base
- Log in `cto_notes`
- Track in `agent_coordination`

### 5. Quality Gates:

- 80%+ coverage
- All tests pass
- TestSprite Agent approval

---

## 🚀 Quick Commands

### Start Development:

```
@Product Manager/CTO Agent: Implement [feature] using FAANG-style development. Coordinate with TestSprite Agent and other agents. Update knowledge base. Report status.
```

### Check Status:

```
@Product Manager/CTO Agent: What's the status? Read knowledge base and report what's done, in progress, and next.
```

### Fix Issue:

```
@Product Manager/CTO Agent: Fix [issue]. Use TDD approach with TestSprite Agent. Update knowledge base. Report status.
```

### Complete Feature:

```
@Product Manager/CTO Agent: Complete [feature] with gold-class quality. Ensure 80%+ coverage. TestSprite Agent must approve. Report status.
```

---

## ✅ What This Ensures

### Always:

- ✅ Reads knowledge base first (persistent memory)
- ✅ Uses FAANG-style development
- ✅ Coordinates multi-agent system
- ✅ Updates knowledge base
- ✅ Ensures quality gates
- ✅ Reports status

### Never:

- ❌ Relies on memory from previous sessions
- ❌ Skips testing
- ❌ Breaks working code
- ❌ Lowers quality standards

---

## 📋 Complete Master Prompt

```
@Product Manager/CTO Agent:

[YOUR TASK/GOAL HERE]

**Requirements:**
1. Read `.ai-knowledge-base.json` first to understand current state
2. Use FAANG-style development:
   - ATDD (Acceptance Test-Driven Development) for features
   - Contract Testing for APIs
   - TDD (Test-Driven Development) for implementation
   - Property-Based Testing for complex logic
3. Coordinate multi-agent system:
   - TestSprite Agent: Generate test plans first, then test after completion
   - Backend API Agent: Implement backend APIs
   - Frontend Agent: Implement frontend UI
   - Log all assignments in `agent_coordination` section
4. Use persistent memory:
   - Update `.ai-knowledge-base.json` with progress
   - Log discussions in `cto_notes` section
   - Track assignments in `agent_coordination` section
5. Follow best practices:
   - Pre-commit hooks (automatic)
   - All tests must pass
   - Coverage 80%+
   - Security scans must pass
   - Architecture compliance
6. Quality gates:
   - TestSprite Agent must approve
   - All tests pass
   - Coverage 80%+
   - No critical issues
7. Report status:
   - What's assigned
   - What's in progress
   - What's completed
   - What's next
   - Any blockers

Please proceed with this task following all best practices.
```

---

## 🎯 Simple Version (Copy This)

```
@Product Manager/CTO Agent:

[YOUR TASK]

Read knowledge base first. Use FAANG-style development (ATDD + Contract + TDD). Coordinate with TestSprite Agent and other agents. Update knowledge base. Ensure 80%+ coverage. Report status.

Proceed.
```

---

**Use this master prompt anytime to get work done with FAANG-level quality! 🚀**
