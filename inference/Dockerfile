FROM python:3.10-slim

WORKDIR /app

COPY . /app/

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y
RUN pip install --no-cache-dir -r requirements.txt

ENV FASTAPI_ENV=production

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8099"]
