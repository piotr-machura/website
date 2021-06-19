import os
from glob import glob
from datetime import datetime
from shutil import copytree
from markdown import Markdown
import jinja2

template_loader = jinja2.FileSystemLoader(searchpath="./templates")
template_env = jinja2.Environment(loader=template_loader)


def md_compile(inpath):
    markdown = Markdown(extensions=['meta'])
    with open(inpath) as infile:
        return markdown.convert(infile.read()), markdown.Meta


# Copy resources
copytree('./src/res', './site/res', dirs_exist_ok=True)

# Compile 404 page
template = template_env.get_template('404.html')
with open('./site/404.html', 'w') as outfile:
    outfile.write(template.render())

# Compile homepage
content, meta = md_compile('./src/index.md')
template = template_env.get_template('home.html')
with open('./site/index.html', 'w') as outfile:
    outfile.write(template.render(
        meta=meta,
        content=content,
    ))

# Compile articles
os.makedirs('./site/blog/', exist_ok=True)
articles = glob('./src/blog/*')
articles.remove('./src/blog/index.md')
meta_list = sorted(
    [md_compile(file)[1] for file in articles],
    key=lambda el: datetime.strptime(el['date'][0], "%Y-%m-%d"),
    reverse=True,
)

files = [
    '/blog/' + os.path.basename(file).replace('.md', '.html')
    for file in articles
]

template = template_env.get_template('article.html')
for article, file in zip(articles, files):
    with open('./site' + file, 'w') as outfile:
        content, meta = md_compile(article)
        outfile.write(template.render(
            meta=meta,
            content=content,
        ))

template = template_env.get_template('article_index.html')
content, meta = md_compile('./src/blog/index.md')
with open('./site/blog/index.html', 'w') as outfile:
    outfile.write(
        template.render(
            meta=meta,
            content=content,
            listing=zip(files, meta_list),
        ))

# Compile projects
os.makedirs('./site/projects/', exist_ok=True)
projects = glob('./src/projects/*')
projects.remove('./src/projects/index.md')
meta_list = sorted(
    [md_compile(file)[1] for file in projects],
    key=lambda el: datetime.strptime(el['date'][0], "%Y-%m-%d"),
    reverse=True,
)

files = [
    '/projects/' + os.path.basename(file).replace('.md', '.html')
    for file in projects
]

template = template_env.get_template('project.html')
for article, file in zip(projects, files):
    with open('./site' + file, 'w') as outfile:
        content, meta = md_compile(article)
        outfile.write(template.render(
            meta=meta,
            content=content,
        ))

template = template_env.get_template('project_index.html')
content, meta = md_compile('./src/projects/index.md')
with open('./site/projects/index.html', 'w') as outfile:
    outfile.write(
        template.render(
            meta=meta,
            content=content,
            listing=zip(files, meta_list),
        ))
