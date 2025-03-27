# start with base image
FROM mysql:latest

# import data into container
# All scripts in docker-entrypoint-initdb.d/ are automatically executed during container startup

ARG MYSQL_DATABASE
ARG MYSQL_ROOT_USER
ARG MYSQL_ROOT_PASSWORD

ENV MYSQL_DATABASE=backend
ENV MYSQL_ROOT_USER=root
ENV MYSQL_ROOT_PASSWORD=password

COPY /*.sql /docker-entrypoint-initdb.d/




