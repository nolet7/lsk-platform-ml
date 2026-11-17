# Separate image: control plane only, not the aerospace classifier.
FROM python:3.12-slim
WORKDIR /srv/platform
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 APP_ENV=production
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && useradd --system --uid 10001 mlplatform
COPY app ./app
COPY platform ./platform
USER 10001
EXPOSE 8080
CMD ["uvicorn", "platform.api:app", "--host", "0.0.0.0", "--port", "8080"]
