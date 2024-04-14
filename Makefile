build:
    docker-compose build

up:
    docker-compose up

down:
    docker-compose down

admin:
	docker-compose run --rm api sh -c "python manage.py createsuperuser"

test:
    docker-compose run --rm api sh -c "python manage.py test"

