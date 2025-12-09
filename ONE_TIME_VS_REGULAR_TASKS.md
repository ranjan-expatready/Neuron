# One-Time vs Regular Tasks

## DevOps/CI/CD Maintenance Guide

**Date:** December 2, 2025
**Purpose:** Clarify what needs to be done once vs regularly

---

## ✅ One-Time Setup (Do Once)

### 1. Pre-Commit Hooks Installation ✅ DONE

**Status:** ✅ **COMPLETED**

**What was done:**

- Installed pre-commit
- Installed hooks in git repository
- Hooks now run automatically on every commit

**You don't need to do this again** - hooks are installed permanently

---

### 2. Branch Protection Setup ⚠️ **NEEDS YOUR ACTION**

**Status:** ⚠️ **REQUIRES GITHUB UI ACCESS**

**Why:** Branch protection must be set up in GitHub web interface (can't be automated via CLI without GitHub API access)

**What to do (5 minutes, one-time):**

1. Go to: https://github.com/YOUR_USERNAME/Neuron-2/settings/branches
2. Click "Add rule"
3. Branch name: `main`
4. Enable:
   - ✅ Require pull request reviews (set to 2)
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date
   - ✅ Do not allow force pushes
   - ✅ Do not allow deletions
5. Click "Create"

**You only do this once** - protection stays enabled

---

### 3. Initial Version Tag ✅ DONE

**Status:** ✅ **COMPLETED**

**What was done:**

- Created version tag v1.0.0
- Tagged current state

**You don't need to do this again** - tag is created

---

## 🔄 Regular Tasks (Ongoing)

### 1. Pre-Commit Hooks ✅ AUTOMATIC

**Frequency:** Every commit (automatic)

**What happens:**

- Hooks run automatically when you commit
- No action needed from you
- If hooks fail, fix issues and commit again

**You don't need to do anything** - it's automatic

---

### 2. Creating Releases 🔄 WHEN NEEDED

**Frequency:** When releasing new version

**When to do:**

- After completing a feature
- After bug fixes
- Before production deployment

**How to do:**

```bash
# 1. Update VERSION file
echo "1.0.1" > VERSION

# 2. Update CHANGELOG.md
# Add release notes

# 3. Commit
git add VERSION CHANGELOG.md
git commit -m "chore: prepare release v1.0.1"

# 4. Create tag
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

**This triggers:**

- Automated release creation
- Production deployment (if configured)

---

### 3. Code Reviews 🔄 EVERY PR

**Frequency:** Every pull request

**What happens:**

- Create PR from feature branch
- CI/CD runs automatically
- Reviewers review code
- Must get 2 approvals
- All tests must pass
- Then merge to main

**You do this regularly** - for every feature/bug fix

---

### 4. Monitoring Deployments 🔄 AFTER EACH DEPLOYMENT

**Frequency:** After each production deployment

**What to check:**

- Health checks passing
- No errors in logs
- Performance metrics normal
- User feedback positive

**You do this regularly** - after each release

---

## 📋 Summary

### One-Time (Do Once):

- ✅ Pre-commit hooks installation (DONE)
- ⚠️ Branch protection setup (YOU NEED TO DO - 5 min)
- ✅ Initial version tag (DONE)

### Regular (Ongoing):

- ✅ Pre-commit hooks (AUTOMATIC - no action needed)
- 🔄 Creating releases (when needed)
- 🔄 Code reviews (every PR)
- 🔄 Monitoring deployments (after each release)

---

## 🎯 What You Need to Do Now

### Immediate (5 minutes):

1. **Set up branch protection:**
   - Go to GitHub → Settings → Branches
   - Follow `.github/BRANCH_PROTECTION.md`
   - Enable protection for `main` branch

### Ongoing (Automatic):

- ✅ Pre-commit hooks run automatically
- ✅ CI/CD runs automatically on PRs
- ✅ Tests run automatically
- ✅ Security scans run automatically

### When Needed:

- Create new version tags for releases
- Review and approve PRs
- Monitor deployments

---

## ✅ Current Status

**Completed (One-Time):**

- ✅ Pre-commit hooks installed
- ✅ Initial version tag created
- ✅ All workflows configured
- ✅ Documentation created

**Needs Your Action (One-Time):**

- ⚠️ Branch protection (5 minutes in GitHub UI)

**Automatic (No Action Needed):**

- ✅ Pre-commit hooks run on every commit
- ✅ CI/CD runs on every PR
- ✅ Tests run automatically
- ✅ Security scans run automatically

---

**Most things are automatic! You only need to set up branch protection once, then everything runs automatically! 🚀**
