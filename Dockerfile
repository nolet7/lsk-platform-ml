FROM python:3.12-slim
WORKDIR /opt/lsk
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd -u 10001 -m appuser
COPY app app
COPY ml ml
COPY sdk sdk
RUN mkdir -p artifacts && chown -R appuser:appuser /opt/lsk
USER appuser
EXPOSE 8765
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8765"]
