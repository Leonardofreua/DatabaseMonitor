#!/usr/bin/env bash

# Init option {{{
Color_off='\033[0m'       # Text Reset

# terminal color template {{{
# Regular Colors
Green='\033[0;32m' # Green
# }}}

SHORTCUT_NAME="DatabaseMonitor.desktop"
EXECUTABLE="DatabaseMonitor.sh"
PROJECT_PATH="/opt/DatabaseMonitor"
APPLICATIONS="${HOME}/.local/share/applications"

msg() {
    printf '%b\n' "$1" >&2
}

success() {
    msg "${Green}[✔]${Color_off} ${1}${2}"
}

chmod +x DatabaseMonitor.py
chmod +x DatabaseMonitor.sh

# ==========================================
#            Python3 Instalation
# ==========================================
if [[ $(python3 -V) != *"3.7"* ]]; then
    sudo apt install software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install python3.7
    success "Installed Python 3.7.3"
else
    success "Python3 already installed"
fi

# ==========================================
#              Pip3 Instalation
# ==========================================
sudo apt install -y python3-pip
success "Installed Pip3"

# ==========================================
#    PostgresSQL and Psycopg2 Instalation
# ==========================================

sudo apt install postgresql
sudo apt install python-psycopg2
sudo apt install libpq-dev
success "Installed PostgreSQL and Psycopg2"

# ==========================================
#          Dependencies Instalation
# ==========================================
sudo pip3 install -r requirements.txt
success "Installed dependencies."

# ==========================================
#      Copy project directory to $HOME
# ==========================================
sudo cp -R $(pwd) $HOME
success "Project copied to $HOME"

# ==========================================
#        Creation of Desktop icon
# ==========================================
cat <<EOF >$APPLICATIONS/$SHORTCUT_NAME
[Desktop Entry]
Version=1.0
Type=Application
Name=DatabaseMonitor
Exec=$PROJECT_PATH/$EXECUTABLE
Path=$PROJECT_PATH
Terminal=false
Categories=Utility;Application;
Icon=/opt/DatabaseMonitor/img/databaseMonitor.png
EOF

chmod +x $APPLICATIONS/$SHORTCUT_NAME
success "The shortcut was created successfully."

