FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache gcc musl-dev linux-headers

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/static

#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
