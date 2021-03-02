# Personal website source
This is my personal website, built with [MkDocs](https://mkdocs.org). It contains whatever I feel like throwing on
there.

### Installation
After puling with git run `pip install -r requirements.txt` (preferably in a virtual environment) to install mkdocs and
all other dependencies.  Serve locally with `mkdocs serve` and deploy using `mkdocs build` or a custom script.

### Easy deployment
Create the following `deploy.sh` bash script:
```bash
#!/bin/bash
mkdocs build
rsync -avzP --delete site/ user@hostname:/path/to/destination
# Optional for docker-compose based servers
ssh user@hostname "cd /path/to/docker/compose; docker-compose restart;"
```
Do not forget to run `chmod +x deploy.sh`.
