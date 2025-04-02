# CONTRIBUTING

Please follow github workflow. Create a ticket and/or branch. Create a pull-request.

## Local Development

### Installation

Please install these tools:

* [`uv` Installation](https://docs.astral.sh/uv/getting-started/installation/)
* [`make`](https://www.gnu.org/software/make/)
* [`git`](https://git-scm.com/)
* [Visual Studio Code](https://code.visualstudio.com/)


### Editor

Start Visual Studio Code:

```bash
make code
```

### Testing

Run auto-formatting, linting, tests and documentation build:

```bash
make all
```

See `make help` for any further details.


## Project Structure

The project contains these files and directories:

| File/Directory | Description |
|---|---|
| `src/` | Python Package Sources - the files this is all about |
| `pyproject.toml` | Python Package Meta File. Also contains all tool settings |
| `.gitignore` | Lists of files and directories ignored by version control system |
| `.github/` | Github Settings |
| `.readthedocs.yaml` | Documentation Server Configuration |
| `.pre-commit-config.yaml` | Pre-Commit Check Configuration |
| `uv.lock` | File with resolved python package dependencies |

Next to that, there are some temporary files ignored by version control system.

| File/Directory | Description |
|---|---|
| `htmlcov/` | Test Execution Code Coverage Report in HTML format |
| `report.xml` | Test Execution Report |
| `.venv` | Virtual Environments |
