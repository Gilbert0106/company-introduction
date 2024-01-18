FROM python:3.8-slim

RUN apt update
RUN apt install python3 -y
RUN useradd --create-home --shell /bin/bash app_user

WORKDIR /usr/app/src

USER app_user

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash"]
