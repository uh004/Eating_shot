FROM python:3.10-slim

ARG DJANGO_SECRET_KEY
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_ENV=production

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py collectstatic --noinput

# run these manually after container is up.
#RUN python manage.py makemigrations
#RUN python manage.py migrate

EXPOSE 8000

CMD ["uvicorn", "core.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
