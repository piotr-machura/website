# Personal website source
This is the source for my personal website. It contains whatever I feel like throwing on there.

It is built from markdown files using [python-markdown](https://pypi.org/project/Markdown/) and
[jinja2](https://pypi.org/project/Jinja2/) template engine. The only JavaScript used is [KaTeX](https://katex.org/) for
math typesetting and [highligh.js](https://highlightjs.org/) for syntax highlighting.

## Building
After puling with git run `pip install -r requirements.txt` (preferably in a virtual environment) to install build dependencies.
Build with `python build.py`, serve locally with `python3 -m http.server --directory ./site`.

## Deploying
To a remote location with rsync:
```bash
#!/bin/bash
source ./.venv/bin/activate # Optional: activate the virtual environment
set -xe
python3 build.py
rsync --archive --compress --partial --delete \
    site/ user@hostname:/path/to/your/site/
```
To Sourcehut pages:
```bash
#!/bin/bash
source ./.venv/bin/activate # Optional: activate the virtual environment
set -xe
python build.py
tar -C site/ -cz . > site.tar.gz
curl --oauth2-bearer "your sourcehut ouath2 token" \
    -Fcontent=@site.tar.gz https://pages.sr.ht/publish/your.sourcehut.domain
rm -rf site.tar.gz
```
