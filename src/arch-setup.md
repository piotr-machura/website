---
toc: true
---
# Arch Linux setup
![Arch Linux logo](./img/arch.png)

Setting up Arch Linux is not exactly difficult, but tedious none the less. And the more you customize it the more steps
there are to remember, so after two Virtual Box and one bare-metal installations I have decided to leave myself a rope
in the form of this very guide, documenting a full installation and setup of my machine, should I ever need to reproduce
it in its entirety. And i **really** mean entirety, down to every currently installed program.

***
## Installation

In order to customize Arch we first need to install it. Duh.

Mandatory warning to always consult the [wiki](https://wiki.archlinux.org/index.php/installation_guide) when in doubt.

### Obtaining and booting the live environment
First we will get the ISO, which is a pre-baked system that will live on our USB drive and contain all the tools we will
need to install Arch on our machine. Steps described here are actually universal for any operating system, not just
Arch.

1. Download the latest Arch Linux ISO from the official [sources](https://www.archlinux.org/download/).
2. [Burn it](https://www.just-google.it/?s=burn%20iso%20to%20usb) to a USB drive.
3. Ensure the boot order is correct (USB before internal hard drive). This should be listed somewhere in the UEFI/BIOS
   of your system.
4. Stick the USB drive into the USB port and boot the machine.
5. Select *"Boot Arch Linux"* when the ISO menu shows up.

### Verify the boot mode
There are two common ways a computer can boot: the new EFI mode or the old-school BIOS mode.
To find out which one you booted in run `ls /sys/firmware/efi/efivars`.  If it lists without an error you have booted
in EFI mode and are good to go. If the directory doesn't exist you have booted in a legacy BIOS/CSM mode. Unfortunately
the only advice I can give you is to consult the motherboard's manual in order to reboot in EFI mode. On the upside this
should not be a problem with modern hardware, and by modern I mean from around 2010 onwards.

The reason we want to work in EFI is **systemd-boot**, which is a dead simple and very fast boot loader, which comes
preloaded with systemd, which in turn is included with every Arch Linux installation.

### Establish an internet connection
The installation requires a working internet connection in order to pull all the latest packages from Arch repos.
Ethernet works out of the box, but wifi requires some additional steps.

1. Open the interactive prompt `iwctl`.
2. List devices `device list`.
3. Scan for networks `station <device name here> get-networks`.
4. Connect `station --passphrase <passphrase here> <device name here> connect <SSID of network here>`.

At any moment you can easily verify the connection with `ping google.com -c 5`.

### Partition the disks
This is usually the *"hardest"* part, as in the one that actually varies from installation to installation. Brace
yourself.

Partitioning a drive means dividing it into usable chunks (called partitions), which are then made available to the
system. The important thing is that space that isn't partitioned is considered empty and no files can be stored there.
For example the simplest way would be to just make one big partition the size of the entire drive and call it a day.
This won't work for us though, since we want to use systemd-boot as our boot loader. Therefore we will make two
partitions - one for it (the ***EFI*** partition) and one for the actual system (the ***file system*** partition).

There are two ways a drive can store information about the way it has been partitioned: the new GUID Partition Table
(GPT) designed to work with EFI and the old Master Boot Record (MBR) from the BIOS days. If you have booted in EFI mode
the tool we use should automatically create GPT partitions, so no need to worry about that choice.

**Note:** I make the assumption here that you have only one drive to work with. If you have multiple it is a good idea
to use a smaller one for the steps described here and a big one for a ***home*** partition, one where all the users'
personal files will live. It should be of type *"Linux file system"*, and feel free to use the entire drive for it.

1. List available drives `lsblk`. Remember the `<disk name>` of the disk you wish to use.
2. Run `cfdisk`. An ncurses interface showing the `<disk name>` and available free space should appear.
3. `[New]` should be highlighted. Use 550MB for the __EFI partition__.
4. Select `[Type]` and find `EFI System`. Move down to `Free Space`.
5. Select `[New]` and use the leftover space to create a __file system partition__. Its type should be *"Linux
   file system"* by default.
6. The partitions are ready. Select `[Write]` and confirm.
7. Check the partitions with `lsblk`. The partitions should be visible under the `<drive name>`. Remember which one's
   which.

### Format the partitions
The drive now contains the partition table (the *information* on how it is partitioned), next thing to do is format it
the way we claimed they would be when we were using cfdisk.

1. Format the __EFI partition__ `mkfs.fat -F32 /dev/<EFI partition name here>`.
2. Format the __file system partition__ `mkfs.ext4 /dev/<filesystem partition name here>`.
3. Mount the __file system partition__ `mount /dev/<filesystem partition name here> /mnt`.
4. Create boot directory `mkdir /mnt/boot` and mount the __EFI partition__ `mount /dev/<EFI partition name here> /mnt/boot`.

**Note:** if you have created a home partition format it as ext4, create the home directory `/mnt/home` and mount it
there the same way you did with EFI partition.

### Install the new system
We are finally here. The partitions are formatted ready for installation, time to pull the packages we need from the
Arch repositories and actually install Linux on the machine.

1. Check the mirror connection speed `pacman -Syyyy`.
    - If the mirrors are slow edit the mirror list `vim /etc/pacman.d/mirrorlist`.
2. Install base system and a few necessary tools `pacstrap /mnt base base-devel linux linux-firmware neovim git`.
3. Generate the partition table `genfstab -U /mnt >> /mnt/etc/fstab`.

The last step generated the *virtual* partition table for the Unix directory structure. The drive "knows" how it is
partitioned without it, but this allows Linux to have a single file system root and mount drives as if they were
directories on boot.

***

Now we will perform what is called a ***chroot***. It is a procedure that allows us to **ch**ange the **root** folder of
our current session, essentially transporting us from the system living on a USB stick to the one we just `pacstrap`ped
on the actual drive. We do this by using

`arch-chroot /mnt`.

You should notice the prompt changing from the customized, colorful one put in place by Arch ISO creators to the boring
white one default in bash. Now that we are here time to do some housekeeping before the system is usable and ready to reboot.

### Timezone and locale
This is pretty self-explanatory. Feel free to change the timezone and the locales to whatever your heart desires.

1. Set the timezone `ln -sf /usr/share/zoneinfo/Poland /etc/localtime`.
2. Generate the clock `hwclock --systohc`.
3. Uncomment the lines
```none
/etc/locale.gen
---------------

pl_PL.UTF-8 UTF-8
en_US.UTF-8 UTF-8
en_GB.UTF-8 UTF-8
```
Save and run `locale-gen`. Next set the locale `localectl set-locale LANG=en_US.UTF-8`.  Set the global key map
`localect set-keymap pl`.

### Create the swap file
The swap file is just a hunk of space on the drive that the system will use after it has run out of RAM. It's a good
idea to have one and to make it at least as big as your system memory because the machine dumps its RAM to the swap
when it hibernates.

1. Copy the file `dd if=/dev/zero of=/swapfile bs=1M count=<size in MB, eg. the amount of RAM>`.
2. Change its permissions `chmod 600 /swapfile`.
3. Make it a swap file `mkswap /swapfile` and activate it `swapon /swapfile`.
4. Add it to file system table by editing
```none
/etc/fstab
----------

# <file system>  <mount point>     <type>    <options>    <dump>    <pass>
...
/swapfile        none              swap      defaults     0         0
```
Make sure to align the swap file entries with the main file system partition entries.

### Host and users
We need a name for our machine, and we need to set up the localhost IP addresses. Many programs (like Syncthing, for
example) rely on the localhost pointing to the machine itself.

1. Change the host name `nvim /etc/hostname`. Type the chosen `<hostname>`, save and quit.
2. Change the default hosts by editing
```none
/etc/hosts
----------

127.0.0.1	localhost
::1		localhost
127.0.1.1	<hostname here>.localdomain	<hostname here>
```
Any Linux user will tell you that it's a very bad idea to be root (system administrator) all the time. We will create a
regular user for the everyday operations and allow him to perform root-only actions with sudo.

3. Change the root password `passwd`.
4. Add the user with `useradd -m <username here>`. Set the password `passwd <username here>`.
5. Add the user to the wheel group `usermod -aG wheel,audio,video,optical,storage <username here>`.
Use `groups <username here>` to list all groups of a user.
6. Edit the sudoers file
```none
EDITOR=nvim visudo
------------------

## Uncomment to allow members of group wheel to execute any command
%wheel ALL=(ALL) ALL
...
Defaults env_keep += "HOME"
```
The last line allows us to keep our `$HOME` variable around when using sudo, as it would normally change from
`/home/<username>` to `/root`. This is important for some of the pacman hooks present in the configuration files.

### Internet and pacman
The Internet connection is working *for now*, since we have established it back in the ISO. We need something to manage
connections on the machine itself. That something is a program called NetworkManager. Install it with `pacman -S networkmanager`.

If you are using Ethernet `systemctl enable --now NetworkManager` should be sufficient. If you are using wifi you have to
do some additional setup.

1. Check if the wifi radio is enabled `nmcli radio wifi`. If not, enable it with `nmcli radio wifi on`.
2. Run `nmcli d wifi list` to list available wifi networks.
3. Run `nmcli d wifi connect <network name here> password '<your password here>'`.

Next we will enable the multilib repository and pretty colors in pacman by editing
```none
/etc/pacman.conf
----------------
...
Color
...
[multilib]
Include = /etc/pacman.d/mirrorlist
```
After we're done it's time to re-sync with mirrors with `pacman -Syyyy`.

### Hardware drivers and boot loader
We need some special packages to take full advantage of our hardware, mainly the [processor
microcode](https://wiki.archlinux.org/index.php/Microcode#Installation) and the [video
drivers](https://wiki.archlinux.org/index.php/Xorg#Driver_installation). Take a look at the Arch Wiki and figure out
what you need.

Next is the boot loader. It is a piece of software that starts the system after the computer turns on, and we'll be
using **systemd-boot**, which comes bundled with the base installation.

First, we enable it with `bootctl install`. Then we need to edit the loader config file, which, among other things,
tells the boot loader to start our Arch Linux after the computer turns on.
```none
/boot/loader/loader.conf
------------------------

default 	arch.conf
editor 		no
console-mode 	max
```
**Note:** use tabs for alignment. Ensure that this is the case by doing `:set list noexpandtab` in Neovim. 

Next we'll need to edit the arch loader config, which tell the boot loader what to actually load when starting Arch.
```none
/boot/loader/entries/arch.conf
------------------------------

title		Arch Linux
linux 		/vmlinuz-linux
initrd 		/initramfs-linux.img
initrd 		/<cpu vendor name in lowercase here>-ucode.img
options		root=/dev/<root partition name here>
```

### Rebooting
We are done configuring the system. Arch is now *technically* installed and ready to use. In order to proceed we will
exit the chroot with `exit` and shutdown the computer with `systemctl poweroff`.

Next, we unplug the ISO from our USB port and power the machine on. The standard TTY screen should appear and we can log
in as the user we have created.

***

## Customization
Congratulations, the system is installed. But, as you may have noticed, it lacks some quality of life features like, oh
I don't know, a graphical interface. Time to take care of that.

### Installing paru
1. Clone the [paru](https://github.com/Morganamilo/paru) AUR helper PKGBUILD `git clone https://aur.archlinux.org/paru-bin.git`.
2. cd into the `paru-bin` and run `makepkg -si`.
3. Verify installation `paru -Syyyy`.

***

### Cloning the repository
In order to fully clone the directory on a freshly installed system perform the following steps:

1. Create an alias `alias dots="/usr/bin/git --git-dir=$HOME/.conifg/dots --work-tree=$HOME"`
2. Clone the repo `git clone --bare https://github.com/piotr-machura/arch-setup.git $HOME/.config/dots`
3. Disable the showing of untracked files `dots config --local status.showUntrackedFiles no`
4. Apply the configs `dots reset --hard`

__Warning:__ Some config files require additional steps in order to take effect.

__Note:__ Copy the `git dots` alias described [
here](https://github.com/piotr-machura/arch-setup/wiki/Customization#git-and-github)
for easy access to the repository.
