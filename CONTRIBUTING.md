# Contribute

## Testing

### Create Environment

Run these commands just the first time:

```bash
# Ensure python3 is installed
python3 -m venv .venv
source .venv/bin/activate
pip install uv
```

### Enter Environment

Run this command once you open a new shell:

```bash
source .venv/bin/activate
```

### Test Your Changes

```bash
make all
```

### Release

Create release via 

    https://github.com/c0fec0de/anycache/releases/new