docker-push-minecraft:
	cd minecraft; make docker-push; 

swarm-up-ngrok:
	cd docker-ngrok; make swarm-up

swarm-up: docker-push-minecraft swarm-up-ngrok 
	cd docker-ngrok; swarm status
