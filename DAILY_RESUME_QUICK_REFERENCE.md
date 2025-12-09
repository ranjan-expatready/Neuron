# Daily Resume Quick Reference

## How to Resume Work Every Day

**Date:** December 1, 2025

---

## 🎯 The Simple Answer

**Every day, just say:**

```
@Product Manager/CTO Agent: Good morning. What's the status? Continue work.
```

**Agent will:**

1. ✅ Read knowledge base (`.ai-knowledge-base.json`)
2. ✅ Know everything from yesterday
3. ✅ Report status
4. ✅ Continue work seamlessly

**That's it!** No context loss. Full statefulness.

---

## 🧠 How Memory Works

### Two-Layer Memory:

1. **`.ai-knowledge-base.json`** (PRIMARY)

   - ✅ Human-readable JSON file
   - ✅ Version-controlled (Git)
   - ✅ Contains: Status, tasks, decisions, progress
   - ✅ Persists across all sessions
   - ✅ All agents read/write this

2. **ChromaDB** (SECONDARY - Optional)
   - ✅ Vector database for semantic search
   - ✅ Used for deep context queries
   - ✅ Not required for daily work

---

## 📋 Daily Workflow

### Morning (Start Your Day):

```
@Product Manager/CTO Agent: Good morning. What's the status? What should we focus on today?
```

**Agent:**

- Reads knowledge base
- Reports yesterday's progress
- Recommends today's priorities
- Continues work

### During Day (Continue Work):

```
@Product Manager/CTO Agent: Continue with current tasks.
```

**Agent:**

- Reads knowledge base
- Sees what's in progress
- Continues seamlessly

### End of Day (Wrap Up):

```
@Product Manager/CTO Agent: End of day summary. What's done? What's next?
```

**Agent:**

- Updates knowledge base with progress
- Reports summary
- Sets up tomorrow

### Next Day (Resume):

```
@Product Manager/CTO Agent: Good morning. Resume work.
```

**Agent:**

- Reads knowledge base
- Knows everything from yesterday
- Continues seamlessly

---

## 🔍 What Persists Across Sessions

### ✅ Always Persists:

- Project status and completion percentage
- All completed tasks
- All in-progress tasks
- All decisions and discussions
- Architecture state
- Requirements gaps
- Current phase and milestones
- Agent assignments

### ✅ How It Persists:

- `.ai-knowledge-base.json` is a **file in your repository**
- It's **version-controlled** (Git)
- It's **always available** to all agents
- It's **human-readable** (you can check it anytime)

### ✅ When It Updates:

- After each task completion
- After each decision
- After each status change
- At end of day
- When you ask for status

---

## 🚀 Quick Commands

### Resume Work:

```
@Product Manager/CTO Agent: Resume work.
```

### Check Status:

```
@Product Manager/CTO Agent: What's the status?
```

### Continue Current Tasks:

```
@Product Manager/CTO Agent: Continue with current tasks.
```

### End of Day:

```
@Product Manager/CTO Agent: End of day summary.
```

---

## 💡 Key Points

1. **No Setup Needed:** Knowledge base persists automatically
2. **No Context Loss:** Everything saved in knowledge base
3. **Simple Commands:** Just ask agent to continue
4. **Full Statefulness:** Agent knows everything from previous sessions
5. **Human-Readable:** You can check knowledge base anytime

---

## 📊 Example: Week-Long Work

### Monday:

```
You: @Product Manager/CTO Agent: Start Phase 1.
Agent: Creates plan, starts work, updates knowledge base
```

### Tuesday:

```
You: @Product Manager/CTO Agent: Good morning. Status?
Agent: Reads knowledge base → Reports progress → Continues
```

### Wednesday:

```
You: @Product Manager/CTO Agent: Continue work.
Agent: Reads knowledge base → Continues seamlessly
```

### Thursday:

```
You: @Product Manager/CTO Agent: Status update.
Agent: Reads knowledge base → Reports → Continues
```

### Friday:

```
You: @Product Manager/CTO Agent: End of week summary.
Agent: Updates knowledge base → Reports → Sets up next week
```

### Next Monday:

```
You: @Product Manager/CTO Agent: Resume work.
Agent: Reads knowledge base → Knows everything → Continues
```

**Every day, agent knows exactly where it left off!**

---

## ✅ Summary

**How to Resume:**

1. Tag agent: `@Product Manager/CTO Agent`
2. Say: "Good morning. Status? Continue work."
3. Agent reads knowledge base
4. Agent continues seamlessly

**Memory:**

- Primary: `.ai-knowledge-base.json` (human-readable, version-controlled)
- Secondary: ChromaDB (optional, for semantic search)

**Statefulness:**

- ✅ Knowledge base persists across sessions
- ✅ Agents read at start of each session
- ✅ Work continues from saved state
- ✅ No context loss

**Daily Pattern:**

- Morning: Check status, continue work
- During day: Continue current tasks
- End of day: Summary, update knowledge base
- Next day: Resume seamlessly

---

**You're ready! Every day, just tag the agent and say "Continue work." 🚀**
