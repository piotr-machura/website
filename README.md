# Personal website source
This is the source for my personal website. It contains whatever I feel like throwing on there.

It is built from markdown files using [python-markdown](https://pypi.org/project/Markdown/) and
[jinja2](https://pypi.org/project/Jinja2/) template engine. The only JavaScript used is [KaTeX](https://katex.org/).

### Installation
After puling with git run `pip install -r requirements.txt` (preferably in a virtual environment) to install build dependencies.
Serve locally with `python3 -m http.server --directory ./site`.

### Deploying with rsync
Create a `deploy.sh` bash script 
```bash
#!/bin/bash -xe
source ./.venv/bin/activate # Optional: activate the virtual environment
python3 build.py
rsync --archive --compress --partial --delete \
    site/ user@hostname:/path/to/my/site/
```
Do not forget to `chmod +x deploy.sh`. In order to deploy automatically after ever commit link it to git hook directory
`ln -s deploy.sh .git/hooks/post-commit`.
