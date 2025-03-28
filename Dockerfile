FROM python:3.9.6

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

COPY .env.local .env

CMD ["python", "agent.py", "start"]