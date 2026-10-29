#!/bin/sh
cd "$(dirname "$0")" || exit 1
sh ./install.sh
printf '\nPress Enter to close.\n'
read -r INSTALL_DONE
