# POC: run on Windows Git Bash, WSL or Linux

This is an educational, **local-only** API. Port 8765 is used to avoid conflict with common development services.

```bash
git checkout poc
python -m venv .venv
# Git Bash / Linux:
source .venv/Scripts/activate  # Windows Git Bash
# On Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m ml.train
python -m pytest -q
python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

In a second terminal:
```bash
curl http://127.0.0.1:8765/healthz
curl -H 'X-Demo-Key: local-demo-key' http://127.0.0.1:8765/v1/repair-orders/RO-1001
curl -H 'X-Demo-Key: local-demo-key' -H 'Content-Type: application/json' -d '{"inspection_id":"INSP-1001","signals":{"surface_texture":0.8,"edge_irregularity":0.7,"color_variance":0.8}}' http://127.0.0.1:8765/v1/predictions
```
Save `prediction_id` and send a POST to `/v1/reviews` with `X-Reviewer: synthetic-inspector`, `disposition: hold_for_engineer`, and rationale. Model calls never modify QMS repair disposition. Full Swagger contract: http://127.0.0.1:8765/docs

For container use, first run training on host, then `docker compose up --build`. Artifacts are ignored by Git and mounted read-only. The POC does not enforce tenant isolation, OIDC, or regulated audit guarantees; never expose it publicly.
