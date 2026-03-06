.PHONY: dev build up down logs pb-migrate clean

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
