# Progressive Requirements Coverage

## How CTO Ensures All Requirements Are Covered

**Date:** December 2, 2025

---

## 🎯 Goal

Ensure the CTO/Product Manager Agent:

1. **Progressively expands** to cover all requirements
2. **Identifies gaps** during implementation
3. **Fills gaps** by researching (IRCC) or asking for user guidance
4. **Tracks coverage** systematically

---

## 📋 Requirements Tracking System

### Knowledge Base Structure

The `.ai-knowledge-base.json` includes a `requirements_coverage` section:

```json
{
  "requirements_coverage": {
    "master_spec": "docs/master_spec_refined.md",
    "prd": "docs/product/prd_canada_immigration_os.md",
    "architecture": "docs/architecture/system_architecture.md",
    "sections": [
      {
        "section_id": "PHASE_1_CORE",
        "section_name": "Phase 1: Core Features",
        "requirements": [
          {
            "req_id": "REQ_001",
            "description": "Client Portal - User Registration",
            "status": "completed",
            "coverage": 100,
            "implemented_in": [
              "backend/app/api/routes/auth.py",
              "frontend/src/pages/register.tsx"
            ],
            "tests": ["backend/tests/test_auth.py"],
            "completed_at": "2025-12-01T10:00:00"
          },
          {
            "req_id": "REQ_002",
            "description": "Case Management - CRUD Operations",
            "status": "in_progress",
            "coverage": 60,
            "implemented_in": ["backend/app/api/routes/cases.py"],
            "tests": [],
            "gaps_identified": [
              {
                "gap_id": "GAP_001",
                "description": "Missing case status workflow transitions",
                "source": "master_spec_refined.md Section 3.2.1",
                "action": "research_ircc",
                "research_url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/eligibility.html",
                "status": "pending"
              }
            ]
          }
        ],
        "overall_coverage": 80,
        "last_reviewed": "2025-12-02T10:00:00"
      }
    ],
    "gaps": [
      {
        "gap_id": "GAP_001",
        "description": "Missing case status workflow transitions",
        "priority": "P1",
        "source": "master_spec_refined.md",
        "action_required": "research_ircc",
        "research_url": "https://www.canada.ca/en/immigration-refugees-citizenship/...",
        "status": "identified",
        "identified_at": "2025-12-02T10:00:00",
        "assigned_to": "Product Manager/CTO Agent"
      }
    ],
    "research_queue": [
      {
        "research_id": "RESEARCH_001",
        "topic": "Express Entry case status transitions",
        "url": "https://www.canada.ca/en/immigration-refugees-citizenship/...",
        "status": "pending",
        "priority": "P1"
      }
    ],
    "user_guidance_needed": [
      {
        "guidance_id": "GUIDANCE_001",
        "question": "What should be the case status workflow for Express Entry applications?",
        "context": "Implementing case management CRUD, need to define status transitions",
        "status": "pending",
        "created_at": "2025-12-02T10:00:00"
      }
    ]
  }
}
```

---

## 🔄 Progressive Coverage Workflow

### Step 1: Before Starting Any Task

**CTO Agent MUST:**

1. **Read Requirements:**

   - Read `docs/master_spec_refined.md`
   - Read `docs/product/prd_canada_immigration_os.md`
   - Read `docs/architecture/system_architecture.md`

2. **Check Coverage:**

   - Read `requirements_coverage` section in knowledge base
   - Identify what's already covered
   - Identify what's missing

3. **Plan Coverage:**
   - Break down task into requirements
   - Map each requirement to spec sections
   - Identify potential gaps upfront

---

### Step 2: During Implementation

**CTO Agent MUST:**

1. **Continuous Gap Detection:**

   - While implementing, compare with spec
   - Identify missing pieces immediately
   - Log gaps in `requirements_coverage.gaps`

2. **Gap Resolution Decision:**

   - **Can research?** → Add to `research_queue`
   - **Need user guidance?** → Add to `user_guidance_needed`
   - **Can infer from spec?** → Document assumption, ask for confirmation

3. **Update Coverage:**
   - Update `requirements_coverage.sections[].requirements[]`
   - Update coverage percentage
   - Log gaps identified

---

### Step 3: Gap Resolution

#### Option A: Research (IRCC)

**When to research:**

- Legal requirements (IRCC rules)
- Official documentation
- Policy changes
- Eligibility criteria

**Process:**

1. Add to `research_queue`
2. Use Browser MCP to navigate IRCC website
3. Extract official requirements
4. Update knowledge base with findings
5. Update requirements coverage
6. Proceed with implementation

**Example:**

```json
{
  "research_id": "RESEARCH_001",
  "topic": "Express Entry document requirements",
  "url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/documents.html",
  "status": "in_progress",
  "findings": "Documents required: Passport, Language test results, Education credentials...",
  "updated_at": "2025-12-02T11:00:00"
}
```

#### Option B: Ask User for Guidance

**When to ask:**

- Business logic decisions
- Workflow preferences
- Feature priorities
- Non-legal requirements

**Process:**

1. Add to `user_guidance_needed`
2. Present question clearly with context
3. Wait for user response
4. Update knowledge base with answer
5. Update requirements coverage
6. Proceed with implementation

**Example:**

```json
{
  "guidance_id": "GUIDANCE_001",
  "question": "What should be the case status workflow for Express Entry applications?",
  "context": "Implementing case management. Spec mentions status transitions but doesn't define exact workflow.",
  "options": [
    "Option 1: Draft → Submitted → In Review → Approved/Rejected",
    "Option 2: Draft → Submitted → AOR → Processing → Decision",
    "Option 3: Custom workflow"
  ],
  "status": "pending"
}
```

---

### Step 4: After Implementation

**CTO Agent MUST:**

1. **Verify Coverage:**

   - Check all requirements in section are covered
   - Verify no gaps remain
   - Update coverage percentage

2. **Document:**

   - Log what was implemented
   - Log what was researched
   - Log what was asked
   - Update knowledge base

3. **Report:**
   - Report coverage progress
   - Report gaps resolved
   - Report any remaining gaps

---

## 🎯 Master Workflow Integration

### Enhanced Master Prompt

```
@Product Manager/CTO Agent:

[YOUR TASK]

**Requirements:**
1. Read knowledge base first
2. **Check requirements coverage** - What's covered? What's missing?
3. **Plan coverage** - Map task to requirements
4. Use FAANG-style development
5. **During implementation:**
   - Continuously check for gaps
   - Research IRCC if legal requirement
   - Ask user if business decision needed
   - Update requirements coverage
6. Coordinate with agents
7. Update knowledge base
8. Ensure 80%+ coverage
9. Report status and coverage progress

Proceed.
```

---

## 📋 Examples

### Example 1: Implementing Case Management

**Before:**

```
CTO: Reads spec → Identifies requirements → Plans implementation
```

**During:**

```
CTO: Implements CRUD → Finds gap: "Status workflow not defined"
CTO: Checks spec → Not clear
CTO: Adds to user_guidance_needed → Asks user
User: "Use Option 2: Draft → Submitted → AOR → Processing → Decision"
CTO: Updates knowledge base → Continues implementation
```

**After:**

```
CTO: Verifies all requirements covered → Updates coverage → Reports progress
```

---

### Example 2: Implementing Document Upload

**Before:**

```
CTO: Reads spec → Identifies requirements → Plans implementation
```

**During:**

```
CTO: Implements upload → Finds gap: "What documents are required for Express Entry?"
CTO: Checks spec → Not detailed
CTO: Adds to research_queue → Researches IRCC
CTO: Finds official requirements → Updates knowledge base → Continues implementation
```

**After:**

```
CTO: Verifies all requirements covered → Updates coverage → Reports progress
```

---

## ✅ What This Ensures

**Always:**

- ✅ Progressive coverage of all requirements
- ✅ Gap identification during implementation
- ✅ Research for legal requirements
- ✅ User guidance for business decisions
- ✅ Systematic tracking of coverage
- ✅ No requirements missed

**Never:**

- ❌ Implement without checking requirements
- ❌ Skip gap identification
- ❌ Guess at legal requirements
- ❌ Make business decisions without user input
- ❌ Leave gaps unaddressed

---

## 🔧 Tools Available

### For Research:

- **Browser MCP** - Navigate IRCC website
- **IRCC Official Website** - https://www.canada.ca/en/immigration-refugees-citizenship/
- **Master Specification** - `docs/master_spec_refined.md`
- **PRD** - `docs/product/prd_canada_immigration_os.md`

### For Tracking:

- **Knowledge Base** - `.ai-knowledge-base.json`
- **Requirements Coverage Section** - `requirements_coverage`
- **Gaps Section** - `requirements_coverage.gaps`
- **Research Queue** - `requirements_coverage.research_queue`
- **User Guidance Queue** - `requirements_coverage.user_guidance_needed`

---

## 📊 Coverage Reporting

### Status Report Format

```
Requirements Coverage Report:
- Phase 1 Core: 80% (8/10 requirements)
- Phase 1 Advanced: 0% (0/15 requirements)
- Phase 2: 0% (0/20 requirements)

Gaps Identified: 2
- GAP_001: Case status workflow (P1) - User guidance needed
- GAP_002: Document requirements (P1) - Research in progress

Research Queue: 1
- RESEARCH_001: Express Entry document requirements (in progress)

User Guidance Needed: 1
- GUIDANCE_001: Case status workflow (pending)
```

---

**This ensures comprehensive, progressive coverage of all requirements! 🚀**
