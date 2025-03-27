FROM golang:1.20.3-alpine AS build

WORKDIR /app

COPY go.mod go.sum /app/
RUN go mod download -x

#RUN -d --name mysql-container -e MYSQL_ROOT_PASSWORD=mysecretpassword -p 3306:3306 mysql

COPY . /app/

RUN go build -o main

EXPOSE 5000

CMD ["./main"]
