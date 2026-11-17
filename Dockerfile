FROM python:3.12-slim AS build
WORKDIR /opt/lsk
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app app
COPY ml ml
COPY sdk sdk
# Synthetic dataset and model, bundled immutably with the image.
RUN python -m ml.train

FROM python:3.12-slim
WORKDIR /opt/lsk
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 APP_ENV=production MODEL_PATH=/opt/lsk/artifacts/model.json
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=build /opt/lsk/app /opt/lsk/app
COPY --from=build /opt/lsk/ml /opt/lsk/ml
COPY --from=build /opt/lsk/sdk /opt/lsk/sdk
COPY --from=build /opt/lsk/artifacts /opt/lsk/artifacts
RUN useradd --system --uid 10001 appuser && chown -R 10001:10001 /opt/lsk
USER 10001
EXPOSE 8765
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8765"]
