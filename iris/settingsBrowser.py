import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from .config import Config


class SettingsHandlers:
    def __init__(self, app):
        self.app = app

    def downloadLocClicked(self, *args):
        dialog = Gtk.FileChooserDialog("Please choose a folder", self.app.go("window1"),
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             "Select", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.app.settingsManager.update_download_location(dialog.get_filename())

        dialog.destroy()

    def openDownloadSwitch(self, *args):
        self.app.settingsManager.update_open_download()

    def gmailButton_toggled(self, *args):
        self.app.settingsManager.toggled(gmail=True)

    def inboxButton_toggled(self, *args):
        self.app.settingsManager.toggled(inbox=True)

    def backClicked(self, *args):
        self.app.load_page(self.app.web_container)

class Settings:

    def __init__(self, get_object):

        self.window = get_object("settingsPage")
        get_object("Setting").remove(self.window)
        self.download_location_label = get_object("downloadLocation")
        self.open_download = get_object("openDownload")
        self.use_inbox = get_object("inboxButton")
        self.use_gmail = get_object("gmailButton")
        self.config = Config()
        self.download_location_label.set_text(self.config.get("SETTINGS", "downloadLocation"))
        self.open_download.set_state(self.config.get("SETTINGS", "opendownload", boolean=True))
        self.use_inbox.set_active(not self.config.get("SETTINGS", "usegmail", boolean=True))
        self.use_gmail.set_active(self.config.get("SETTINGS", "usegmail", boolean=True))

    def get_window(self):
        return self.window

    def update_download_location(self, loc):
        self.download_location_label.set_text(loc)
        self.config.set("SETTINGS", "downloadLocation", loc)

    def update_open_download(self):
        self.config.set("SETTINGS", "opendownload", repr(self.open_download.get_active()))

    def toggled(self, inbox=False, gmail=False):
        if inbox and self.use_inbox.get_active():
            self.use_gmail.set_active(False)
            self.update_default_client(inbox=True)
        elif inbox and not self.use_inbox.get_active():
            self.use_gmail.set_active(True)
            self.update_default_client(gmail=True)

        if gmail and self.use_gmail.get_active():
            self.use_inbox.set_active(False)
            self.update_default_client(gmail=True)
        elif gmail and not self.use_gmail.get_active():
            self.use_inbox.set_active(True)
            self.update_default_client(inbox=True)

    def update_default_client(self, inbox=False, gmail=False):
        if inbox:
            self.config.set("SETTINGS", "usegmail", repr(False))
        if gmail:
            self.config.set("SETTINGS", "usegmail", repr(True))
