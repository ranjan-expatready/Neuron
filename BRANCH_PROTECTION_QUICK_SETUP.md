# Branch Protection Quick Setup

## 5-Minute One-Time Setup

**Purpose:** Protect your main branch from breaking changes

---

## 🎯 Quick Steps

### Step 1: Open GitHub

Go to: **https://github.com/YOUR_USERNAME/Neuron-2/settings/branches**

_(Replace YOUR_USERNAME with your actual GitHub username)_

---

### Step 2: Add Branch Protection Rule

1. Click **"Add rule"** or **"Add branch protection rule"**

2. **Branch name pattern:** Type `main`

3. **Enable these checkboxes:**

   ✅ **Require pull request reviews before merging**

   - Required number of approvals: **2**
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require review from Code Owners (if you have CODEOWNERS file)

   ✅ **Require status checks to pass before merging**

   - ✅ Require branches to be up to date before merging
   - In "Status checks that are required", enable:
     - `backend-ci`
     - `frontend-ci`

   ✅ **Require conversation resolution before merging**

   ✅ **Do not allow force pushes**

   ✅ **Do not allow deletions**

4. Click **"Create"** or **"Save changes"**

---

## ✅ Done!

**That's it!** Your main branch is now protected.

**What this means:**

- ✅ No one can push directly to `main`
- ✅ All changes must go through PRs with 2 approvals
- ✅ `backend-ci` and `frontend-ci` must pass
- ✅ Force pushes and branch deletions are blocked

---

## 🔄 This is One-Time

**You only do this once** - the protection stays enabled forever.

**After setup:**

- Everything is automatic
- Pre-commit hooks run on commit
- CI/CD runs on PRs
- Tests run automatically
- You just code and create PRs!

---

**5 minutes, one-time setup, permanent protection! 🛡️**
