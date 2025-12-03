.PHONY: test-frontend test-e2e

test-frontend:
	cd frontend && npm install && npm run lint && npm run build

test-e2e:
	@echo "Run 'make e2e-spine' from backend after starting backend/frontend servers."
