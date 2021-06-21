Title:        Personal server
Description:  Your very own platform, with Docker
Repository:   https://github.com/piotr-machura/personal-server/
Date:         2021-04-18

# Personal server

![Docker logo](/res/img/docker_logo.png)

We will use the following open source software to create our server:

- **Web server:** [nginx](https://nginx.org/), modified to include [certbot](https://certbot.eff.org) for ease of
   obtaining and renewing LetsEncrypt SSL certificates.
- **Email stack:** [docker-mailserver](https://docker-mailserver.github.io/docker-mailserver/v9.1/), configured to maximize
   the probability of not landing in Gmails spam folder.
- **CardDAV server:** [Radicale](https://radicale.org/3.0.html), used to sync Roundcube contacts with e.g.  an
   Android phone.

A simplified schema of the server is portrayed below, keep in mind all of the software will be running in their own
respective Docker conatiners.

<img style="background-color: white;" src="/res/img/server_diagram.png" alt="Simplified server diagram"></img>

# Setting up the server
The following notation will be used:

- X.X.X.X will denote the static host **IPv4 address**.
- example.com will denote the **base domain** purchased at the registrar.
- ./ will denote the root of the project (ie. the directory containing docker-compose.yml).

The source code required for the implementation is available in the associated [GitHub
repository](https://github.com/piotr-machura/personal-server/).

### Project structure
The project structure is as follows:
```
./
│
├─ config/
│  ├─ radicale/
│  ├─ roundcube/
│  └─ nginx/
│
├─ build/
│  ├─ radicale/
│  ├─ nginx-certbot/
│  └─ roundcube/
│
├─ data/
│  ├─ roundcube/
│  ├─ nginx/
│  ├─ radicale/
│  ├─ mailserver/
│  └─ letsencrypt/
│
├─ docker-compose.yml
└─ admin.sh
```

### DNS records

We will set the following dns records (arrow meaning "pointing to"):

| A | CNAME | MX | TXT |
| --- | --- | --- | --- |
| example.com → X.X.X.X | dav.example.com → example.com | *empty* → mail.example.com | DKIM |
| www.example.com → X.X.X.X | | | DMARC |
| mail.example.com → X.X.X.X | | | SPF|

The above mentioned TXT records ensure no email spoofing has taken place and greatly increase the probability of our
messages not being flagged as spam. They require the server to be already running and are discussed in more detail in
[#Mail server administration](#mail-server-administration).

### Skeleton docker-compose.yml
Create a skeleton of docker-compose.yml file as follows:
```yaml
version: '3'
services:
  # Service sections will go here

networks:
  default:
    name: service_network
```
Containers under the `services` key are automatically added to the default network. We have therefore rennamed it to
`service_network` for clarity.

## Reverse proxy
All of our services (with email being the only exception) will be served through an instance of the nginx web server
acting as a **reverse proxy**. This ensures that all connections with the outside world are utilizing HTTPS protocol
and, as a consequence, SSL encryption. To achieve this we will use the **nginx** web server, modified to include the
**Certbot** LetsEncrypt client. This will allow us to automatically obtain and renew the SSL certificates for all of our
domains.

**Note:** there exists an official [Certbot](https://hub.docker.com/r/certbot/certbot) docker container, but it requires
access to host's port 80 for accepting the HTTP challenges when obtaining/renewing certificates. This conflicts with the
nginx container, and would require some intricate mechanizm that would stop the nginx container every time Certbot tries
to renew SSL certificates, ie. once per day, and then restarting nginx once Certbot is done. The solution proposed here
is, in author's opinion, much simpler.

### Nginx-certbot image

We shall start by writing a new Dockerfile under `./build/nginx-certbot/Dockerfile`. We will use the `nginx:alpine`
official image as our base and install Certbot and it's nginx plugin from official Alpine Linux repositories.
```dockerfile
FROM nginx:alpine

RUN set -xe; \
    apk add certbot certbot-nginx; \
    mkdir /etc/letsencrypt /var/log/letsencrypt
```
We have also created the directories used by Certbot for storing certificates and renewal logs. To make the data
persistent we use docker volumes.
```dockerfile
VOLUME ["/etc/letsencrypt"]
VOLUME ["/var/log/letsencrypt"]
```
Alpine Linux does not come with the usual cron utility. We have to create a shell script in an appropriate location and
start the crond task daemon in the background when the container starts.
```dockerfile
COPY ./renew /etc/periodic/daily/renew
RUN chmod +x /etc/periodic/daily/renew
```
Provide the renew script by writing the `./build/nginx-cerbot/renew`.
```bash
#!/bin/sh
sleep $(($RANDOM % 60))m
certbot renew
```
The first line delays the renewal by a random time between 0 and 60 minutes, as LetsEncrypt recommends attempting
renewal at different times each day. All that remains is to modify the container's entry point to start the crond which
will execute the above script.
```dockerfile
CMD sh -c "crond; nginx -g 'daemon off;'"
```
Notice that the nginx web server is started with the 'daemon off' option to keep it in the foreground. This is because a
docker container will exit once no processes are running in the foreground.

### Configuring the web server
To host the static content stored in `./data/nginx/default` on the website root create a basic configuration file in
`./config/nginx/default.conf`.
```nginx
server {
    listen       80;
    server_name  example.com www.example.com;

    location / {
        root /usr/share/nginx/html/default;
        index index.html index.htm;
    }

    error_page 404 /404.html;
    location /404.html {
        root   /usr/share/nginx/html/default;
    }
}
```
The default server responds to requests on port 80 for our base domain and WWW sub domain, hosting the static content
from `/usr/share/nginx/html/default` (corresponding to `./data/nginx/default` on host machine). Do not worry about SSL
certificates and HTTP to HTTPS redirects, as those will be automatically added by Certbot.

**Note:** it is important that initial nginx configuration files **do not contain** a reference to the certificates
**unless those are already present** (eg. backed up from a previous installation), as nginx will error and exit with
'file not found' message. It is therefore advisable not to version controll additional changes to the configuration
after the server has been deployed (or even add the entire `./config/nginx` directory to a `.gitignore`).

### Nginx docker-compose section
All that is left is to setup the launch of our container inside `./docker-compose.yml` under the `services`
key.
```yaml
webserver:
  build: ./build/nginx-certbot
  image: local/nginx-certbot
  container_name: nginx-certbot
  restart: unless-stopped
  volumes:
    - ./config/nginx:/etc/nginx/conf.d
    - ./data/nginx:/usr/share/nginx/html:ro
    - ./data/letsencrypt:/etc/letsencrypt
  ports:
    - "80:80"
    - "443:443"
```
We have named our image `local/nginx-certbot` and docker-compose will automatically build it from source files in
`./build/nginx-certbot` if it's not already present on the system. The container's HTTP and HTTPS ports are published as
corresponding host's ports and the container will restart if nginx crashes. The `default.conf` we have just written
(and any other file in `./config/nginx` will be automatically sourced thanks to an 'include' directive in the default
nginx config.

Note that while the static website data is bound as read only, the configuration and certificate volumes are not. This
is because they will be modified by Certbot when the certificates are obtained.

## CardDAV server
CardDAV is an internet protocol based on HTTP used for synchronizing address books between devices and services. On iOS
the default contacts can connect to a CardDAV server, and there exist multiple open source solutions allowing the same
on Android.

We will be hosting a CardDAV server called [Radicale](https://radicale.org/3.0.html), which is free, open source and
extremely lightweight. Unfortunately, there is no first-party Docker container, so we will have to create one ourselves.

### Radicale image
Create a new Dockerfile in the `./build/radicale` directory, starting from the base Alpine Linux image and adding
software required by the CardDAV server.
```dockerfile
FROM alpine:3.13.2
RUN set -xe && \
    apk add --no-cache apache2-utils python3 py3-bcrypt py3-cffi py3-pip; \
    pip3 install bcrypt passlib pytz radicale; \
    mkdir -p /var/radicale/data/collections /var/radicale/config; \
    touch /var/radicale/data/users
```
You may have noticed that, aside from required python tools, we have installed `apache2-utils`. This is because the most
secure way of authenticating Radicale users is with Apache's `htpasswd`, and that's what we will use. We have also
created two directories - one for the user data and one for configuration, as well as a file `users` used by `htpasswd`.

Next, we will need to write a configuration file for Radicale. Create `./build/radicale/config.ini` and fill it with the
following contents.
```ini
[auth]
type = htpasswd
htpasswd_filename = /var/radicale/data/users
htpasswd_encryption = bcrypt

[server]
hosts = 0.0.0.0:8000

[storage]
filesystem_folder = /var/radicale/data/collections
```
Most setting are pretty self explanatory. We have chosen bcrypt as the password encryption algorithm and we the
container will host Radicale on port 8000. Copy the file to `./config/radicale` and to finish the container.
```dockerfile
COPY ./config.ini /var/radicale/config/config.ini

VOLUME ["/var/radicale/data"]
VOLUME ["/var/radicale/config"]

EXPOSE 8000

CMD sh -c "python3 -m radicale --config /var/radicale/config/config.ini"
```
We copy the configuration, expose data and config volumes, as well as our chosen port. The container's entry point is
simply Python launching Radicale with our configuration file.

### CardDAV docker-compose section
Let's add the new container to our `./docker-compose.yml` under the `services` key.
```yaml
carddav:
  build: ./build/radicale
  image: local/radicale
  container_name: radicale
  restart: unless-stopped
  volumes:
    - ./config/radicale:/var/radicale/config:ro
    - ./data/radicale:/var/radicale/data
```
We have named our image `local/radicale` and our container `radicale`. Notice that we have not **published** any ports.
This is because we will use our nginx container to act as a reverse proxy, redirecting HTTPS encrypted traffic to
Radicale.

### CardDAV reverse proxy
All we have to do is add new virtual host in `./config/nginx/dav.conf` (remember that all files in
`./config/nginx` are sourced automatically), pointing all HTTP requests for host `dav.exapmle.com` to our Radicale
container, port 8000.
```nginx
server {
    listen 80;
    server_name dav.example.com;
    location / {
        proxy_pass http://radicale:8000/;
    }
}
```
The key to the reverse proxy is the `proxy_pass` directive. Thanks to the Docker network connecting our containers we
can refer to the Radicale container by it's name, and Docker will resolve that to the IP address of said container in
the Docker network. This way there is no need to expose additional ports on the host or worry about encrypting the
traffic between the CardDAV server and the Internet, as the connection is established between the client and nginx, and
then relayed internally to Radicale, and all connections with nginx will be encrypted once we get our certificates from
Certbot.

## Email client
Our server will host a web email client, providing easy access to the soon-to-be created email server. The software of
choice is [Roundcube](https://roundcube.net), am open source PHP email client with desktop and mobile interfaces. We
will customize it with some community plugins, adding additional functionality.

### Roundcube image
Start by extending the base Roundcube image by writing a new Dockerfile in the `./build/roundcube` directory.
```dockerfile
FROM roundcube/roundcubemail:latest
```
In order to install plugins we need [Composer](https://getcomposer.org/), a dependency management tool for PHP.
```dockerfile
RUN set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends git; \
    curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer; \
    mv /usr/src/roundcubemail/composer.json-dist /usr/src/roundcubemail/composer.json; \
    composer \
        --working-dir=/usr/src/roundcubemail/ \
        --prefer-dist --prefer-stable \
        --no-update --no-interaction \
        --optimize-autoloader --apcu-autoloader \
        require \
            johndoh/contextmenu \
            roundcube/carddav \
            texxasrulez/persistent_login  \
            kitist/html5_notifier \
    ; \
    composer \
        --working-dir=/usr/src/roundcubemail/ \
        --prefer-dist --no-dev \
        --no-interaction \
        --optimize-autoloader --apcu-autoloader \
        update;
```
Our plugins are listed after the `composer ... require` command, with the flags recommended in Roundcube documentation.
Feel free to add your own from the [Roundcube plugins repository](https://packagist.org/?type=roundcube-plugin).
The `composer ... update` command downloads plugins and required dependencies at the time of building the image.

In order to utilize the plugins they need to be enabled in Roundcube configuration file. Provide it by writing
`./config/roundcube/config.php`.
```php
<?php
$config['plugins'] = [
  'archive',
  'zipdownload',
  'carddav',
  'persistent_login',
  'html5_notifier',
  'contextmenu'
];
```
Add all of the plugins you installed with Composer. The `archive` and `zipdownload` are provided by default.

### Roundcube docker-compose section
Add the newly created image to the `./docker-compose.yml` under the `services` key.
```yaml
webmail:
  build: ./build/roundcube
  image: local/roundcube
  container_name: roundcube
  restart: unless-stopped
  volumes:
    - ./config/roundcube:/var/roundcube/config:ro
    - ./data/roundcube:/var/roundcube/db
  environment:
    - ROUNDCUBEMAIL_DB_TYPE=sqlite
    - ROUNDCUBEMAIL_SKIN=elastic
    - ROUNDCUBEMAIL_UPLOAD_MAX_FILESIZE=75M
    - ROUNDCUBEMAIL_DEFAULT_HOST=tls://mail.example.com
    - ROUNDCUBEMAIL_SMTP_SERVER=tls://mail.example.com
```
Notice that the IMAP and SMTP host names point to our domain's MX record, and are utilizing TLS encryption by default.
We have bound the database and configuration volumes to our host machine, but yet again no ports have been exposed. This
is because, as with the CardDAV server, we will access our email client through the nginx proxy.

### Roundcube reverse proxy
Edit the `./config/nginx/default.conf` file to include the following inside the `server {}` block.
```nginx
# ...
location /mail/ {
   proxy_set_header Host $host;
   proxy_pass http://roundcube:80/;
}
# ...
```
Note the trailing slash in `/mail/` and after the port number. Again, thanks to the Docker network we can refer to the
Roundcube container by it's name and redirect `http(s)://example.com/mail` to the email client web interface.

## Email server
Hosting and maintaining an email server is widely considered notoriously difficult. One has to worry about the
cooperation between the SMTP (mail **transfer** protocol) and the IMAP (mail **access** protocol) services, SPAM index
of popular mail providers, as well as the security implications of receiving arbitrary data (in the form of attachments)
from anyone on the internet.

Fortunately, there exist multiple "batteries included" solutions, many of them available as Docker images. Our stack of
choice is the [docker-maislerver](https://github.com/docker-mailserver/docker-mailserver), which provides all of the
tools required to deploy and maintain an email server, together with quality-of-life features like the
[SpamAssasin](https://spamassassin.apache.org/) SPAM filter, [ClamAV](https://www.clamav.net/) antivirus and
anti-spoofing provided by [OpenDKIM](http://www.opendkim.org/) and
[OpenDMARC](https://github.com/trusteddomainproject/OpenDMARC).

### Mail server docker-compose section
The docker-mailserver image does not require any modifications, and most of the configuration is done via environment
variables. Add the container to `./docker-compose.yml` under `services` key.
```yaml
mailserver:
  image: mailserver/docker-mailserver:latest
  container_name: mailserver
  restart: always
  hostname: mail
  domainname: example.com
  ports:
   - "25:25"
   - "143:143"
   - "587:587"
   - "993:993"
  volumes:
   - ./data/mailserver/mail:/var/mail
   - ./data/mailserver/state:/var/mail-state
   - ./data/mailserver/logs:/var/log/mail
   - ./data/mailserver/config:/tmp/docker-mailserver
   - ./data/letsencrypt:/etc/letsencrypt:ro
   - /etc/localtime:/etc/localtime:ro
  environment:
   - ONE_DIR=1
   - SPOOF_PROTECTION=1
   - ENABLE_CLAMAV=1
   - ENABLE_AMAVIS=1
   - POSTSCREEN_ACTION=enforce
   - SSL_TYPE=letsencrypt
   - POSTFIX_MAILBOX_SIZE_LIMIT=10000000000
   - POSTFIX_MESSAGE_SIZE_LIMIT=80000000
   - POSTFIX_INET_PROTOCOLS=ipv4
   - ENABLE_SPAMASSASSIN=1
   - SPAMASSASSIN_SPAM_TO_INBOX=1
   - MOVE_SPAM_TO_JUNK=1
  cap_add:
   - "NET_ADMIN"
   - "SYS_PTRACE"
```
Our container publishes common IMAP/SMTP host ports and it restarts **always**, since while a mail server is down all
messages send to associated addresses will bounce. We give the container numerous volumes in our `./data` directory,
including access to the SSL certificates soon-to-be generated by Certbot. We also synchronize the local time of the
container with the host by sharing `/etc/localtime`.

The configuration done by environment variables is documented in [docker-mailserver's official
documentation](https://docker-mailserver.github.io/docker-mailserver/v9.1/). Many other options are available, and it is
recommended to go through them and modify the `environment` key as necessary.

### Using Certbot to obtain email-related SSL certificates
Certbot analyzes the nginx configuration and validates domains found in the server names. In order to
obtain certificates for the mail.example.com host used by IMAP nad SMTP protocols, we have to add another configuration
file under `./config/nginx/mail.conf`.
```nginx
server {
    listen 80;
    server_name mail.example.com;
    return 301 https://example.com/mail/
}
```
This virtual host simply redirects all HTTP(S) requests for mail.example.com to the location of the Roundcube container.


# First launch
All of the following steps are accomplished using the `./admin.sh` script provided in the associated
[GitHub](https://github.com/piotr-machura/personal-server/) repository. Edit the `DOMAIN` variable and use `chmod + x
./admin.sh` followed by `./admin.sh -h` to view all the available options.

To make sure our host machine is ready for launch run `./admin.sh -i`. It will check if Docker, docker-compose and other
required tools are available and download them as necessary, as well as launch Certbot and obtain certificates all SSL
certificates if they are not already present. Follow the steps when prompted by Certbot and agree to modifying the
configuration to create redirects from HTTP to HTTPS in all of the `./config/nginx/*.conf` files we have created.

After it is done visit example.com in your browser. You should be greeted by a default nginx
welcome screen and a green padlock on the URL bar signifying encrypted connection. Add a basic
`./data/nginx/default/index.html` to verify that static content from said directory is hosted properly.

## Mail server administration
The docker-mailserver container comes with it's own script for creating and managing user accounts, aliases and many
other functionalities. This script is downloaded and wrapped by `./admin.sh` with the `-m` flag.

Create a user with `./admin.sh -m email add username@example.com` and provide a password when prompted. Once a user has
been created we can generate the DNS text records used to prevent spoofing our email address. Use `./admin.sh -mk` and
add the contents in appropriate records in your DNS provider's interface. The format is `<host name> IN TXT <contents>`,
note that the SPF record has an empty host name.

After you modify your DNS records you can use a tool like [AppmailDev](https://appmaildev.com/)'s DKIM test to verify
that the messages are signed correctly. Simply navigate to example.com/mail in your browser, log into your newly
created user account and compose a message.

## CardDAV administration
Users can be added and removed from the Radicale server with `./admin.sh -da` and `./admin.sh -dd` respectively. List
them with `./admin.sh -dl`.

Once you have created some users navigate to dav.example.com in your browser and log in to see the available
collections. Create a new address book using Radicale's web interface.

In order to sync the contacts with the Roundcube client log into your email account under example.com/mail and navigate
to *"Settings/Proferences/CardDAV*. Use your CardDAV username and password and dav.example.com as the server's address.
Hit *"Save"* and the address book should appear in *"Contacts"*. Add contacts to your heart's content.

## Final notes
The `./admin.sh` script allows for easy maintenance of the running services Use `./admin.sh -h` and `./admin.sh -m help`
to get information on the available functionality.

The project has resulted in a successful creation of a personal server, hosting a static website, email client and an
email server. There are some improvements which could be made to the project, some of which include:

   - using a MySQL database instead of SQLite;
   - adding two-factor authentication plugin to Roundcube;
   - providing a fully-fledged cloud storage solution with NextCloud.

**Author:** Piotr Machura.

Source code: [https://github.com/piotr-machura/personal-server](https://github.com/piotr-machura/personal-server).

Documentation source: [https://github.com/piotr-machura/website/blob/master/src/personal-server.md](https://github.com/piotr-machura/website/blob/master/src/personal-server.md).

Created as a project for the "Computer Networks" class under the supervision of dr. Łukasz
Graczykowski during the academic year 2020/21.
