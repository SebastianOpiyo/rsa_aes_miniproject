# DOCUMENTATION 

# Prerequisites
- Ensure you have the following installed:
    1. Docker
    2. Python version 3.8  and above (Development done with python 3.10)
- Docker will install the rest of the application dependency from the `requirements.txt file.`

## To build Dockerfile run:
1. `docker build -t api-server .`
2. `docker build -t api-consumer .`

## To run the API server
`docker run -p 5000:5000 api-server`

## To run the Api client consumer
`docker run api-consumer`

