#!/usr/bin/env python3

import psycopg2
import logging
import requests
import pyroute2 as pr
import yaml
import sys
import os

from colorama import Fore, Style, init
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QWidget, qApp

class DatabaseMonitor:
    FILE_CONFIG = 'config.yml'

    def create_connection_with_database(self, logger):
        section = self.parser_settings('support')
        con = None
        try:
            con = psycopg2.connect(host=section['host'], database=section['database'],
                                   user=section['user'], password=section['passwd'],
                                   port=section['port'], connect_timeout=3)
            cur = con.cursor()
            cur.execute('SELECT 1')
        except psycopg2.OperationalError as e:
            self.generate_log(logger, 'error', 'Database Offline!', e)
            return False
        else:
            self.generate_log(logger, 'info', 'Database Online!')
            return True
        finally:
            if(con):
                cur.close();
                con.close();

    def check_network_status(self, logger):
        section = self.parser_settings('site')
        try:
            requests.get(section)
            return True
        except requests.ConnectionError as e:
            self.generate_log(logger, 'error', 'No Internet', e)
            return False

    def check_vpn_status(self, logger):
        ipr = pr.IPRoute()
        section = self.parser_settings('vpn')

        for route in section['routes']:
            value = ipr.route('show', dst=route)
            ipr.close()
            if len(value) > 0:
                return True
            else:
                self.generate_log(logger, 'error', 'VPN Offline!')
                return False

    def logger_settings(self):
        section = self.parser_settings('log')
        logger = logging.getLogger(__name__)
        formatter = logging.Formatter(self.stylize_message_level_name())
        file_handler = logging.FileHandler(section['file_name'])
        stream_handler = logging.StreamHandler()

        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        return logger

    def parser_settings(self, section):
        sections = {}
        current_dir = os.getcwd()
        file_config = f"{current_dir}/{self.FILE_CONFIG}"
        try:
            with open(file_config, 'r') as ymlfile:
                config = yaml.safe_load(ymlfile)
            ymlfile.close()
            sections = config[section]
        except KeyError:
            print(f"{section}'s is unknown.")

        return sections

    def generate_log(self, logger, level, message, details=None):
        if level == 'info':
            logger.setLevel(logging.INFO)
            logger.info(self.stylize_message(message, level))
        elif level == 'error':
            logger.setLevel(logging.ERROR)
            logger.error(self.stylize_message(message, level))
            if details is not None:
                logger.error(details)

    def stylize_message(self, message, level):
        return Style.BRIGHT + \
               f"{Fore.GREEN if level == 'info' else Fore.RED}" + f"{message}"

    def stylize_message_level_name(self):
        return Style.BRIGHT + Fore.WHITE + "[" + \
               '%(levelname)s' + Fore.WHITE + "] " + \
               '%(asctime)s: %(message)s'


class SystemTrayIcon(QSystemTrayIcon, DatabaseMonitor):
    def __init__(self, icon, logger, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        DatabaseMonitor.__init__(self)
        menu = QMenu(parent)
        menu.setStyleSheet("* { background-color: black; color: #FFFFFF; } QMenu::item::selected {background-color: blue;}");
        self.menu_settings(menu)
        self.logger = logger
        self.update_icon()

    def get_configs(self, key):
        return self.parser_settings(key)

    def open_file(self):
        return os.system(f'{self.get_configs("default_editor")} {self.get_configs("log")["file_name"]}')

    def tail_log(self):
        return os.system(f"gnome-terminal -e 'bash -c \"tail -f {self.get_configs('log')['file_name']};bash\"'")

    def menu_settings(self, menu):
        tail_log_action = menu.addAction("Tail logs")
        log_file_action = menu.addAction('Show logs')
        change_icon_action = menu.addAction('Update')
        exit_action = menu.addAction('Exit')
        self.setContextMenu(menu)
        tail_log_action.triggered.connect(self.tail_log)
        log_file_action.triggered.connect(self.open_file)
        change_icon_action.triggered.connect(self.update_icon)
        exit_action.triggered.connect(qApp.quit)

    def update_icon(self):
        try:
            timer = QTimer()
            timer.timeout.connect(self.update_icon)
            timer.start(60000)
            tray_section = self.get_configs('tray')

            if not self.check_network_status(self.logger):
                icon = tray_section['network']
            elif not self.check_vpn_status(self.logger):
                icon = tray_section['alert']
            elif not self.create_connection_with_database(self.logger):
                icon = tray_section['offline']
            else:
                icon = tray_section['online']

            self.setIcon(QIcon(icon))

        finally:
            QTimer.singleShot(60000, self.update_icon)


def main():
    # Colorama module's initialization.
    init(autoreset=True)

    db = DatabaseMonitor()
    section = db.parser_settings('tray')
    app = QApplication(sys.argv)
    w = QWidget()

    tray_icon = SystemTrayIcon(QIcon(section['offline']), db.logger_settings(), w)

    tray_icon.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
