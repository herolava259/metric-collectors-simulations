# uv python-package-tools 

## I. Commands 

- create project : `uv init <your-service>`
- create lib: `uv init --lib  <your-lib-name>`
- create lock: `uv lock`
- view structure deps tree: `uv tree`
- add your own packages:  `uv add <your-own-pkg-path> --package <your-own-service> --editable`
- add tool: `uv tool install <ruff/>`
- sync for new env: `uv sync`
- build package: `uv build`
- increase version of package: `uv version <x.y.z>`
- minor version ex: 1.2.3 => 1.3.0: `uv version --bump minor`
    - beta: `uv version --bump patch --bump beta`
    - alpha: `uv version --bump major --bump alpha`
