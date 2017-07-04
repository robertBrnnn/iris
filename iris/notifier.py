import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify, GdkPixbuf
from os.path import normpath, join, abspath, dirname
from os import getcwd, sep, pardir

WHERE_AM_I = abspath(dirname(__file__))
STATIC_DIR = join(WHERE_AM_I, 'static')

class Notifier:
    def __init__(self):
        Notify.init("Iris")
        self.app_icon = join(STATIC_DIR, 'iris.ico')

    def create_notification(self, summary, message):
        notification = Notify.Notification.new(summary, message)
        image = GdkPixbuf.Pixbuf.new_from_file(self.app_icon)
        notification.set_icon_from_pixbuf(image)
        notification.set_image_from_pixbuf(image)
        notification.show()
