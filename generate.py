import glob
from os.path import basename
from markdown import markdown

OUTPUT = './site/'
INPUT = './src/*'
for file in glob.glob(INPUT):
    with open(file) as infile:
        print(OUTPUT + basename(file.replace('.md', '.html')))
        print(markdown(infile.read()))
