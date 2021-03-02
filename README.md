# Personal website source
This is my personal website, built with [MkDocs](https://mkdocs.org). It contains whatever I feel like throwing on
there.

## Easy deployment
Create the following bash script:
```bash
#!/bin/bash
mkdocs build
rsync -avzP site/ <user>@<remote server>:<destination>
# Optional for docker-compose based servers
ssh <user>@<remote server> "cd /path/to/docker/compose; docker-compose restart;"
```
Do not forget to run `chmod +x deploy.sh`.
