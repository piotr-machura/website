# Personal website source
This is the source for my personal website. It contains whatever I feel like throwing on there.

It is built from markdown files using [python-markdown](https://pypi.org/project/Markdown/) and
[jinja2](https://pypi.org/project/Jinja2/) template engine. The only JavaScript used is [KaTeX](https://katex.org/).

### Installation
After puling with git run `pip install -r requirements.txt` (preferably in a virtual environment) to install build dependencies.
Serve locally with `python3 -m http.server --directory ./site`.

### Deploying with rsync after every commit
Create a hook at `./git/hooks/post-commit`:
```bash
#!/bin/bash -xe
python3 build.py
rsync --archive --compress --partial --delete \
    site/ user@hostname:/path/to/my/site/
```
Do not forget to run `chmod +x ./.git/hooks/post-commit`.
