Title:        Arch Linux setup
Description:  BTW I use arch. Did you know that I use arch?
Repository:   https://sr.ht/~piotr-machura/arch-setup/
Date:         2021-02-21

# Arch Linux setup
Setting up Arch Linux is not exactly difficult, but tedious none the less. And the more you customize it the more steps
there are to remember, so after two Virtual Box and one bare-metal installations I have decided to leave myself a rope
in the form of this repository, containing the setup of my machine, should I ever need to reproduce it in its entirety.
And i **really** mean entirety, down to every currently installed program.

## Software

- **Window manager:** [Qtile](http://www.qtile.org/)
- **Terminal:** [Alacritty](https://github.com/alacritty/alacritty)
- **Editor:** [Neovim](https://neovim.io/)
- **File manager:** [Thunar](https://docs.xfce.org/xfce/thunar/start)
- **Browser:** [Firefox](https://www.mozilla.org/en-US/firefox/new/)
- **PDF viewer:** [Zathura](https://pwmt.org/projects/zathura/)
- **Color scheme:** [Nord](https://www.nordtheme.com/)
- **Font:** [Rubik](https://fontlibrary.org/en/font/rubik)
- **Mono space font:** [JetBrains Mono](https://www.jetbrains.com/lp/mono/)

A complete list of all installed software is available under `~/.local/share/pacman/PKGLIST`.

## Screenshots

![Screenshot 1](./img/ss_1.jpg)

![Screenshot 2](./img/ss_2.jpg)

![Screenshot 3](./img/ss_3.jpg)

## Using the repository 
The master branch of the repository directly tracks the changes made to the config files, with the project root in my
home directory. As such I don't want it to contain a README, license and other repo-specific things, so they are kept on
a master branch (which is displayed by default) and actual configuration files can be found on the "dots" branch. 
