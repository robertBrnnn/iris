from os.path import normpath, join, abspath, dirname, expanduser, exists, isfile
from os import getcwd, sep, pardir, makedirs
from gi.repository import GLib
import configparser


DATA_DIR = join(expanduser("~"), '.iris')
CONFIG = join(DATA_DIR, 'iris.ini')

iris_ini = """
[SETTINGS]
downloadlocation = {}
opendownload = True
usegmail = False

"""


class Config:

    def __init__(self):
        self.first_run()
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG)

    def get(self, section, var, boolean = False):
        if not boolean:
            return self.config.get(section, var)
        else:
            return self.config.getboolean(section, var)

    def set(self, section, var, value):
        self.config.set(section, var, value)
        self._update_config()

    def first_run(self):
        if not exists(DATA_DIR):
            makedirs(DATA_DIR)

        if not isfile(CONFIG):
            with open(CONFIG, 'a+') as f:
                f.write(iris_ini.format(
                GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD)
                ))

    def _update_config(self):
        with open(CONFIG, 'w') as configfile:
            self.config.write(configfile)
