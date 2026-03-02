.PHONY: dev prod down logs test scale

dev:
	docker compose --profile dev up --build

prod:
	docker compose --profile prod up --build -d

down:
	docker compose --profile dev down
	docker compose --profile prod down

logs:
	docker compose logs -f --tail=200

test:
	docker compose --profile dev up -d --build
	docker compose --profile dev exec api-dev pytest -q

scale:
	docker compose --profile prod up -d --scale worker=3