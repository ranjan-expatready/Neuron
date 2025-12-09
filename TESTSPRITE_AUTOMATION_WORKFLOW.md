# TestSprite Automation Workflow

## How Tests Run Automatically in Multi-Agent System

**Date:** December 1, 2025

---

## 🎯 The Goal

**Automatically test all code changes** so we're never building blindly. Every feature is tested before completion.

---

## 🔄 Automatic Testing Flow

### Flow 1: After Code Completion (Automatic)

```
Backend API Agent completes code
         ↓
Product Manager/CTO Agent detects completion
         ↓
Automatically invokes TestSprite
         ↓
Tests generated and executed
         ↓
Results logged in knowledge base
         ↓
If pass: Mark complete ✅
If fail: Assign fix → Re-test
```

### Flow 2: Before Assignment (Proactive)

```
Product Manager/CTO Agent assigns task
         ↓
Generates test plan using TestSprite
         ↓
Shares test plan with agent
         ↓
Agent implements with tests in mind
         ↓
Tests already planned, easier to pass
```

### Flow 3: Continuous Monitoring

```
Any code change detected
         ↓
TestSprite monitors changes
         ↓
Auto-generates tests for new code
         ↓
Runs tests automatically
         ↓
Reports to Product Manager/CTO Agent
```

---

## 📋 Product Manager/CTO Agent Automation

### Automatic Actions:

1. **After Agent Completes Code:**

   ```python
   # Pseudo-code
   if agent_completed_code:
       test_results = testsprite_generate_code_and_execute(
           project_path="/Users/ranjansingh/Projects/Neuron-2",
           project_name="Neuron-2",
           test_scope="diff"  # Only test changed code
       )
       log_test_results(test_results)

       if test_results.tests_failed > 0:
           assign_fix_to_agent()
       else:
           mark_task_complete()
   ```

2. **When Assigning Work:**

   ```python
   # Pseudo-code
   if assigning_backend_task:
       test_plan = testsprite_generate_backend_test_plan(
           project_path="/Users/ranjansingh/Projects/Neuron-2"
       )
       share_test_plan_with_agent(test_plan)
   ```

3. **Weekly/Milestone:**
   ```python
   # Pseudo-code
   if milestone_complete:
       test_plan = testsprite_generate_backend_test_plan(
           project_path="/Users/ranjansingh/Projects/Neuron-2"
       )
       test_results = testsprite_generate_code_and_execute(
           project_path="/Users/ranjansingh/Projects/Neuron-2",
           test_scope="codebase"  # Full codebase
       )
       review_coverage(test_results)
   ```

---

## 🚀 How to Use

### Method 1: Automatic (Recommended)

**Product Manager/CTO Agent automatically:**

- Invokes TestSprite after code completion
- Generates tests
- Runs tests
- Reports results
- Ensures quality

**You don't need to do anything!** It happens automatically.

---

### Method 2: On-Demand

**You can request testing:**

```
@Product Manager/CTO Agent: Run tests for recent changes
```

**Agent:**

- Invokes TestSprite
- Generates and runs tests
- Reports results

---

### Method 3: Before Starting Work

**You can request test plan:**

```
@Product Manager/CTO Agent: Generate test plan for document upload feature
```

**Agent:**

- Invokes TestSprite
- Generates test plan
- Shares with implementing agent

---

## 📊 Knowledge Base Integration

### Test Results Structure:

```json
{
  "test_results": {
    "last_run": "2025-12-01T12:00:00",
    "overall_coverage": 75,
    "total_tests": 80,
    "passing_tests": 78,
    "failing_tests": 2,
    "coverage_threshold": 80,
    "meets_threshold": false,
    "recent_runs": [
      {
        "task_id": "CASE_MANAGEMENT",
        "timestamp": "2025-12-01T12:00:00",
        "tests_generated": 15,
        "tests_passed": 14,
        "tests_failed": 1,
        "coverage": 85,
        "status": "partial_pass",
        "agent": "Backend API Agent",
        "files_tested": ["backend/app/api/routes/cases.py"],
        "action_required": "Fix failing test"
      }
    ]
  }
}
```

---

## ✅ Quality Gates

### Before Marking Complete:

1. ✅ Tests generated
2. ✅ Tests executed
3. ✅ All tests pass
4. ✅ Coverage meets threshold (80%+)
5. ✅ No critical issues

**If any fail:**

- Fix assigned to agent
- Re-test required
- Only mark complete when all pass

---

## 🎯 Best Practices

### 1. Test After Every Feature

- Automatic after code completion
- No manual intervention needed
- Quality ensured

### 2. Test Plan Before Implementation

- Generate test plan when assigning
- Agent knows what to test
- Easier to pass tests

### 3. Continuous Monitoring

- Track coverage
- Monitor test results
- Ensure quality standards

### 4. Automatic Re-testing

- Re-run after fixes
- Verify all pass
- Only complete when green

---

## 📋 Example: Complete Automation

### Day 1: Assignment

```
You: @Product Manager/CTO Agent: Implement document upload

Product Manager/CTO Agent:
1. Breaks down task
2. Generates test plan (TestSprite)
3. Assigns to Backend API Agent
4. Shares test plan
```

### Day 2: Implementation

```
Backend API Agent:
1. Implements feature
2. Updates knowledge base: "completed"

Product Manager/CTO Agent (Automatic):
1. Detects completion
2. Invokes TestSprite: Generate and run tests
3. Results: 12 tests, 11 passed, 1 failed
4. Updates knowledge base with results
5. Assigns fix to Backend API Agent
```

### Day 3: Fix

```
Backend API Agent:
1. Fixes failing test
2. Updates knowledge base

Product Manager/CTO Agent (Automatic):
1. Detects fix
2. Invokes TestSprite: Re-run tests
3. All tests pass ✅
4. Marks feature complete
5. Updates knowledge base
```

**All automatic! No manual testing needed.**

---

## 🚀 Quick Commands

### Request Testing:

```
@Product Manager/CTO Agent: Run tests for recent changes
```

### Request Test Plan:

```
@Product Manager/CTO Agent: Generate test plan for [feature]
```

### Check Test Status:

```
@Product Manager/CTO Agent: What's our test coverage?
```

### Re-run Tests:

```
@Product Manager/CTO Agent: Re-run all tests
```

---

## ✅ Summary

### Automatic Testing:

1. **After Code Completion:**

   - Product Manager/CTO Agent automatically invokes TestSprite
   - Tests generated and executed
   - Results logged
   - Quality ensured

2. **Before Assignment:**

   - Test plan generated
   - Shared with agent
   - Agent implements with tests in mind

3. **Continuous:**
   - Coverage monitored
   - Quality tracked
   - Standards enforced

### Result:

- ✅ **No blind building** - Everything tested
- ✅ **Automatic quality** - Tests run automatically
- ✅ **Coverage ensured** - 80%+ threshold
- ✅ **Quality gates** - Only complete when tests pass

---

**TestSprite is now fully integrated and automatic! 🚀**
