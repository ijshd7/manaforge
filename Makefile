.PHONY: dev build up down logs pb-migrate clean lint lint-fix test test-frontend test-backend

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
	cd backend && unset VIRTUAL_ENV && uv run pytest
