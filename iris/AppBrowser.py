import gi
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2 as webkit
from gi.repository import GLib
import re
import webbrowser
from os.path import normpath, join, abspath, dirname, expanduser, exists
from os import getcwd, sep, pardir, makedirs
from .settings import *
from .config import Config
from .notifier import Notifier


DATA_DIR = join(expanduser("~"), '.iris')
COOKIES = join(DATA_DIR, 'storage.txt')

if not exists(DATA_DIR):
    makedirs(DATA_DIR)

# mailto urls gmail = https://mail.google.com/mail/?view=cm&fs=1&to=someone@example.com&su=SUBJECT&body=BODY&bcc=someone.else@example.com
# inbox = https://inbox.google.com/?view=cm&fs=1&to=someone@example.com&su=SUBJECT&body=BODY&bcc=someone.else@example.com
INITIAL_URL = {'gmail': 'https://mail.google.com',
                'inbox': 'http://inbox.google.com'}

MAILTO_URL = {'gmail': 'https://mail.google.com/mail/?view=cm&fs=1&',
                'inbox': 'https://inbox.google.com/?view=cm&fs=1&'}

google_links_hack = """

//window.addEventListener('click', fn, true);

/*
var images = document.getElementsByTagName("img");
for (var i=0, len=images.length, img; i<len; i++) {
    img = images[i];
    img.addEventListener('click', fn, true);
}*/

/*
document.onreadystatechange = function () {
    if (document.readyState === "complete") {
        window.addEventListener('click', fn, true);

        var images = document.getElementsByTagName("img");
        for (var i=0, len=images.length, img; i<len; i++) {
            img = images[i];
            img.addEventListener('click', fn, true);
        }
    }
}*/

/*
function fn(e) {

    var e = window.e || e;
    var target = e.target || e.srcElement,
        parent = e.target.parentNode;

    if (e.target.tagName !== 'A'){
        e.preventDefault();
        if(ValidURL(parent)){
            window.open(parent);
        }else{
            CheckParents(parent)
        }
        return;
    }

    if (ValidURL(target)){
        e.preventDefault();
        window.open(target);
    }
}*/
/*
Above did work, but suddenly stopped. Using below for now :-(
*/

window.addEventListener("click", function fn(e) {

        var e = window.e || e;
        var target = e.target || e.srcElement,
            parent = e.target.parentNode;

        if (e.target.tagName !== 'A'){
            e.preventDefault();
            if(ValidURL(parent)){
                window.open(parent);
            }else{
                CheckParents(parent)
            }
            return;
        }

        if (ValidURL(target)){
            e.preventDefault();
            window.open(target);
        }
    }, true);

var images = document.getElementsByTagName("img");
for (var i=0, len=images.length, img; i<len; i++) {
    img = images[i];
    img.addEventListener('click', function fn(e) {

            var e = window.e || e;
            var target = e.target || e.srcElement,
                parent = e.target.parentNode;

            if (e.target.tagName !== 'A'){
                e.preventDefault();
                if(ValidURL(parent)){
                    window.open(parent);
                }else{
                    CheckParents(parent)
                }
                return;
            }

            if (ValidURL(target)){
                e.preventDefault();
                window.open(target);
            }
        }, true);
}



// Check clicked nested element within anchor to depth of 5
function CheckParents(e){
    var parent = e.parentNode;
    for(var i = 0; i<=5; i++){
        if(ValidURL(parent)){
            window.open(parent)
        }
        parent = parent.parentNode
    }
}

function ValidURL(str) {
    var pattern = /(http|https):\/\/(\w+:{0,1}\w*)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%!\-\/]))?/;
    if(!pattern.test(str)) {
        return false;
    } else {
        return true;
    }
}
"""


class AppBrowser(webkit.WebView):

    def __init__(self, app, mailto=None):
        webkit.WebView.__init__(self)

        self.config = Config()

        self.initial_url = ""
        self.mailto_url = ""
        self.load_mail_urls()

        settings = self.get_settings()
        settings.set_property("allow-file-access-from-file-urls",
                                set_allow_file_access_from_file_urls)

        settings.set_property("allow-modal-dialogs", set_allow_modal_dialogs)

        settings.set_property("auto-load-images", set_auto_load_images)

        settings.set_property("default-font-size", int(set_default_font_size))

        settings.set_property("default-monospace-font-size",
                                int(set_default_monospace_font_size))

        settings.set_property("draw-compositing-indicators",
                                set_draw_compositing_indicators)

        settings.set_property("enable-accelerated-2d-canvas",
                                set_enable_accelerated_2d_canvas)

        settings.set_property("enable-caret-browsing",
                                set_enable_caret_browsing)

        settings.set_property("enable-developer-extras",
                                set_enable_developer_extras)

        settings.set_property("enable-dns-prefetching",
                                set_enable_dns_prefetching)

        settings.set_property("enable-frame-flattening",
                                set_enable_frame_flattening)

        settings.set_property("enable-fullscreen", set_enable_fullscreen)

        settings.set_property("enable-html5-database",
                                set_enable_html5_database)

        settings.set_property("enable-html5-local-storage",
                                set_enable_html5_local_storage)

        settings.set_property("enable-hyperlink-auditing",
                                set_enable_hyperlink_auditing)

        settings.set_property("enable-java", set_enable_java)

        settings.set_property("enable-javascript", set_enable_javascript)

        settings.set_property("enable-media-stream", set_enable_media_stream)

        settings.set_property("enable-mediasource", set_enable_mediasource)

        settings.set_property("enable-offline-web-application-cache",
                                set_enable_offline_web_application_cache)

        settings.set_property("enable-page-cache", set_enable_page_cache)

        settings.set_property("enable-plugins", set_enable_plugins)

        settings.set_property("enable-resizable-text-areas",
                                set_enable_resizable_text_areas)

        settings.set_property("enable-site-specific-quirks",
                                set_enable_site_specific_quirks)

        settings.set_property("enable-smooth-scrolling",
                                set_enable_smooth_scrolling)

        settings.set_property("enable-spatial-navigation",
                                set_enable_spatial_navigation)

        settings.set_property("enable-tabs-to-links", set_enable_tabs_to_links)

        settings.set_property("enable-webaudio", set_enable_webaudio)

        settings.set_property("enable-webgl", set_enable_webgl)

        settings.set_property("enable-write-console-messages-to-stdout",
                                set_enable_write_console_messages_to_stdout)

        settings.set_property("enable-xss-auditor", set_enable_xss_auditor)

        settings.set_property("javascript-can-access-clipboard",
                                set_javascript_can_access_clipboard)

        settings.set_property("javascript-can-open-windows-automatically",
                                set_javascript_can_open_windows_automatically)

        settings.set_property("load-icons-ignoring-image-load-setting",
                                set_load_icons_ignoring_image_load_setting)

        settings.set_property("media-playback-allows-inline",
                                set_media_playback_allows_inline)

        settings.set_property("media-playback-requires-user-gesture",
                                set_media_playback_requires_user_gesture)

        settings.set_property("minimum-font-size", set_minimum_font_size)

        settings.set_property("user-agent", set_user_agent)

        settings.set_property("zoom-text-only", set_zoom_text_only)
        self.set_settings(settings)

        self.ACCEPTED_LINKS = ["inbox.google.com",
                                "mail.google.com",
                                "calendar.google.com",
                                "[w]{3}.google.com/calendar",
                                "drive.google.com",
                                "accounts?.google.com"]

        # Cookie storage
        web_context = webkit.WebContext.get_default()
        manager = web_context.get_cookie_manager()
        manager.set_accept_policy(webkit.CookieAcceptPolicy.ALWAYS)
        manager.set_persistent_storage(COOKIES,
                                        webkit.CookiePersistentStorage.TEXT)

        # Load inital location (if started by mailto, open mailto url)
        self.load_uri(self.initial_url) if mailto is None else self.load_uri(
                                                    self.mailto_url + mailto
                                                    )

        # Navigation controls
        self.connect("load-changed", self.load_javascript)
        self.connect("decide-policy", self.on_navigation)
        self.connect("create", self.on_create)

        # Page change controls
        app.window.connect('notify::is-active', self.page_active)
        self.page_content = None
        self.ident = None
        self.sent_notification = False
        self.notify = Notifier()
        self.app = app

        # Download manager
        web_context.connect("download-started",
                            app.downloadsManager.download_requested)

    def load_mail_client(self):
        self.load_uri(self.initial_url)

    def load_mailto_url(self, url):
        self.load_uri(self.mailto_url + url)

    def load_mail_urls(self):
        self.initial_url = INITIAL_URL['inbox'] if not \
            self.config.get("SETTINGS", "usegmail", boolean=True) else \
            INITIAL_URL['gmail']

        self.mailto_url = MAILTO_URL['inbox'] if not \
            self.config.get("SETTINGS", "usegmail", boolean=True) else \
            MAILTO_URL['gmail']

    def page_active(self, window, param):
        if window.props.is_active:
            # remove timeout if ident not None
            if not self.ident is None:
                GLib.source_remove(self.ident)
                self.ident = None
                self.sent_notification = False
                self.page_content = None
            if self.app.window.get_urgency_hint():
                self.app.window.set_urgency_hint(False)
        elif not window.props.is_active:
            # create the timeout, if ident is None
            # get initial screenshot to compare against
            if self.ident is None:
                # runs every 3 minutes
                #self.ident = GLib.timeout_add(180000, self.screenshot)
                self.ident = GLib.timeout_add(60000, self.screenshot)
                #self.set_initial_shot()

    def set_initial_shot(self):
        """Bit of a hacky utility that's troublesome"""
        def get_initial_shot(source, res, user_data):
            self.page_content = self.get_snapshot_finish(res).get_data()
        # Run the shot
        self.get_snapshot(0, 0, None, get_initial_shot, None)

    def screenshot(self):
        self.get_snapshot(0, 0, None, self.get_shot, None)
        return True

    def get_shot(self, source, res, user_data):
        sc =  self.get_snapshot_finish(res)
        if self.page_content is None:
            # Just in case clause
            self.page_content = sc.get_data()
        else:
            if not self.page_content == sc.get_data() \
                        and not self.sent_notification:
                summary = "Updates"
                message = "Iris has new messages for you!"
                self.notify.create_notification(summary, message)
                self.sent_notification = True
                self.app.window.set_urgency_hint(True)

    def load_javascript(self, web_view, load_event):
        if webkit.LoadEvent.FINISHED == webkit.LoadEvent(load_event):
            self.run_javascript(google_links_hack, None, None, None)

    def on_navigation(self, web_view, decision, decision_type):
        # Check whether a nav request ( webkit.PolicyDecisionType(decision_type) == webkit.PolicyDecisionType(0) )
        if webkit.PolicyDecisionType(decision_type) == webkit.PolicyDecisionType.NAVIGATION_ACTION and \
            webkit.NavigationType.LINK_CLICKED == decision.get_navigation_type():
            req = decision.get_request()
            self.verify_accept(req.get_uri())

    def on_create(self, web_view, action):
        req = action.get_request()
        uri = req.get_uri()
        self.verify_accept(uri)

    def verify_accept(self, url2check):
        if url2check.replace(" ", "") == "":
            return

        ok = []
        for url in self.ACCEPTED_LINKS:
            ok.append(re.findall('https?://{0}'.format(url), url2check))

        flatten = lambda l: [item for sublist in l for item in sublist]
        lst = flatten(ok)

        if len(lst) > 0:
            self.load_uri(url2check)
        else:
            try:
                webbrowser.open_new_tab(url2check)
            except:
                webbrowser.open_new(url2check)
