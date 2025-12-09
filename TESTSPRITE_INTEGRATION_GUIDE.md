# TestSprite MCP Integration Guide

## Automated Testing in Multi-Agent Development Workflow

**Date:** December 1, 2025
**Purpose:** Integrate TestSprite MCP for automated testing in multi-agent development

---

## 🎯 Overview

**TestSprite MCP** provides automated testing capabilities that integrate seamlessly with our multi-agent system. This guide explains how to use it effectively.

---

## 🔧 TestSprite MCP Capabilities

### Available Tools:

1. **`testsprite_bootstrap_tests`** - Initialize TestSprite
2. **`testsprite_generate_code_summary`** - Analyze codebase
3. **`testsprite_generate_standardized_prd`** - Generate PRD
4. **`testsprite_generate_frontend_test_plan`** - Frontend test plan
5. **`testsprite_generate_backend_test_plan`** - Backend test plan
6. **`testsprite_generate_code_and_execute`** - Generate and run tests
7. **`testsprite_rerun_tests`** - Re-run tests

---

## 🚀 Integration Strategy

### Strategy 1: Automatic Testing After Code Changes

**Workflow:**

1. Agent completes code changes
2. Product Manager/CTO Agent automatically invokes TestSprite
3. Tests generated and executed
4. Results logged in knowledge base
5. If tests fail, agent fixes issues

### Strategy 2: Pre-Commit Testing

**Workflow:**

1. Agent finishes feature
2. TestSprite generates comprehensive tests
3. Tests run automatically
4. Only proceed if tests pass
5. Update knowledge base with test results

### Strategy 3: Continuous Testing

**Workflow:**

1. Agent makes code changes
2. TestSprite monitors changes
3. Auto-generates tests for new code
4. Runs tests continuously
5. Reports results to Product Manager/CTO Agent

---

## 📋 How Product Manager/CTO Agent Uses TestSprite

### When Assigning Work:

**Product Manager/CTO Agent:**

```
1. Assigns task to Backend API Agent: "Implement case management APIs"
2. Immediately invokes TestSprite:
   - Generate backend test plan
   - Set up test requirements
3. Updates knowledge base with test plan
4. Backend API Agent implements with tests in mind
```

### After Code Changes:

**Product Manager/CTO Agent:**

```
1. Backend API Agent completes implementation
2. Product Manager/CTO Agent invokes TestSprite:
   - Generate tests for new code
   - Execute tests
   - Report results
3. If tests fail:
   - Assign fix to Backend API Agent
   - Re-run tests
4. Update knowledge base with test results
```

### Weekly/Milestone Testing:

**Product Manager/CTO Agent:**

```
1. At milestone completion
2. Invoke TestSprite:
   - Generate comprehensive test plan
   - Run full test suite
   - Generate test report
3. Review coverage and quality
4. Update knowledge base
```

---

## 🔄 Automated Testing Workflow

### Step 1: Agent Completes Code

**Backend API Agent:**

- Implements feature
- Updates knowledge base: `status: "completed"`
- Files modified: `["backend/app/api/routes/cases.py"]`

### Step 2: Product Manager/CTO Agent Detects Completion

**Product Manager/CTO Agent:**

- Reads knowledge base
- Sees: "Backend API Agent completed case management APIs"
- **Automatically invokes TestSprite**

### Step 3: TestSprite Generates Tests

**TestSprite:**

- Analyzes code changes
- Generates test plan
- Creates test code
- Executes tests

### Step 4: Results Logged

**Product Manager/CTO Agent:**

- Receives test results
- Updates knowledge base:
  ```json
  {
    "test_results": {
      "task_id": "CASE_MANAGEMENT",
      "tests_generated": 15,
      "tests_passed": 14,
      "tests_failed": 1,
      "coverage": 85,
      "status": "partial_pass"
    }
  }
  ```

### Step 5: Fix if Needed

**If tests fail:**

- Product Manager/CTO Agent assigns fix to Backend API Agent
- Backend API Agent fixes issues
- TestSprite re-runs tests
- Process repeats until all pass

---

## 📊 Knowledge Base Integration

### Test Results Tracking:

```json
{
  "test_results": {
    "last_run": "2025-12-01T12:00:00",
    "overall_coverage": 75,
    "total_tests": 80,
    "passing_tests": 78,
    "failing_tests": 2,
    "recent_runs": [
      {
        "task_id": "CASE_MANAGEMENT",
        "timestamp": "2025-12-01T12:00:00",
        "tests_generated": 15,
        "tests_passed": 14,
        "tests_failed": 1,
        "coverage": 85,
        "agent": "Backend API Agent",
        "files_tested": ["backend/app/api/routes/cases.py"]
      }
    ]
  }
}
```

---

## 🎯 Best Practices

### 1. Test After Every Feature

**Product Manager/CTO Agent should:**

- Invoke TestSprite after each feature completion
- Generate tests for new code
- Ensure coverage before marking complete

### 2. Test Plan Before Implementation

**Product Manager/CTO Agent should:**

- Generate test plan when assigning work
- Share test plan with implementing agent
- Agent implements with tests in mind

### 3. Continuous Monitoring

**Product Manager/CTO Agent should:**

- Monitor test coverage
- Track test results
- Ensure quality standards

### 4. Automatic Re-testing

**Product Manager/CTO Agent should:**

- Re-run tests after fixes
- Verify all tests pass
- Only mark complete when tests pass

---

## 🔧 Implementation: Product Manager/CTO Agent Prompt

### Updated Workflow:

**When assigning work:**

```
1. Break down task
2. Generate test plan using TestSprite
3. Assign implementation task
4. Assign test task (with test plan)
```

**When work completed:**

```
1. Detect completion in knowledge base
2. Invoke TestSprite to generate tests
3. Execute tests
4. Review results
5. If pass: Mark complete
6. If fail: Assign fix
```

**Weekly/Milestone:**

```
1. Generate comprehensive test plan
2. Run full test suite
3. Review coverage
4. Update knowledge base
```

---

## 📋 Example: Complete Workflow

### Day 1: Assignment

**You:**

```
@Product Manager/CTO Agent: Implement document upload feature
```

**Product Manager/CTO Agent:**

1. Breaks down into tasks
2. **Invokes TestSprite:** `testsprite_generate_backend_test_plan`
3. Gets test plan for document upload
4. Assigns to Backend API Agent with test plan
5. Updates knowledge base

### Day 2: Implementation Complete

**Backend API Agent:**

- Completes implementation
- Updates knowledge base: `status: "completed"`

**Product Manager/CTO Agent (Automatic):**

1. Detects completion
2. **Invokes TestSprite:** `testsprite_generate_code_and_execute`
3. Tests generated and executed
4. Results: 12 tests, 11 passed, 1 failed
5. Updates knowledge base with results
6. Assigns fix to Backend API Agent

### Day 3: Fix and Re-test

**Backend API Agent:**

- Fixes failing test
- Updates knowledge base

**Product Manager/CTO Agent (Automatic):**

1. Detects fix
2. **Invokes TestSprite:** `testsprite_rerun_tests`
3. All tests pass
4. Marks feature complete
5. Updates knowledge base

---

## 🚀 Quick Commands

### Generate Test Plan:

```
@Product Manager/CTO Agent: Generate test plan for case management feature
```

**Agent invokes:** `testsprite_generate_backend_test_plan`

### Run Tests:

```
@Product Manager/CTO Agent: Run tests for recent changes
```

**Agent invokes:** `testsprite_generate_code_and_execute`

### Re-run Tests:

```
@Product Manager/CTO Agent: Re-run all tests
```

**Agent invokes:** `testsprite_rerun_tests`

### Check Test Coverage:

```
@Product Manager/CTO Agent: What's our test coverage?
```

**Agent reads:** Knowledge base test results

---

## 📊 TestSprite Configuration

### Project Settings:

```json
{
  "test_sprite": {
    "project_path": "/Users/ranjansingh/Projects/Neuron-2",
    "local_port": 8000,
    "type": "backend",
    "test_scope": "codebase",
    "coverage_threshold": 80,
    "auto_test": true,
    "test_on_completion": true
  }
}
```

---

## ✅ Integration Checklist

### Product Manager/CTO Agent:

- [x] Invoke TestSprite after code completion
- [x] Generate test plans before assignment
- [x] Track test results in knowledge base
- [x] Ensure tests pass before marking complete
- [x] Re-run tests after fixes
- [x] Monitor test coverage

### Backend/Frontend Agents:

- [x] Implement with tests in mind
- [x] Update knowledge base when complete
- [x] Fix issues if tests fail
- [x] Wait for test approval before marking done

### QA Agent:

- [x] Review test plans
- [x] Validate test coverage
- [x] Ensure quality standards
- [x] Sign off on test results

---

## 🎯 Summary

### How TestSprite Integrates:

1. **Product Manager/CTO Agent coordinates:**

   - Invokes TestSprite at right times
   - Tracks test results
   - Ensures quality

2. **Automatic Testing:**

   - After code completion
   - Before marking complete
   - After fixes

3. **Knowledge Base Tracking:**

   - Test results logged
   - Coverage tracked
   - Quality monitored

4. **Quality Assurance:**
   - No code marked complete without tests
   - Coverage requirements enforced
   - Continuous quality monitoring

---

**TestSprite is now integrated into your multi-agent workflow! 🚀**
