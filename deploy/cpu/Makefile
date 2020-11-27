-include .env
#####################################################################################
start:
	docker-compose up -d

stop:
	docker-compose stop && docker-compose rm -f

clean: stop
#####################################################################################
test:
	curl -i -X POST http://localhost:$(SERVICE_PORT)/model -d@data.json