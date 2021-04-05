# Personal server

![Docker logo](img/docker_logo.png)


The goal of this project is to create a personal server that will host a static website, fully capable email stack and a
webmail client. Docker makes the process of configuration and deployment faster and tidier, allowing us to construct the
server from *almost* ready-to-go parts. It also makes the installation pretty much host-independent, as in the host's
operating system does not matter as long as docker engine and docker-compose are available.

We will use the following open source software to create our server:

- **Web server:** [nginx](https://nginx.org/), modified to include [certbot](https://certbot.eff.org) for ease of
   obtaining and renewing LetsEncrypt SSL certificates. 
- **Email stack:** [docker-mailserver](https://docker-mailserver.github.io/docker-mailserver/v9.1/), configured to maximize
   the probability of not landing in Gmails spam folder.
- **Webmail client:** [Roundcube](https://roundcube.net/) with [context
   menu](https://github.com/JohnDoh/roundcube-contextmenu), [persistent
   login](https://github.com/mfreiholz/persistent_login) and [CardDAV](https://github.com/mstilkerich/rcmcarddav) plugins.
- **CardDAV server:** [Radicale](https://radicale.org/3.0.html), used to sync Roundcube contacts with e.g.  an
   Android phone.

A simplified schema of the server is portrayed below, keep in mind all of the software will be running in their own
respective Docker conatiners.

![Simplified server diagram](img/server_diagram.svg)

# Containers

A container is a process that has been separated from the rest of the system. Said separation is usually
achieved using the OS-level virtualization capabilities of the Linux kernel, in particular the [kernel
namespaces](https://en.wikipedia.org/wiki/Linux_namespaces) and [cgroups](https://en.wikipedia.org/wiki/Cgroups).
Containerization is akin to the unix **chroot**, since the contained process uses host's kernel and as such does not
require a supervisor, thus incurring much lesser performance penalty than a traditional virtual machine.

A container bundles all of the basic utilities required for system operation (a posix-compatible shell, GNU or BusyBox
coreutils etc.), all the dependencies required by the containerized application, the application itself **and nothing
more**. From the point of view of the contained process the container is just a barren computer, created with the
specific goal of running said application.

Communication with the host, other containers, or the Internet, is usually achieved through networking.  The containers
are usually connected in a local network managed by the containerization software (in case of Docker the docker-daemon),
allowing for local communication using their **exposed** ports, and can bind to host's ports by **publishing** them,
essentially making them their own.

A process run from within a container does not have access to host's file system or any other processes unless
directly specified, making the infrastructure more resilient to exploits and application-level vulnerabilities.

## Docker basics
Docker is the most popular containerization framework in the world. It is open source and written in the Go programming
language. It is available on all the major platforms, but targets Linux as production environment. Once installed it
allows running, inspecting, and stopping containers with a single command.

The Docker, Inc. company provides professional support for enterprises utilizing Docker, and hosts a
[repository](https://hub.docker.com/) of ready-to-use, open source images for popular services such as nginx, mySQL and
many others. The containers are automatically downloaded and started when the `docker run` command is issued.
Users are welcome to contribute by uploading their own images or extending existing ones.

### Images and containers
A container image is a blueprint of the application's environment. It specifies the structure of the file system,
installed software, external dependencies and all other **static** components of a container. The process of creating an
image is specified in a **Dockerfile** and initiated with `docker build`, similarly to compiling a C project with
Makefile and `make`.

Once an image is built it is possible to create multiple different containers based on it, or even publish it to a
remote repository, eg. the first-party [DockerHub](https://hub.docker.com/). An image can be **pulled** from remote
location with `docker pull`, which also happens automatically when `docker run` is executed specifying an image not
found locally

A specific container is created and started with `docker run`. It is usually identified by a **name**, either given by
the user or assigned randomly by Docker. At any point it is possible to `docker exec` a command inside of any running
container, eg. launching an interactive shell session.

### Volumes
The docker-daemon manages the process of starting, stopping and removing docker containers. Every time the container is
started a file system **volume** is created , which persists the container stopping (which is akin to turning off the
machine), but their availability is not guaranteed after container removal and the location is implementation-specific.

In order to persist container data **bound volumes** must be specified in the `docker run` command. Binding a volume
boils down to specifying a host's directory where the container's directory should be mounted, similarly to mounting eg.
a USB drive in the Linux file system. Files in the volume can be accessed by the host like any other files, which allows
for injecting configuration, creating backups, pushing static content etc.

Since the location of the bound directory in the host's file system  is for the end-user to choose, this allow for
bundling data for multiple user applications in one directory, instead of having them scattered around the file system.
This enables less complex backups and easy version control of the containerized applications' configuration files.

### Networking
Networking is the preferred way for containers to communicate with each other and with other machines. An image can
**expose** a port, allowing other network entities access to  eg. a web service hosted there. When a container is
created based on such image the user can choose to **publish** said port, binding it to a host's port of their choice.
The service will then be available to the local network or the Internet just like any other network application run on
the host.

It is worth mentioning that publishing a port is established directly on the level of Linux's iptables, bypassing the
more user-friendly iptables wrappers such as ufw and firewall-cmd. It is nevertheless recommended to allow traffic
through a port in such wrapper, as not doing so has been reported to cause issues.

When multiple containers run on the same machine it is possible to connect them into a local network, managed by the
docker daemon. Each container is assigned an Ipv4 address, allowing for communication. Docker also creates a **name
server**, which resolves containers' names to their IP addresses. One can, for example, ping container named
`name1` from container `name2` simply with `ping name1` (if the two reside in the same docker network). This mechanizm
is useful for creating a **reverse proxy** that is also a container in of itself.

## docker-compose
The `docker run` command usually requires a lot of arguments (name, bound volumes, networks, published ports, environment
variables etc.). It also assumes some components to already be in place (eg. the used networks). This can make the
process of deploying multiple dependent containers cumbersome, requiring multiple multi-line commands executed in the
correct order.

A tool which solves the above problems is called **docker-compose**. It is a single binary file which upon execution
looks for a docker-compose.yml file in the current directory or any of its parents. The YML file specifies the containers,
networks, volumes and everything else needed to orchestrate the deployment of a multi-container setup. This makes
reproducing a complex set of interconnected web services as simple as pulling the docker-compose.yml file (eg. from a
GitHub repository) and issuing the command `docker-compose up -d`.

# Setting up the server
The following notation will be used:

- X.X.X.X will denote the static host **IPv4 address**.
- example.com will denote the **base domain** purchased at the registrar.
- ./ will denote the root of the project (ie. the directory containing docker-compose.yml).

The source code required for the implementation is available in the associated [GitHub
repository](https://github.com/piotr-machura/personal-server/).

### Project structure
The project structure is as follows:
```none
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
├─ admin.sh
└─ init.sh
```

The `./config` directory contains persistent config of containerized applications, `./build` will contain build
resources for customized containers and the `./data` directory will be populated with docker volumes specific to the
current installation (user data, certificates, website files etc.). The first two can be version controlled (eg. with
Git), and `./data` can be easily backed up (eg. using rsync).

The `./init.sh` shell script is used to install all of the required tools (Docker, docker-compose, mail server setup
script), whereas `./admin.sh` enables easy administration of the server (adding users, obtaining SSL certificates etc.).

### DNS records

We will set the following dns records (arrow meaning "pointing to"):

| **A** | **CNAME** | **MX** | **TXT** |
| --- | --- | --- | --- |
| example.com → X.X.X.X | dav.example.com → example.com | *empty* → mail.example.com | DKIM |
| www.example.com → X.X.X.X | | | DMARC |
| mail.example.com → X.X.X.X | | | SPF|

The above mentioned TXT records ensure no email spoofing has taken place and greatly increase the probability of our
messages not being flagged as spam. They require the server to be already running and are discussed in more detail in
[Mail server#Best practices](#).

### Skeleton docker-compose.yml
Create a skeleton of docker-compose.yml file is as follows:
```yaml
version: '3'
services:
  <service sections will go here>
```

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

### Creating the image

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
Configuration files for the nginx web server will be automatically sourced from `./config/nginx`. To host the static content stored in
`./data/nginx/default` on the website root create a basic configuration file in `./config/nginx/default.conf`.
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
certificates, as those will be automatically added by Certbot.

### The nginx docker-compose section
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
corresponding host's ports and the container will restart if nginx crashes.. The `default.conf` we have just written
(and any other file in `./config/nginx` will be automatically sourced thanks to an 'include' directive in the default
nginx config.

Note that while the static website data is bound as read only, the configuration and certificate volumes are not. This
is because they will be modified by Certbot when the certificates are obtained.
