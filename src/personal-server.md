# Personal server setup

![Docker logo](img/docker_logo.png)

The goal of this project is to create a personal server that will host a static website, fully capable email stack and a
webmail client. Docker makes the process of configuration and deployment faster and tidier, allowing us to construct the
server from *almost* ready-to-go parts. It also makes the installation pretty much host-independent, as in the host's
operating system does not matter as long as docker engine and docker-compose are available.

We will use the following open source software to create our server:

- **Web server:** [nginx](https://nginx.org/), modified to include [certbot](https://certbot.eff.org) for ease of
   obtaining and renewing LetsEncrypt SSL certificates. 
- **Email stack:** [docker-mailserver](https://github.com/docker-mailserver/docker-mailserver), configured to maximize
   the probability of not landing in Gmails spam folder.
- **Webmail client:** [Roundcube](https://roundcube.net/) with [context
   menu](https://github.com/JohnDoh/roundcube-contextmenu), [persistent
   login](https://github.com/mfreiholz/persistent_login) and [CardDAV](https://github.com/mstilkerich/rcmcarddav) plugins.
- **CardDAV server:** [Radicale](https://radicale.org/3.0.html), used to sync Roundcube contacts with e.g.  an
   Android phone.

A simplified schema of the server is portrayed below, keep in mind all of the software will be running in their own
respective Docker conatiners.

![Simplified server diagram](img/server_diagram.svg)

## DNS records
The following notation will be used:

- X.X.X.X will denote the static host **IPv4 address**.
- example.com will denote the **base domain** purchased at the registrar.

We will set the following dns records (arrow meaning "pointing to"):

| **A** | **CNAME** | **MX** | **TXT** |
| --- | --- | --- | --- |
| example.com → X.X.X.X | dav.example.com → example.com | mail.example.com | DKIM |
| www.example.com → X.X.X.X | | | DMARC |
| mail.example.com → X.X.X.X | | | SPF|

The above mentioned TXT records ensure no email spoofing has taken place and greatly increase the probability of our
messages not being flagged as spam. They require the server to be already running and are discussed in more detail in
*"Mail server best practices"*.

# The nginx reverse proxy
All of our services (with email being the only exception) will be served through an instance of the nginx web server
acting as a **reverse proxy**. This ensures that all connections with the outside world are utilizing HTTPS protocol
and, as a consequence, SSL encryption.
