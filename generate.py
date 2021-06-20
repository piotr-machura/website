from os import makedirs
from os.path import relpath, basename
from glob import glob
from datetime import datetime
from shutil import rmtree, copytree
from markdown import Markdown
from jinja2 import Environment, FileSystemLoader as fsl


class Document:
    env = Environment(loader=fsl(searchpath="./templates"))

    def __init__(self, path):
        self.path = ('./site/' + relpath(path, './src')).replace(
            '.md', '.html')
        self.basename = basename(self.path)
        with open(path) as f:
            md = Markdown(extensions=['meta'])
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
    makedirs('./site/projects/')
    makedirs('./site/blog/')
    makedirs('./site/writing/')
    copytree('./src/res', './site/res')

    # Render 404 page
    Document.render_static('404.html', './site/404.html')

    # Render homepage
    home = Document('./src/index.md')
    home.render(template='home.html')

    # Compile blog
    articles = glob('./src/blog/*')
    articles.remove('./src/blog/index.md')
    articles = sorted(
        [Document(article) for article in articles],
        key=lambda el: datetime.strptime(el.meta['date'], "%Y-%m-%d"),
        reverse=True,
    )
    for article in articles:
        article.render(template='article.html')

    blog = Document('./src/blog/index.md')
    blog.render(template='blog.html', listing=articles)

    # Render projects
    projects = glob('./src/projects/*')
    projects.remove('./src/projects/index.md')
    projects = sorted(
        [Document(project) for project in projects],
        key=lambda el: datetime.strptime(el.meta['date'], "%Y-%m-%d"),
        reverse=True,
    )
    for project in projects:
        project.render(template='project.html')

    proj_idx = Document('./src/projects/index.md')
    proj_idx.render(template='projects.html', listing=projects)

    # Render writing page
    writing = Document('./src/writing/index.md')
    writing.render(template='writing.html')
