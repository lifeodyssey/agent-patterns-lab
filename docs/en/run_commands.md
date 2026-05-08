# Command Notes: What `uv run` Does

The common command is:

```bash
uv run python examples/21_react_loop.py
```

It means: **run this Python file inside the environment managed by `uv`.**

## Recommended Version

Start with:

```bash
uv run python examples/21_react_loop.py
```

If it works, you do not need the longer version.

## Longer Version

You may also see:

```bash
PYTHONPATH=src uv run --no-sync python examples/21_react_loop.py
```

| Part | Meaning | When useful |
|---|---|---|
| `PYTHONPATH=src` | Tells Python where the local package lives. | If imports fail. |
| `uv run` | Runs a command in the project environment. | Almost always. |
| `--no-sync` | Runs without syncing dependencies first. | When the env is already ready. |
| `python examples/...` | The actual Python script. | This is the main part. |

You may also see:

```bash
UV_CACHE_DIR=.uv_cache uv run ...
```

That only moves the `uv` cache into the repo folder. It is useful in sandboxes or CI, but not required for normal reading.
