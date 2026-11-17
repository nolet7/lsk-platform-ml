FROM python:3.12-slim AS build
WORKDIR /opt/model
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ml ./ml
RUN python -m ml.train

FROM python:3.12-slim
WORKDIR /opt/model
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MODEL_PATH=/opt/model/artifacts/model.json
RUN useradd --system --uid 10001 serving
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=build /opt/model/artifacts ./artifacts
COPY app ./app
COPY examples/sklearn_inference/inference.py ./inference.py
USER 10001
EXPOSE 8080
CMD ["uvicorn","inference:app","--host","0.0.0.0","--port","8080"]
