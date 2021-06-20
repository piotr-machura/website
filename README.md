# Personal website source
This is my personal website, built with [MkDocs](https://mkdocs.org). It contains whatever I feel like throwing on
there.

### Installation
After puling with git run `pip install -r requirements.txt` (preferably in a virtual environment) to install build dependencies.
Serve locally with `python3 -m http.server --directory ./site`.

### Deploying with rsync after every commit
Create the following hook at `./git/hooks/post-commit`:
```bash
#!/bin/bash -xe
python3 build.py
rsync --archive --compress --partial --delete \
    site/ user@hostname:/path/to/site/
```
Do not forget to run `chmod +x ./.git/hooks/post-commit`.
