# Quick Reference: One-Time vs Regular

## What You Need to Do

**Date:** December 2, 2025

---

## ✅ ONE-TIME SETUP (Do Once, Then Never Again)

### 1. Branch Protection ⚠️ **YOU NEED TO DO THIS**

**Time:** 5 minutes
**Frequency:** Once (stays enabled forever)

**Steps:**

1. Go to: https://github.com/ranjan-expatready/Neuron/settings/branches
2. Click "Add rule"
3. Branch: `main`
4. Enable all protection settings
5. Click "Create"

**Done!** Protection stays enabled forever.

---

### 2. Pre-Commit Hooks ✅ **DONE FOR YOU**

**Status:** ✅ Already installed

**What it does:**

- Runs automatically on every commit
- Formats code
- Lints code
- Security checks
- Prevents bad code

**You don't need to do anything** - it's automatic!

---

### 3. Version Tag ✅ **DONE FOR YOU**

**Status:** ✅ Already created (v1.0.0)

**To push:**

```bash
git push origin v1.0.0
```

**You only do this once** - tag is created.

---

## ✅ AUTOMATIC (No Action Needed - Happens Automatically)

### Pre-Commit Hooks ✅ AUTOMATIC

- **Runs:** Every commit
- **You do:** Nothing - it's automatic!

### CI/CD Pipeline ✅ AUTOMATIC

- **Runs:** On every PR
- **You do:** Nothing - it's automatic!

### Tests ✅ AUTOMATIC

- **Runs:** On every PR
- **You do:** Nothing - it's automatic!

### Security Scans ✅ AUTOMATIC

- **Runs:** On every PR
- **You do:** Nothing - it's automatic!

### Coverage Checks ✅ AUTOMATIC

- **Runs:** On every PR
- **You do:** Nothing - it's automatic!

---

## 🔄 REGULAR (When Needed)

### Creating Releases 🔄 WHEN RELEASING

**When:** After completing features

**How:**

```bash
echo "1.0.1" > VERSION
# Update CHANGELOG.md
git add VERSION CHANGELOG.md
git commit -m "chore: prepare release v1.0.1"
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

**Frequency:** When you want to release (weekly, monthly, etc.)

---

### Code Reviews 🔄 EVERY PR

**Process:**

1. Create feature branch
2. Make changes
3. Commit (hooks run automatically)
4. Push and create PR
5. Get 2 approvals
6. Merge

**Frequency:** Every feature/bug fix

---

## 📋 Summary

### One-Time (Do Once):

- ✅ Pre-commit hooks (DONE)
- ✅ Version tag (DONE)
- ⚠️ Branch protection (YOU DO - 5 min)

### Automatic (No Action):

- ✅ Pre-commit hooks (automatic)
- ✅ CI/CD (automatic)
- ✅ Tests (automatic)
- ✅ Security scans (automatic)

### Regular (When Needed):

- 🔄 Create releases
- 🔄 Code reviews

---

## 🎯 What You Need to Do

### Right Now (5 minutes):

**Set up branch protection:**

- Go to: https://github.com/ranjan-expatready/Neuron/settings/branches
- Follow `BRANCH_PROTECTION_QUICK_SETUP.md`

### After That:

- ✅ **Everything is automatic!**
- ✅ Just code, commit, create PRs
- ✅ All quality checks run automatically

---

**One-time setup, then everything is automatic! 🚀**
