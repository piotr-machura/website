# ⚠️ This is and old version ⚠️
This is my personal website, built with [MkDocs](https://mkdocs.org). It contains whatever I feel like throwing on
there.

### Installation
After puling with git run `pip install -r requirements.txt` (preferably in a virtual environment) to install mkdocs and
all other dependencies.  Serve locally with `mkdocs serve`.

### Deploying with rsync after every commit
Create the following hook at `./git/hooks/post-commit`:
```bash
#!/bin/bash -xe
mkdocs build --quiet --clean
rsync --archive --compress --partial --delete \
    site/ user@hostname:/path/to/site/
```
Do not forget to run `chmod +x ./.git/hooks/post-commit`.
