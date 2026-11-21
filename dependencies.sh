#!/usr/bin/env bash
set -euo pipefail
if [[ $EUID == 0 ]]; then
  echo 'Executa como utilizador normal; sudo será usado apenas para os pacotes.' >&2
  exit 1
fi
sudo apt-get update
sudo apt-get install -y python3 python3-gi gir1.2-glib-2.0 dconf-cli libglib2.0-bin \
  gnome-shell gnome-shell-common gnome-shell-extension-prefs gnome-tweaks \
  gnome-terminal nautilus gnome-software gir1.2-gtk-3.0 gir1.2-gtk-4.0 \
  gir1.2-adw-1 gir1.2-gdesktopenums-3.0 gir1.2-gnomedesktop-4.0 \
  gir1.2-gnomedesktop-3.0 gir1.2-clutter-1.0 gir1.2-gdkpixbuf-2.0 \
  gir1.2-pango-1.0 gir1.2-gmenu-3.0 fontconfig libgtk-3-bin \
  adwaita-icon-theme breeze-icon-theme
