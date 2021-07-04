Title:        Personal server
Description:  Your very own platform, with Docker
Repository:   https://sr.ht/~piotr-machura/personal-server/
Date:         2021-04-18

# Personal server
I have wanted to get away from Google for quite some time now. The first step, obviously, is switching to DuckDuckGo,
but after that things get significantly harder. I needed something to replace Gmail (for obvious reasons) and Google
Contacts (as it is quite handy to have the same contact book in your email and your phone). It just so happens my needs
were pretty clear this time around:

- email server with my own domain name;
- webmail client with PGP encryption support;
- CardDAV integration, to sync the contacts with my phone (using [davx5](https://www.davx5.com/)).

And, while we're at it, some place to host this very website. All of this open source (of course), and with as much
control as I can have over it.

You can probably guess how it ended. I just did it myself.


## With FOSS help
As it turns out, there are FOSS solutions to all of the above, and *almost* all of them have ready-to-go Docker
containers. With the help of [nginx](), [docker-mailserver](), [Roundcube]() and [Radicale]() my server was brought to
life in a span of a few weeks, totaling maybe two days of total work.

It was overall much easier than I thought it would be, which is always a pleasant surprise. The only part I had some
trouble with was obtaining SSL certificates with Certbot, which *does* have a standalone Docker container, but requires
access to host's port 80 to perform the challenges. And, as you can probably guess, port 80 is already occupied by
nginx, serving this very website. I was trying to introduce some sort of complex dance, in which nginx would shut itself
down while Certbot did it's thing, but ultimately packaging the two in a single container proved to be the easiest and
cleanest solution.

After that hiccup it was all smooth sailing, even containerizing Radicale (for which a first party Docker container does
not exist) proved to be extremely easy.

## Containers and portability
There is a problem with doing all of this yourself - it needs to be **reliable**. Email is a pretty important thing,
and you don't want it to *not* work. If it fails, you better have a plan to bring it back up to speed as fast as
possible.

The thing about containers is that they are **portable** (it's the reason they exist). Data files are contained in a
single directory, which can be automatically tarballed and SCP'd to a backup location, creating a
backup every hour (or however often you please). Then, in the event of some failure, I can simply:

1. nuke the server (if necessary);
2. pull the setup repository from remote (GitHub or Sourcehut);
3. untar the backup into the data directory;
4. run `admin.sh -i` (or just `docker-compose up -d --build` if I haven't completely nuked the server)…

…and things are back up and running in ~5 minutes. The same is true for the migration case - changing the VPS provider
is as simple as executing steps 2-4, with the addition of changing the IP addresses in DNS records to the new
virtual machine.
 
I want the things I maintain to be **reliable** and **reproducible** - in the event I screw things up or my house burns
down I want to be able to get my setups up and running as quickly and painlessly as possible, exactly the same as they
were before the disaster struck. Containers are awesome for that.
