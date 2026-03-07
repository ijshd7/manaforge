.PHONY: dev build up down logs pb-migrate clean lint lint-fix test test-frontend test-backend fix-venv bump

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

pb-migrate:
	docker compose exec pocketbase /pb/pocketbase migrate up

clean:
	docker compose down -v --rmi all

lint:
	bash -c 'source $$HOME/.nvm/nvm.sh && nvm use 22 && cd frontend && npx pnpm lint && cd ../backend && ruff check app'

lint-fix:
	bash -c 'source $$HOME/.nvm/nvm.sh && nvm use 22 && cd frontend && npx pnpm lint:fix && cd ../backend && ruff check --fix app && ruff format app'

test:
	$(MAKE) test-frontend
	$(MAKE) test-backend

test-frontend:
	bash -c 'source $$HOME/.nvm/nvm.sh && nvm use 22 && cd frontend && npx pnpm test:run'

test-backend:
	cd backend && unset VIRTUAL_ENV && uv run --extra dev pytest

# One-time fix when backend .venv was created by Docker (root-owned). Run if make test fails with "Permission denied".
fix-venv:
	sudo rm -rf backend/.venv

# Bump version in VERSION, backend/pyproject.toml, frontend/package.json. Usage: make bump [PART=patch|minor|major|0.2.0]
bump:
	./scripts/bump-version.sh $(or $(PART),patch)
