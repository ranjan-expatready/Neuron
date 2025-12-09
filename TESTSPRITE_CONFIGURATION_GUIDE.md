# TestSprite Configuration Guide

## Best-in-Class Setup for Maximum Context

**Date:** December 2, 2025
**Purpose:** Configure TestSprite with optimal settings for comprehensive testing

---

## 🎯 Configuration Settings

### 1. Testing Types ✅

**Mode:**

- ✅ **Backend** (Selected) - Correct!
- Your backend is running on port 8000

**Scope:**

- ✅ **Codebase** (Selected) - Good for first-time setup
- This will analyze your entire codebase
- After initial setup, you can use "Code diff" for incremental testing

**Recommendation:** Keep "Codebase" for first bootstrap, then switch to "Code diff" for faster subsequent runs.

---

### 2. Authentication ⚠️ **NEEDS UPDATE**

**Current:** "None - No authentication required" ❌

**Should be:** "Bearer Token (JWT)" ✅

**Why:** Your backend uses JWT authentication. TestSprite needs to authenticate to test protected endpoints.

**How to Configure:**

1. **Change Type:** Select "Bearer Token (JWT)" from dropdown
2. **Token:** You'll need to provide a JWT token
3. **Get Token:** TestSprite will need to login first, or you can provide a test token

**Alternative:** If you want to test without auth first:

- Keep "None" for initial bootstrap
- Update to "Bearer Token" after bootstrap completes
- This allows TestSprite to analyze structure first

---

### 3. Local Development Port ✅

**Port:** `8000` ✅ (Correct!)

- Your backend is running on http://localhost:8000

**Path:** `/` ✅ (Correct!)

- Your API base is at root level

**Status:** ✅ **Correct Configuration**

---

### 4. Product Specification Doc ⚠️ **REQUIRED**

**Current:** Not uploaded ❌

**What to Upload:** You have excellent product documentation! Choose the best one:

### Option 1: Master Specification (Recommended)

**File:** `docs/master_spec_refined.md`

- ✅ Most comprehensive
- ✅ Includes all features, architecture, agents
- ✅ Complete system overview
- ✅ Best for TestSprite to understand full context

### Option 2: Product Requirements Document

**File:** `docs/product/prd_canada_immigration_os.md`

- ✅ Detailed feature requirements
- ✅ User stories and acceptance criteria
- ✅ Good for test case generation

### Option 3: Both (Best)

**Upload:** `docs/master_spec_refined.md` first

- Then upload `docs/product/prd_canada_immigration_os.md` if allowed
- Or combine them into one document

**Recommendation:** Upload `docs/master_spec_refined.md` - it's the most comprehensive.

---

## 📋 Step-by-Step Configuration

### Step 1: Upload Product Specification

1. Click "Select your product requirements document"
2. Navigate to: `docs/master_spec_refined.md`
3. Upload the file
4. Wait for upload to complete

**Why This Matters:**

- TestSprite uses this to understand your product
- Generates better test cases
- Understands feature requirements
- Creates acceptance tests aligned with your spec

---

### Step 2: Update Authentication (After Bootstrap)

**For Now:** Keep "None" to allow initial bootstrap

**After Bootstrap Completes:**

1. Change to "Bearer Token (JWT)"
2. Run the seed helper to get a fresh token:
   ```bash
   cd backend
   source venv/bin/activate
   python scripts/seed_testsprite_user.py
   ```
   Copy the `jwt_token` value from the script output into TestSprite.
3. TestSprite will now authenticate automatically for every test run.

**How to Get Test Token:**

```bash
# Register a test user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testsprite@test.com",
    "password": "test123456",
    "first_name": "TestSprite",
    "last_name": "Agent"
  }'

# Login to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testsprite@test.com",
    "password": "test123456"
  }'
```

---

### Step 3: Verify Configuration

**Before Starting:**

- ✅ Mode: Backend
- ✅ Scope: Codebase (for first time)
- ✅ Port: 8000
- ✅ Path: /
- ✅ Product Spec: Uploaded
- ⚠️ Auth: None (for now, update later)

---

## 🎯 Best Practices

### 1. Product Specification

- ✅ Upload comprehensive spec (master_spec_refined.md)
- ✅ Include acceptance criteria
- ✅ Include API documentation if available

### 2. Authentication

- Start with "None" for bootstrap
- Update to "Bearer Token" after bootstrap
- Provide test credentials or token

### 3. Scope

- Use "Codebase" for first-time setup
- Switch to "Code diff" for faster subsequent runs
- "Code diff" only tests changed files

### 4. Port Configuration

- Ensure backend is running
- Verify port 8000 is accessible
- Test health endpoint before starting

---

## 📄 Recommended Files to Upload

### Primary (Must Have):

1. **`docs/master_spec_refined.md`** ⭐ **BEST CHOICE**
   - Complete system specification
   - All features documented
   - Architecture included
   - Agent system explained

### Secondary (If Allowed):

2. **`docs/product/prd_canada_immigration_os.md`**

   - Detailed requirements
   - User stories
   - Acceptance criteria

3. **`docs/architecture/system_architecture.md`**
   - Technical architecture
   - API design
   - Database schema

---

## 🔧 Complete Configuration Checklist

### Before Starting TestSprite:

- [ ] **Mode:** Backend ✅
- [ ] **Scope:** Codebase ✅ (for first time)
- [ ] **Port:** 8000 ✅
- [ ] **Path:** / ✅
- [ ] **Product Spec:** Upload `docs/master_spec_refined.md` ⚠️
- [ ] **Authentication:** None (for bootstrap) ⚠️
- [ ] **Backend Running:** http://localhost:8000 ✅

### After Bootstrap:

- [ ] Update Authentication to "Bearer Token (JWT)"
- [ ] Provide test token or credentials
- [ ] Switch Scope to "Code diff" for faster runs
- [ ] Run first test suite

---

## 🚀 What Happens After Configuration

### TestSprite Will:

1. **Analyze Product Spec:**

   - Understand your product features
   - Extract requirements
   - Identify test scenarios

2. **Analyze Codebase:**

   - Scan all backend files
   - Understand API structure
   - Identify endpoints

3. **Generate Test Plan:**

   - Create comprehensive test plan
   - Generate test cases
   - Align with product spec

4. **Generate Tests:**

   - Unit tests
   - Integration tests
   - API tests
   - Acceptance tests

5. **Execute Tests:**
   - Run generated tests
   - Report results
   - Identify issues

---

## ✅ Summary

### What to Fill In:

1. **Product Specification Doc:**

   - Upload: `docs/master_spec_refined.md` ⭐
   - This gives TestSprite full context

2. **Authentication:**

   - Keep "None" for now (allows bootstrap)
   - Update to "Bearer Token" after bootstrap

3. **Everything Else:**
   - ✅ Already correct!

### Next Steps:

1. Upload `docs/master_spec_refined.md`
2. Click "Continue" or "Start"
3. Wait for bootstrap (20-30 minutes)
4. After bootstrap, update authentication
5. Run first test suite

---

**Your configuration is almost perfect! Just upload the product spec and you're ready! 🚀**
