# Code Review Checklist

## FAANG-Level Quality Standards

**Use this checklist for all pull requests to `main` branch**

---

## 🔍 Pre-Review Checklist

### Code Quality:

- [ ] Code follows style guide (black, isort, prettier)
- [ ] No linting errors
- [ ] No type errors
- [ ] Code is readable and well-documented
- [ ] No commented-out code
- [ ] No debug statements left in

### Testing:

- [ ] Tests added for new features
- [ ] Tests updated for changed features
- [ ] All tests passing
- [ ] Coverage maintained (80%+)
- [ ] Edge cases tested
- [ ] Integration tests updated if needed

### Security:

- [ ] No hardcoded secrets
- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] Authentication/authorization correct
- [ ] Security scan passed

### Architecture:

- [ ] Follows system architecture
- [ ] No breaking changes (or documented)
- [ ] Database migrations tested
- [ ] API contracts maintained
- [ ] Multi-tenant isolation maintained

### Documentation:

- [ ] Code comments for complex logic
- [ ] API documentation updated
- [ ] README updated if needed
- [ ] Changelog updated
- [ ] Knowledge base updated (if applicable)

---

## ✅ Approval Criteria

**PR can be approved when:**

- ✅ All checklist items checked
- ✅ All CI checks passing
- ✅ 2+ approvals from reviewers
- ✅ No blocking comments
- ✅ All conversations resolved

---

**This ensures code quality and prevents breaking changes! ✅**
