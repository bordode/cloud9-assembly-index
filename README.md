# Cloud-9 Assembly Index

Detecting non-stochastic assembly in dark-matter halos via mutual-information analysis of JWST-era simulations.

## Running locally (recommended)

1) Create and activate a virtual environment

```bash
python3 -m venv venv
. venv/bin/activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Run with gunicorn (recommended)

```bash
# runs on port 8080 by default
gunicorn main:app --bind 0.0.0.0:8080
```

Or run directly for development (debugging):

```bash
python3 main.py
```

Then test endpoints:

```bash
curl http://127.0.0.1:8080/
curl http://127.0.0.1:8080/analyze
curl http://127.0.0.1:8080/status
```

## Docker

Build and run the container (Dockerfile now installs requirements and runs gunicorn):

```bash
docker build -t cloud9-assembly-index .
docker run --rm -p 8080:8080 cloud9-assembly-index
```

## Heroku / Procfile

This repo includes a Procfile that uses gunicorn: `web: gunicorn main:app --bind 0.0.0.0:$PORT`. Ensure `requirements.txt` contains `gunicorn` and `Flask`.

## nohup or background-run scripts

If you previously used a hard-coded absolute path (e.g., `/home/cloudshell-user/Sovereign_Workspace/repo/main.py`), update any scripts to run from the repository root. Example:

```bash
cd /path/to/repo && nohup python3 main.py > run.log 2>&1 &
```

## Notes
- The Dockerfile and Procfile are now consistent and run `main:app` through gunicorn.
- If you prefer the lightweight `messenger.py` app instead, update the Procfile and Dockerfile accordingly.
