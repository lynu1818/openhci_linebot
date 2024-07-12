FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENV PORT=8080

CMD ["gunicorn", "-b", "0.0.0.0:$PORT", "main:app", "--workers", "3", "--timeout", "300"]
