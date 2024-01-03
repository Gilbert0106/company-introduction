FROM python:3.8-slim

RUN apt update
RUN apt install python3 -y
RUN useradd --create-home --shell /bin/bash app_user

WORKDIR /usr/app/src

USER app_user

COPY . .

CMD ["bash"]
