# Repository Maintenance Guidelines

- Format Python code with `ruff format` before committing. `uv run prek run --all-files` does this.
- Run the test suite with `uv run pytest -n auto` before every commit.
- Cite the ReqIDs from `docs/specs/` in every issue and pull request. Change the spec and `docs/rtm.md` in the same diff as the behavior.
