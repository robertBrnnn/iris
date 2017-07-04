import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib
from .config import Config
from os.path import join
from .notifier import Notifier
from .openFile import open_file


class DownloadHandlers:
    def __init__(self, app):
        self.app = app

    def downloadBackClicked(self, *args):
        self.app.load_page(self.app.web_container)


class Downloads:
    def __init__(self, get_object):
        self.go = get_object
        self.window = self.go("downloadsPage")
        self.go("Download").remove(self.window)
        self.download_container = self.go("downloads")
        self.downloads = []
        self.config = Config()

        self.notify = Notifier()

        # Initial downloads stuff
        self.liststore = Gtk.ListStore(str, int)
        treeview = Gtk.TreeView(model=self.liststore)

        # First column
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Download", renderer_text, text=0)
        treeview.append_column(column_text)

        # Second column
        renderer_progress = Gtk.CellRendererProgress()
        column_progress = Gtk.TreeViewColumn("Progress", renderer_progress,
                                             value=1, inverted=2)
        treeview.append_column(column_progress)

        self.window.pack_start(treeview, True, True, 0)
        treeview.show()

        GLib.timeout_add(100, self._update_downloads_view)

    def get_window(self):
        return self.window

    def _decide_destination(self, download, suggested_filename):
        dialog = Gtk.FileChooserDialog("Select location to save to",
                                        self.go('window1'),
                                        Gtk.FileChooserAction.SAVE,
                                        (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_SAVE,
                                        Gtk.ResponseType.OK))

        dialog.set_current_folder(
            self.config.get("SETTINGS", "downloadlocation"))
        dialog.set_current_name(suggested_filename)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            download.set_destination(dialog.get_uri())
            self.downloads.append(download)
            self.liststore.append(
                [download.get_destination(),
                download.get_estimated_progress() * 100])
        elif response == Gtk.ResponseType.CANCEL:
            download.cancel()
        dialog.destroy()

    def download_requested(self, context, download):
        download.connect("finished", self._download_finished)
        download.connect("failed", self._download_failed)
        download.connect("received-data", self._received_data)
        download.connect("decide-destination", self._decide_destination)
        return False

    def _received_data(self, download, data):
        """
        print("Download {0}, data {1}".format(download.get_destination(),
                                                data))
        """
        pass

    def _download_finished(self, download):
        dest = download.get_destination()
        summary = "Download complete"
        body = "{0} has finished downloading".format(
                dest[dest.rfind('/'):].replace('/', ''))
        self.notify.create_notification(summary, body)
        self._remove_from_liststore(download)
        self.downloads.remove(download)

        if self.config.get("SETTINGS", "opendownload", boolean=True):
            open_file(dest)

    def _download_failed(self, download, error):
        dest = download.get_destination()
        summary = "Download Failed"
        body = "{0} has failed to download. Error {1}".format(
                dest[dest.rfind('/'):].replace('/', ''),
                error.message)
        self.notify.create_notification(summary, body)
        self._remove_from_liststore(download)
        self.downloads.remove(download)


    def _update_downloads_view(self):
        for download in self.downloads:
            progress = download.get_estimated_progress() * 100
            name = download.get_destination()
            self._update_list_store(name, progress)
        return 1

    def _remove_from_liststore(self, download):
        for v in self.liststore:
            if v[0] == download.get_destination():
                self.liststore.remove(v.iter)

    def _update_list_store(self, name, progress):
        for row in self.liststore:
            if row[0] == name:
                self.liststore.set_value(row.iter, 1, progress)
