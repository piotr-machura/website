# Personal server

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

## Reverse proxy
All of our services (with email being the only exception) will be served through an instance of the nginx web server
acting as a **reverse proxy**. This ensures that all connections with the outside world are utilizing HTTPS protocol
and, as a consequence, SSL encryption.
