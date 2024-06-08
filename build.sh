#!/bin/sh

dockerize -wait tcp://db:3306 -timeout 60s

alembic upgrade head

uvicorn url_shortner.main:app --host 0.0.0.0 --port 8000