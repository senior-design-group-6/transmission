# Receiver Code

## How to run

### With `uv`

```bash
uv sync
uv run python -m receiver_code
```

### With `python` + `pip`

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m receiver_code
```

## How to Update `requirements.txt`

```bash
uv export --no-hashes --format requirements.txt > requirements.txt
```
