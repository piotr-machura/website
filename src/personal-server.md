---
toc: true
---
# Personal server setup

![Docker logo](img/docker_logo.png)

The goal of this project is to create a personal server that will host a static website, fully capable email stack and a
webmail client. Docker makes the process of configuration and deployment faster and tidier, allowing us to construct the
server from *almost* ready-to-go parts. It also makes the installation pretty much host-independent, as in the host's
operating system does not matter as long as docker engine and docker-compose are available.

We will use the following open source software to create our server:

- **Web server:** [nginx](https://hub.docker.com/_/nginx/), modified to include [certbot](https://certbot.eff.org) for
   ease of obtaining and renewing LetsEncrypt SSL certificates. 
- **Email stack:** [docker-mailserver](https://hub.docker.com/r/mailserver/docker-mailserver), configured to maximize
   the probability of not landing in Gmails spam folder.
- **Webmail client:** [Roundcube](https://hub.docker.com/r/roundcube/roundcubemail) with [context
   menu](https://github.com/JohnDoh/roundcube-contextmenu), [persistent
   login](https://github.com/mfreiholz/persistent_login) and [CardDAV](https://github.com/mstilkerich/rcmcarddav) plugins.
- **CardDAV server:** [Radicale](https://hub.docker.com/r/xlrl/radicale), used to sync Roundcube contacts with e.g.  an
   Android phone.

A simplified schema of the server is portrayed below, keep in mind all of the software will be running in their own
respective Docker conatiners.

![Simplified server diagram](img/server_diagram.svg)
