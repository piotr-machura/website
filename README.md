# Personal website source
This is the source for my personal website. It contains whatever I feel like throwing on there.

It is built from markdown files using [python-markdown](https://pypi.org/project/Markdown/) and
[jinja2](https://pypi.org/project/Jinja2/) template engine. The only JavaScript used is [KaTeX](https://katex.org/).

### Installation
After puling with git run `pip install -r requirements.txt` (preferably in a virtual environment) to install build dependencies.
Serve locally with `python3 -m http.server --directory ./site`.

### Deploying with rsync after every commit
Create a `deploy.sh` bash script 
```bash
#!/bin/bash -xe
python3 build.py
rsync --archive --compress --partial --delete \
    site/ user@hostname:/path/to/my/site/
```
Run `chmod +x deploy.sh` and link it to git hook directory `ln -s deploy.sh .git/hooks/post-commit`.
