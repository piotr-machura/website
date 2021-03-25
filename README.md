# Personal website source
This is my personal website, built with [MkDocs](https://mkdocs.org). It contains whatever I feel like throwing on
there.

### Installation
After puling with git run `pip install -r requirements.txt` (preferably in a virtual environment) to install mkdocs and
all other dependencies.  Serve locally with `mkdocs serve`.

### Deploying with rsync
Create the following `deploy.sh` bash script:
```bash
#!/bin/bash
mkdocs build -q
rsync -az --partial --delete site/ user@hostname:/path/to/destination
```
Do not forget to run `chmod +x deploy.sh`.
