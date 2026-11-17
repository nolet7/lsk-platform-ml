FROM python:3.12-slim
WORKDIR /srv/platform
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 APP_ENV=production
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && useradd --system --uid 10001 platformworker
COPY app ./app
COPY mlplatform ./mlplatform
USER 10001
CMD ["python","-m","mlplatform.reconciler"]
