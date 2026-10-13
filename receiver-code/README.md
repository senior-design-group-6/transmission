# Receiver Code

## How to run

### With `uv`

```bash
uv sync
uv run python -m receiver_code
```

### With `python` + `pip`

```bash
python -m pip install -r requirements.txt
python -m receiver_code
```

## How to Update `requirements.txt`

```bash
uv export --no-hashes --format requirements.txt > requirements.txt
```
