"""Site generation script.

After installing the requirements run `python3 generate.py` to generate the
website in the ./site directory.

**WARNING:** All contents of ./site will be deleted.
"""

from os.path import relpath, basename
from glob import glob
from datetime import datetime
from shutil import rmtree, copytree, ignore_patterns
from markdown import Markdown
from jinja2 import Environment, FileSystemLoader
# pylint: disable=C0115, C0103, C0116


class Document:
    env = Environment(loader=FileSystemLoader(searchpath="./templates"))

    def __init__(self, path):
        self.path = ('./site/' + relpath(path, './src')).replace(
            '.md', '.html')
        self.basename = basename(self.path)
        with open(path) as f:
            md = Markdown(
                extensions=['meta', 'extra', 'toc', 'markdown_del_ins'])
            self.content = md.convert(f.read())
            self.meta = md.Meta
        for el in self.meta:
            self.meta[el] = ' '.join(self.meta[el])

    @classmethod
    def render_static(cls, template_name, path, **kwargs):
        with open(path, 'w') as f:
            f.write(cls.env.get_template(template_name).render(**kwargs))

    def render(self, template, **kwargs):
        with open(self.path, 'w') as f:
            f.write(
                self.env.get_template(template).render(
                    content=self.content,
                    meta=self.meta,
                    **kwargs,
                ),
            )


if __name__ == '__main__':
    # Prepare file tree
    rmtree('./site/')
    copytree('./src', './site', ignore=ignore_patterns('*.md', '*.pdf'))

    # Render error pages
    for code in ['403', '404', '500', '502', '503', '504']:
        Document.render_static(
            'error.html',
            './site/' + code + '.html',
            code=code,
            redirect=(int(code) < 500), # Redirect 400 codes to home
        )

    # Render homepage
    home = Document('./src/index.md')
    home.render(template='home.html')

    # Render blog
    articles = glob('./src/blog/*.md')
    articles.remove('./src/blog/index.md')
    articles = sorted(
        [Document(article) for article in articles],
        key=lambda el: datetime.strptime(el.meta['date'], "%Y-%m-%d"),
        reverse=True,
    )
    for article in articles:
        article.render(template='article.html')

    blog = Document('./src/blog/index.md')
    blog.render(template='listing.html', listing=articles, date=True)

    # Render projects
    projects = glob('./src/projects/*.md')
    projects.remove('./src/projects/index.md')
    projects = sorted(
        [Document(project) for project in projects],
        key=lambda el: datetime.strptime(el.meta['date'], "%Y-%m-%d"),
        reverse=True,
    )
    for project in projects:
        project.render(template='project.html')

    proj_idx = Document('./src/projects/index.md')
    proj_idx.render(template='listing.html', listing=projects)

    # Render writing page
    writing = Document('./src/writing/index.md')
    writing.render(template='writing.html')
