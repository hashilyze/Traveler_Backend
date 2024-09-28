FROM python:3.11.9-slim
MAINTAINER JUNSU BAE <jsbae1023@gmail.com>

CMD ["python", "server.py"]
EXPOSE 5000

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

