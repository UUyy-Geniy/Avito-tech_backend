build:
	docker-compose build

up: build
	docker-compose up

migrate:
	docker-compose run --rm api sh -c "python manage.py migrate"

admin: migrate
	docker-compose run --rm api sh -c "python manage.py createsuperuser"

test: migrate
	docker-compose run --rm api sh -c "python manage.py test"

down:
	docker-compose down


