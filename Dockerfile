FROM python:3.8-slim

RUN apt update \ 
    && apt install python3 -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/app/src

RUN mkdir -p /usr/app/src/reports \
    && useradd --create-home --shell /bin/bash app_user \
    && chown -R app_user:app_user /usr/app/src/reports

USER app_user

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash"]

RUN echo "alias generate-report='python3 main.py'" >> /home/app_user/.bashrc