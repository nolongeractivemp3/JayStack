# Jaystack
This is a Web stack i made to make it easier for me to develop and deploy web applications.
you can view the diagram here https://excalidraw.com/#json=poseT4xk_tgyaDuS7PGS3,FRif6yl9fqhzjI3NSGry0g
# usage
## commands
Run with `docker-compose up -d` or `docker-compose up -d --build`
stop with `docker-compose down`
logs with `docker-compose logs -f` name of service
# networks
to talk to things use `nameofservice:port` for example `backend:8080` or `pocketbase:8080`


![diagram](img/stack.png)
