# TestSprite Monitoring Guide

## How to Know If TestSprite Is Stuck or Processing

**Date:** December 1, 2025
**Purpose:** Help monitor TestSprite operations and detect if stuck

---

## 🔍 How to Check If TestSprite Is Running

### Method 1: Check Knowledge Base Status

**Check agent coordination:**

```bash
cat .ai-knowledge-base.json | jq '.agent_coordination.coordination_log[-5:]'
```

**Look for:**

- `event: "test_plan_generated"` - TestSprite started
- `event: "tests_executing"` - TestSprite running
- `event: "tests_completed"` - TestSprite finished

---

### Method 2: Check Test Results

**Check test results:**

```bash
cat .ai-knowledge-base.json | jq '.test_results'
```

**Look for:**

- `last_run` timestamp - When tests last ran
- `recent_runs` - Recent test executions
- Status updates

---

### Method 3: Check Process Status

**Check if TestSprite process is running:**

```bash
ps aux | grep testsprite
```

**Or check Node processes:**

```bash
ps aux | grep node
```

---

### Method 4: Check TestSprite Output Files

**TestSprite creates output files:**

```bash
# Check for test reports
ls -la testsprite-reports/
ls -la test-reports/
ls -la coverage/

# Check for test plan files
find . -name "*test*plan*" -type f
find . -name "*testsprite*" -type f
```

---

## ⏱️ Expected Duration

### TestSprite Bootstrap:

- **Normal:** 2-5 minutes
- **Large codebase:** 5-15 minutes
- **First time:** 10-20 minutes (analyzing entire codebase)

### Test Generation:

- **Small feature:** 1-3 minutes
- **Medium feature:** 3-10 minutes
- **Large feature:** 10-30 minutes

### Test Execution:

- **Unit tests:** 30 seconds - 2 minutes
- **Integration tests:** 2-10 minutes
- **Full suite:** 10-30 minutes

---

## 🚨 Signs It's Stuck

### Red Flags:

- ⚠️ Running > 30 minutes without output
- ⚠️ No file changes in last 10 minutes
- ⚠️ No knowledge base updates in last 10 minutes
- ⚠️ Process shows 0% CPU usage
- ⚠️ No new test files created

### Normal Signs (Still Processing):

- ✅ Recent file changes
- ✅ Knowledge base updates
- ✅ Process using CPU
- ✅ New test files appearing
- ✅ Logs showing activity

---

## 🔧 How to Check Status

### Quick Status Check:

**Ask Product Manager/CTO Agent:**

```
@Product Manager/CTO Agent: What's the status of TestSprite? Is it still running?
```

**Product Manager/CTO Agent will:**

- Check knowledge base
- Check process status
- Report current state

---

### Detailed Status Check:

**Check coordination log:**

```bash
# Last 10 coordination events
cat .ai-knowledge-base.json | jq '.agent_coordination.coordination_log[-10:]'
```

**Check for TestSprite activity:**

```bash
# Filter for TestSprite events
cat .ai-knowledge-base.json | jq '.agent_coordination.coordination_log[] | select(.agent == "TestSprite Agent")'
```

---

## 🛠️ Troubleshooting

### If Stuck (> 30 minutes):

#### Step 1: Cancel and Check Logs

1. Click "Cancel" button in IDE
2. Check for error messages
3. Check knowledge base for errors

#### Step 2: Check for Errors

```bash
# Check for error logs
find . -name "*.log" -type f | xargs grep -i error
find . -name "*testsprite*" -type f | xargs grep -i error
```

#### Step 3: Check System Resources

```bash
# Check memory
free -h  # Linux
vm_stat  # macOS

# Check disk space
df -h

# Check CPU
top
```

#### Step 4: Retry with Smaller Scope

**If bootstrap is stuck, try:**

```
@Product Manager/CTO Agent: Bootstrap TestSprite with scope "diff" instead of "codebase"
```

**Or skip bootstrap and generate tests directly:**

```
@Product Manager/CTO Agent: Generate test plan for backend without bootstrap
```

---

## 📊 Monitoring Commands

### Real-Time Monitoring:

**Watch knowledge base updates:**

```bash
watch -n 5 'cat .ai-knowledge-base.json | jq ".agent_coordination.coordination_log[-3:]"'
```

**Watch for new files:**

```bash
watch -n 5 'find . -name "*test*" -type f -mmin -5 | head -10'
```

**Watch process:**

```bash
watch -n 5 'ps aux | grep testsprite'
```

---

## ✅ What TestSprite Does (Why It Takes Time)

### Bootstrap Process:

1. **Codebase Analysis** (2-5 min)

   - Scans all files
   - Analyzes structure
   - Identifies testable components

2. **Test Plan Generation** (3-10 min)

   - Creates test structure
   - Generates test cases
   - Defines test scenarios

3. **Test Code Generation** (5-15 min)

   - Generates test files
   - Creates test fixtures
   - Sets up test infrastructure

4. **Test Execution** (2-10 min)
   - Runs generated tests
   - Collects results
   - Generates reports

**Total: 12-40 minutes for full bootstrap**

---

## 🎯 Quick Status Commands

### Check If Running:

```bash
# Method 1: Process check
ps aux | grep -i testsprite

# Method 2: Knowledge base check
cat .ai-knowledge-base.json | jq '.agent_coordination.coordination_log[-1]'

# Method 3: File changes
find . -name "*test*" -type f -mmin -5
```

### Check Progress:

```bash
# Last coordination event
cat .ai-knowledge-base.json | jq '.agent_coordination.coordination_log[-1]'

# Test results
cat .ai-knowledge-base.json | jq '.test_results.last_run'
```

---

## 🚀 Best Practices

### 1. Use Smaller Scope First:

- Start with `"diff"` scope (only changed files)
- Then expand to `"codebase"` if needed

### 2. Monitor Progress:

- Check knowledge base every 5 minutes
- Watch for file changes
- Monitor process status

### 3. Set Timeouts:

- If > 30 minutes, cancel and investigate
- Try smaller scope
- Check for errors

### 4. Use Incremental Approach:

- Bootstrap once
- Generate tests incrementally
- Run tests in batches

---

## 📋 Status Indicators

### ✅ Still Processing (Normal):

- Recent knowledge base updates
- New test files appearing
- Process using CPU
- Logs showing activity
- File timestamps updating

### ⚠️ Possibly Stuck:

- No updates for 10+ minutes
- Process at 0% CPU
- No new files
- No knowledge base updates

### 🚨 Definitely Stuck:

- No updates for 30+ minutes
- Process not responding
- No file changes
- Error messages in logs

---

## 🔄 What to Do

### If Still Processing (< 30 minutes):

- ✅ Wait - TestSprite can take 20-30 minutes for full bootstrap
- ✅ Monitor knowledge base for updates
- ✅ Check for new test files
- ✅ Be patient - first bootstrap takes longest

### If Stuck (> 30 minutes):

1. **Cancel** the operation
2. **Check logs** for errors
3. **Try smaller scope** (`"diff"` instead of `"codebase"`)
4. **Ask Product Manager/CTO Agent** for status
5. **Retry** with different parameters

---

## 💡 Pro Tips

### 1. Start Small:

```
@Product Manager/CTO Agent: Bootstrap TestSprite for backend only, scope "diff"
```

### 2. Monitor Progress:

```
@Product Manager/CTO Agent: What's TestSprite status? Show me progress
```

### 3. Check Results:

```
@Product Manager/CTO Agent: Show me TestSprite test results
```

### 4. If Stuck:

```
@Product Manager/CTO Agent: TestSprite seems stuck, cancel and try smaller scope
```

---

## ✅ Summary

### How to Know If Processing:

- ✅ Check knowledge base for updates
- ✅ Check for new test files
- ✅ Monitor process CPU usage
- ✅ Check coordination log

### Expected Duration:

- **Bootstrap:** 10-20 minutes (first time)
- **Test Generation:** 3-10 minutes
- **Test Execution:** 2-10 minutes

### If Stuck:

- ⚠️ Cancel after 30 minutes
- ⚠️ Check for errors
- ⚠️ Try smaller scope
- ⚠️ Ask Product Manager/CTO Agent

---

**TestSprite can take time, especially on first bootstrap. Monitor progress and be patient! ⏱️**
