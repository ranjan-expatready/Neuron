# Branch Protection Setup Guide

## FAANG-Level Code Safety

**Purpose:** Prevent breaking working code and ensure code quality

---

## 🛡️ Branch Protection Rules

### For `main` Branch:

**Required Settings:**

1. ✅ **Require pull request reviews before merging**

   - Required approvals: 2
   - Dismiss stale reviews when new commits are pushed
   - Require review from Code Owners

2. ✅ **Require status checks to pass before merging**

   - Required status checks:
     - `backend-ci`
     - `frontend-ci`
   - Require branches to be up to date before merging

3. ✅ **Require conversation resolution before merging**

   - All comments must be resolved

4. ✅ **Restrict who can push to matching branches**

   - No one can push directly (only via PR)

5. ✅ **Do not allow force pushes**

   - Prevents force push to main

6. ✅ **Do not allow deletions**
   - Prevents branch deletion

---

## 📋 How to Set Up (GitHub UI)

### Step 1: Navigate to Settings

1. Go to your GitHub repository
2. Click **Settings** → **Branches**

### Step 2: Add Branch Protection Rule

1. Click **Add rule**
2. Branch name pattern: `main`
3. Enable all settings above
4. Click **Create**

### Step 3: Configure Status Checks

1. In the same rule, scroll to **Require status checks to pass**
2. Check:
   - `backend-ci`
   - `frontend-ci`

---

## 🔧 Alternative: GitHub API

```bash
# Set branch protection via API
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["backend-ci","frontend-ci"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":2}' \
  --field restrictions=null
```

---

## ✅ Result

**After setup:**

- ✅ No direct pushes to main
- ✅ All PRs require 2 approvals
- ✅ All tests must pass
- ✅ All security checks must pass
- ✅ No force push allowed
- ✅ Working code protected

---

**This ensures you never break working code! 🛡️**
