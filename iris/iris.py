import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk as gdk
from gi.repository import GLib
from os.path import normpath, join, abspath, dirname, isfile
from os import getcwd, sep, pardir, getpid, unlink
from .AppBrowser import AppBrowser
from .settingsBrowser import SettingsHandlers, Settings
from .downloadsBrowser import DownloadHandlers, Downloads
import time
import sys
import inspect

# Message bus stuff
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

# Mailto url parsing stuffs
try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
     from urlparse import urlparse, parse_qs

# So we don't run multiples
pid = str(getpid())
pidfile = "/tmp/iris_messenger.pid"

# Files for the UI
WHERE_AM_I = abspath(dirname(__file__))
STATIC_DIR = join(WHERE_AM_I, 'static') #join(normpath(WHERE_AM_I + sep + pardir), 'static')


class Handlers:
    def __init__(self, app):
        self.main = MainHandlers(app)
        self.settings = SettingsHandlers(app)
        self.download = DownloadHandlers(app)

    def get_all_handlers(self):
        handlers = {}
        for c in [self.main, self.settings, self.download]:
            methods = inspect.getmembers(c, predicate=inspect.ismethod)
            handlers.update(methods)
        return handlers


class MainHandlers:

    def __init__(self, app):
        self.app = app

    def onDeleteEvent(self, *args):
        Gtk.main_quit(*args)

    def gmailClicked(self, *args):
        self.app.load_uri("http://mail.google.com")

    def driveClicked(self, *args):
        self.app.load_uri("http://drive.google.com")

    def calendarClicked(self, *args):
        self.app.load_uri("http://calendar.google.com")

    def settingsClicked(self, *args):
        self.app.load_page(self.app.settings)

    def downloadsClicked(self, *args):
        self.app.load_page(self.app.downloads)


class MaillService(dbus.service.Object):
    def __init__(self, app):
        bus_name = dbus.service.BusName('org.iris.messenger',
                                        bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name,
                                    '/org/iris/messenger')
        self.app = app

    @dbus.service.method('org.iris.messenger')
    def mailto(self, mailto_url):
        self.app.window.maximize()
        self.app.load_uri(mailto_url, mailto=True)

    @dbus.service.method('org.iris.messenger')
    def send_error(self):
        self.app.window.maximize()
        dialog = ErrorWindow(self.app.window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            pass
        dialog.destroy()


class ErrorWindow(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "My Dialog", parent, 0,
            (Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_default_size(150, 100)
        self.set_decorated(False)
        message = """
Iris messenger is already running\n
You can only run one window of Iris at any one time.
"""
        label = Gtk.Label(message)
        box = self.get_content_area()
        box.add(label)
        self.show_all()


class MainWindow(object):

    def __init__(self, mailto=None):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(join(STATIC_DIR, 'gui3.glade'))

        # Get objects
        self.go = self.builder.get_object
        self.window = self.go('window1')
        self.web_container = self.go('scrolledwindow1')
        self.page_container = self.web_container.get_parent()
        self.menu = self.page_container.get_children()[0]

        # On destroy events
        self.window.connect("destroy", self.quit)
        self.window.connect("delete_event", self.quit)

        # Window size + dimensions
        self.window.maximize()

        # Get settings window
        self.settingsManager = Settings(self.go)
        self.settings = self.settingsManager.get_window()

        # Get downloads window
        self.downloadsManager = Downloads(self.go)
        self.downloads = self.downloadsManager.get_window()

        # Create WebView
        self.webview = AppBrowser(self, mailto)
        self.web_container.add_with_viewport(self.webview)

        # Connect signals
        self.builder.connect_signals(Handlers(self).get_all_handlers())

        # Key shortcut handlers
        self.window.connect("key-press-event", self.on_key_pressed)

        # Page loading handler
        GLib.timeout_add(1000, self.loading)
        # Page loading spinner
        self.spinner = self.go('spinner')

        # Mailto message invocation handling
        DBusGMainLoop(set_as_default=True)
        myservice = MaillService(self)

        # Show it all
        self.window.show_all()

    def loading(self):
        # load icon
        if self.webview.is_loading():
            self.spinner.start()
        else:
            self.spinner.stop()
        return 1

    def on_key_pressed(self, widget, event):
        keyval = event.keyval
        keyval_name = gdk.keyval_name(keyval)
        state = event.state

        ctrl = (state & gdk.ModifierType.CONTROL_MASK)

        if ctrl and keyval_name == 'm':
            self.load_page(self.web_container)
            self.webview.load_mail_client()
        elif ctrl and keyval_name == 'd':
            self.load_page(self.web_container)
            self.load_uri("http://drive.google.com")
        elif ctrl and keyval_name == 'c':
            self.load_page(self.web_container)
            self.load_uri("http://calendar.google.com")
        elif ctrl and keyval_name == 'D':
            self.load_page(self.downloads)
        elif ctrl and keyval_name == 'S':
            self.load_page(self.settings)
        elif ctrl and keyval_name == 'BackSpace':
            self.load_page(self.web_container)
        else:
            return False
        return True

    def load_page(self, new):
        children = self.page_container.get_children()
        for c in children:
            if not c == self.menu and not c == new:
                self.page_container.remove(c)
                self.page_container.add(new)

    def add_widget(self, old, new):
        parent = old.get_parent()
        parent.remove(old)
        parent.add(new)

    def load_uri(self, uri, mailto=False):
        """
        Load an URI on the browser.
        """
        for c in self.page_container.get_children():
            if not c == self.menu and not c == self.web_container:
                self.load_page(self.web_container)

        if mailto:
            self.webview.load_mailto_url(uri)
        else:
            self.webview.load_uri(uri)

    def quit(self, win, obj):
        Gtk.main_quit()
        unlink(pidfile)
        sys.exit()


def run(mailto=None):
    # Write the pid file
    file(pidfile, 'w').write(pid)
    gui = MainWindow(mailto) if not mailto is None else MainWindow()
    Gtk.main()


def send_mailto_command(url):
    bus = dbus.SessionBus()
    iris_service = bus.get_object('org.iris.messenger',
                                '/org/iris/messenger')
    mailto = iris_service.get_dbus_method('mailto',
                                          'org.iris.messenger')
    mailto(url)
    sys.exit()


def check_another_instance():
    return True if isfile(pidfile) else False


def notify_and_exit():
    bus = dbus.SessionBus()
    iris_service = bus.get_object('org.iris.messenger',
                                '/org/iris/messenger')
    error = iris_service.get_dbus_method('send_error',
                                         'org.iris.messenger')
    error()
    sys.exit()


def main():

    try:
        sys.argv[1]
    except IndexError:

        if check_another_instance():
            notify_and_exit()
        else:
            run()

    else:

        parsed = urlparse(sys.argv[1])
        mail_addr = parsed.path
        fields = parse_qs(parsed.query)

        url = "to={0}".format(mail_addr)
        url += "&subject={}".format("".join(fields['subject'])) \
                if 'subject' in fields else ''

        url += "&body={}".format("".join(fields['body'])) \
                if 'body' in fields else ''

        url += "&bcc={}".format(",".join(fields['bcc'])) \
                if 'bcc' in fields else ''

        url += "&cc={}".format(",".join(fields['cc'])) if 'cc' in fields else ''

        if check_another_instance():
            send_mailto_command(url)
        else:
            run(url)
