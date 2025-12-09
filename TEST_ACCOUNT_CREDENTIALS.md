# Test Account Credentials

## For TestSprite Configuration

**Date:** December 2, 2025

---

## ✅ Test Account Created Successfully

Your test account has been created and is ready to use!

---

## 🔑 Credentials

**Test Account Email:**

```
testsprite.automation@canadaos.dev
```

**Test Account Password:**

```
TestSprite!234
```

---

## 📋 For TestSprite Configuration

**Use these credentials in TestSprite:**

1. **Email:** `testsprite.automation@canadaos.dev`
2. **Password:** `TestSprite!234`
3. **Organization:** `TestSprite Automation Org`
4. **JWT Token:** Run the seed script below and paste the printed `jwt_token` into TestSprite’s “Bearer Token” field.

```bash
cd backend
source venv/bin/activate
python scripts/seed_testsprite_user.py
```

The script is idempotent and will re-use the same account, returning a fresh token each time.

---

## ✅ Verification

The seed script automatically ensures:

- ✅ User + org exist
- ✅ Membership is admin-level
- ✅ Fresh JWT token is returned for TestSprite

---

## 🔒 Security Note

This is a test account with simple credentials. For production, use stronger passwords and proper security practices.

---

**Your test account is ready! Use these credentials in TestSprite configuration. 🚀**
