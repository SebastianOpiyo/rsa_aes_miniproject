# DOCUMENTATION 

# Prerequisites
- Ensure you have the following installed:
    1. Docker, docker-compose
    2. Python version 3.8  and above (Development done with python 3.10)
- Docker will install the rest of the application dependency from the `requirements.txt file.`

## To build Docker Containers run:
- Check if docker daemon is running with ` sudo service docker status`
- If it is running start docker by running  `sudo service docker start`
- Run individual images if it exists with `docker run <image-name>`

### Flags
Here are some of the options that you can pass to the docker run command:

* `-it`: This option tells Docker to run the container in interactive mode. This means that you will be able to interact with the container from the command line.
* `-d`: This option tells Docker to run the container in detached mode. This means that the container will run in the background and you will not be able to interact with it from the command line.
* `-p`: This option tells Docker to map a port from the container to a port on your host machine. This allows you to access the application running in the container from your host machine.
## Run Docker-compose to build and run images
- `docker-compose build`
- To rebuild the container run the following: `docker-compose up -d --build <my-container>`

## To run the API server
`docker run -p 5000:5000 api-server`

## To run the Api client consumer
`docker run api-consumer`

