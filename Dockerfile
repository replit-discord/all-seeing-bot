FROM golang:latest

WORKDIR /opt/app

EXPOSE 3000
EXPOSE 3001
EXPOSE 8888
EXPOSE 9229

RUN apt update
RUN apt install inotify-tools -y

CMD ["./scripts/start_app.sh"]

