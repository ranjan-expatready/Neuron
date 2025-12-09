# Quick Reference: Progressive Requirements Coverage

## How CTO Ensures All Requirements Are Covered

---

## 🎯 The Simple Answer

**CTO Agent will:**

1. ✅ Read requirements before every task
2. ✅ Check what's already covered
3. ✅ Identify gaps during implementation
4. ✅ Research IRCC for legal requirements
5. ✅ Ask you for business decisions
6. ✅ Track coverage systematically

---

## 📋 Master Prompt Enhancement

**Add this to your master prompt:**

```
@Product Manager/CTO Agent:

[YOUR TASK]

Read knowledge base first. **Check requirements coverage** - what's covered? What's missing? **During implementation, identify gaps** - research IRCC if legal, ask me if business decision. **Update requirements coverage**. Use FAANG-style development. Coordinate with agents. Ensure 80%+ coverage. Report status and coverage progress.

Proceed.
```

---

## 🔄 How It Works

### Before Task:

- CTO reads requirements from spec
- Checks what's already covered
- Plans what needs to be covered

### During Task:

- CTO implements
- Finds gap → **Research IRCC** (if legal) or **Ask you** (if business)
- Updates coverage
- Continues implementation

### After Task:

- CTO verifies all requirements covered
- Updates coverage percentage
- Reports progress

---

## 📊 Coverage Tracking

**In Knowledge Base:**

- `requirements_coverage.sections[]` - What's covered
- `requirements_coverage.gaps[]` - What's missing
- `requirements_coverage.research_queue[]` - What needs IRCC research
- `requirements_coverage.user_guidance_needed[]` - What needs your input

---

## ✅ What This Ensures

**Always:**

- ✅ Progressive coverage of all requirements
- ✅ Gap identification during implementation
- ✅ Research for legal requirements
- ✅ User guidance for business decisions
- ✅ No requirements missed

---

**That's it! CTO will progressively cover all requirements and fill gaps! 🚀**
