Title:        This very website
Description:  Yes, the one you're on right now
Author:       Piotr Machura
Date:         2021-06-19
Repository:   https://sr.ht/~piotr-machura/website/

Picture this: you want to have your own website, some place on the Internet just for you and your thoughts. So now
you have three options:

1. Use a static site generator like MkDocs or Hugo, which is very appealing.
2. Use a bloated, LAMP based platform like WordPress, which is even more appealing.
3. Walk the righteous path and simply edit the HTML by hand, which is frankly repulsing.

You know me, I was in the 3rd "DIY, no bloat, no javascript" crew, spending hours upon hours trying to build do own
thing by copying a "template" *(foreshadowing?)* HTML file and populating it's contents.

Eventually, though, I decided to forfeit my software purism and use a static site generator. You know, a thing that
takes some markdown files and lumps them together, adding css and js along the way.

Alas, no static site generator was quite right for me. I needed something simple, and something I would have full
control of. So I did the only reasonable thing, and wrote my own.

## Templates are easy
There is an old saying that programmers don't do thing because they are easy, but because they *thought* they were easy.
The solution to my website problem turned out to be quite the opposite - as it turns out, templates really are just that
easy.

The whole project took less than two days to complete, totaling *maybe* 6 hours of work. Most of which I spent on the
website's design, tweaking CSS to make it minimalist and good looking (Did I succeed? You tell me). The only piece of js
on this site is [KaTeX](https://katex.org/), which renders math. Useful if you want fancy equations on your website, and
I do.

It has also made it clear to me why people like python so much. It allows you to hack together a solution to a problem
that does not require neither speed nor excessive control over details like memory management. You can have a website
generator up and running with two imports ([python-markdown](https://pypi.org/project/Markdown/) and
[Jinja2](https://pypi.org/project/Jinja2/)) and a total of ~70 lines of code.

This is the kind of scenario where python
shines - short development time and a wide array of ready-to-go solutions to high level problems like this one.

As a side note, my girlfriend is not a fan of the new style. Quote:

> The website looks like it's broken.

> Like there's been an error, or something.

Not everyone likes the minimalist style, or doing everything by yourself, and that's ok. But I do.
