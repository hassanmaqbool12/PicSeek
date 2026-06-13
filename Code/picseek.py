import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, Gio
import tempfile
import threading
import subprocess
import os
import time
import webbrowser
from requests import post

FILE = None
PATH = os.path.dirname(__file__)
TARGET = 'screen'
SCREENSHOT = False

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"
NAME = "PicSeek"

def show_error_log(text):
    print(f'[{GREEN}{NAME}{RESET}] {RED}LOG: {RESET}{text}')

def show_success_log(text):
    print(f'[{GREEN}{NAME}{RESET}] {GREEN}LOG: {RESET}{text}')

class AfterShotAPP(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.carbon.picseek-aftershot", flags=Gio.ApplicationFlags.NON_UNIQUE)
        pass

    def do_activate(self):
        self.window = Gtk.Window(application=self, title="DC")
        self.window.set_title("Draw & Capture")
        self.window.set_resizable(False)
        self.window.set_size_request(-1, 400)
        global SCREENSHOT
        self.type = 'Save' if SCREENSHOT else 'Search'

        styler = Gtk.CssProvider()
        styler.load_from_path(PATH+"/style.css")
        display = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(display, styler, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.head = Gtk.HeaderBar()
        self.head.set_show_close_button(True)
        self.window.set_titlebar(self.head)

        self.head.set_title('Draw & Search')

        self.option_bt = Gtk.Button.new_from_icon_name('help-about-symbolic', Gtk.IconSize.BUTTON)

        self.head.pack_start(self.option_bt)

        self.body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)

        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(FILE, 250, 190, True)
        self.image = Gtk.Image.new_from_pixbuf(self.pixbuf)

        self.loading_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.spinner = Gtk.Spinner()
        self.search_label = Gtk.Label(label=self.type)

        self.semi_bt_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.cancel_bt = Gtk.Button(label='Cancel')
        self.search_bt = Gtk.Button()
        self.search_bt.add(self.loading_box)

        self.semi_bt_box.pack_start(self.cancel_bt, True, True, 0)
        self.semi_bt_box.pack_end(self.search_bt, True, True, 0)
        
        self.loading_box.pack_start(self.spinner, True, True, 0)
        self.loading_box.pack_start(self.search_label, True, True, 0)
        
        self.body.pack_start(self.image, True, True, 0)
        self.body.pack_end(self.semi_bt_box, False, False, 0)

        self.body.set_name('body')
        self.image.set_name('image')
        self.search_bt.set_name('search')
        self.cancel_bt.set_name('cancel')

        self.search_bt.connect('clicked', self.search)
        self.cancel_bt.connect('clicked', self.kill)
        self.option_bt.connect('clicked', self.about)
        self.window.connect("destroy", self.kill)

        self.window.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.window.connect("key-press-event", self.on_key_press)

        self.window.set_can_focus(True)
        self.window.grab_focus()

        self.window.add(self.body)
        self.window.show_all()
        self.spinner.hide()

    def on_key_press(self, widget, event):
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self.search(None)

        if event.keyval == Gdk.KEY_Escape:
            self.kill()
    
    def search(self, widget):
        global SCREENSHOT
        global FILE
        if SCREENSHOT:
            import shutil
            import datetime
            if FILE and os.path.exists(FILE):
                dst = os.path.expanduser(f'~/Pictures/Screenshot-{datetime.datetime.now()}.png')
                shutil.copy(FILE, dst)
                os.remove(FILE)
                self.kill()
        else:
            self.overlay_mode = False
            self.window.set_title('Uploading Image')
            self.spinner.start()
            self.spinner.show()
            self.search_label.set_visible(False)
            self.search_bt.set_sensitive(False)
            threading.Thread(target=self.upload_image, args=(FILE, ), daemon=True).start()
    
    def show_error_dialog(self, text, sectext):
        self.normalize()
        self.dialog = Gtk.MessageDialog(
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            text=text
        )
        self.dialog.format_secondary_text(sectext)

        self.dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.dialog.add_button("Retry", Gtk.ResponseType.OK)
        self.dialog.set_default_response(Gtk.ResponseType.OK)
        

        self.dialog.set_title(text)

        def on_response(widget, response):
            widget.destroy()
            if response == Gtk.ResponseType.OK:
                widget.destroy()
                self.search(FILE)
            else:
                self.kill()
            return

        self.dialog.connect("response", on_response)
        self.dialog.show_all()
        return

    def upload_image(self, image):
        if image and os.path.exists(image):
            with open(image, 'rb') as file:
                show_success_log('Uploading image')
                try:
                    server = post('https://api.imgbb.com/1/upload?expiration=5&key=52fcc4c20855f87022e955fd5dfdb5e9', files={'image': file})
                    if server.status_code == 200:
                        response = server.json()
                        url = 'https://lens.google.com/uploadbyurl?url='+response['data']['url']
                        try:
                            subprocess.run(['chromium', f'--app={url}'])
                            show_success_log('Chromium found')
                        except:
                            try:
                                show_error_log('[LOG] Chromium not found. Opening in default browser.')
                                webbrowser.open(url)
                            except Exception as e:
                                show_error_log('[LOG] Error: No Browser Found. Webbrowser error: ', e)
                        
                        GLib.idle_add(self.kill)
                    else:
                        GLib.idle_add(self.show_error_dialog, 'Upload Rejected by Server', 'The server has rejected the image upload request')
                except:
                    GLib.idle_add(self.show_error_dialog, 'Connection error occured', 'You are offline, Please check your connection')
                
        else:
            GLib.idle_add(self.show_error_dialog, 'Image not Found', f'The requested image was not found at {FILE}')
        
        return True
        
        
    def normalize(self):
        self.window.set_title('Draw & Search')
        self.search_label.set_visible(True)
        self.spinner.hide()
        self.search_bt.set_sensitive(True)
        return
    
    def about(self, widget=None):
        webbrowser.open('https://github.com/hassanmaqbool12/PicSeek')
    
    def kill(self, widget=None):
        if FILE and os.path.exists(FILE):
            show_success_log('File Deleted')
            os.remove(FILE)
        self.quit()

class DrawCapture(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.carbon.picseek-draw", flags=Gio.ApplicationFlags.NON_UNIQUE)
        self.overlay_mode = True
        pass

    def do_activate(self):
        self.window = Gtk.Window(application=self)
        self.window.set_decorated(False)
        self.window.set_keep_above(True)
        self.window.fullscreen()
        self.window.set_app_paintable(True)
        self.window.set_name('overlay')
        self.is_on = False

        # Enable RGBA visual for transparency
        screen = self.window.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.window.set_visual(visual)

        # Capture mouse events
        self.window.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK)

        self.window.connect("destroy", self.kill)
        self.window.connect("button-press-event", self.on_press)
        self.window.connect("button-release-event", self.on_release)
        self.window.connect("motion-notify-event", self.on_motion)
        self.window.connect("draw", self.on_draw)

        # Selection coordinates
        self.start_x = self.start_y = self.end_x = self.end_y = 0
        self.dragging = False

        self.window.show_all()

        display = Gdk.Display.get_default()
        cursor = Gdk.Cursor.new_for_display(display, Gdk.CursorType.CROSS)
        self.window.get_window().set_cursor(cursor)

    def on_press(self, widget, event):
            
        self.start_x, self.start_y = int(event.x_root), int(event.y_root)
        self.end_x, self.end_y = self.start_x, self.start_y
        self.dragging = True
        self.is_on = True

    def on_motion(self, widget, event):
        if self.dragging:
            self.end_x, self.end_y = int(event.x_root), int(event.y_root)
            self.window.queue_draw()  # redraw rectangle

    def on_release(self, widget, event):
        self.end_x, self.end_y = int(event.x_root), int(event.y_root)
        self.dragging = False
        self.capture_selection()
        self.is_on = False

    def on_draw(self, widget, cr):

        if not self.overlay_mode:
            return False

        # Dark transparent overlay
        cr.set_source_rgba(0.1, 0.1, 0.1, 0.10)
        cr.paint()

        if self.dragging:

            x = min(self.start_x, self.end_x)
            y = min(self.start_y, self.end_y)
            w = abs(self.end_x - self.start_x)
            h = abs(self.end_y - self.start_y)

            context = widget.get_style_context()
            context.add_class("rubberband")

            success, color = context.lookup_color(
                "theme_selected_bg_color"
            )

            if success:
                cr.set_source_rgba(
                    color.red,
                    color.green,
                    color.blue,
                    0.10
                )
            else:
                cr.set_source_rgba(0.3, 0.5, 1, 0.10)

            cr.rectangle(x, y, w, h)
            cr.fill_preserve()

            if success:
                cr.set_source_rgba(
                    color.red,
                    color.green,
                    color.blue,
                    1
                )
            else:
                cr.set_source_rgba(0.3, 0.5, 1, 0.1)

            cr.set_line_width(1)
            cr.stroke()

        return False

    def capture_selection(self):
        global FILE
        FILE = os.path.join(tempfile.gettempdir(), "picseek_capture.png")

        #XXX This if statement is very useful. It prevents duplication of Sample pictures.
        if FILE and os.path.exists(FILE):
            os.remove(FILE)

        x1, y1 = min(self.start_x, self.end_x), min(self.start_y, self.end_y)
        x2, y2 = max(self.start_x, self.end_x), max(self.start_y, self.end_y)

        width = x2 - x1
        height = y2 - y1
        region = f"{width}x{height}+{x1}+{y1}"

        # close overlay first
        self.window.hide()

        # allow compositor to redraw screen
        while Gtk.events_pending():
            Gtk.main_iteration()

        time.sleep(0.15)
        print(region)
        subprocess.run(["flameshot", "gui", "--region", region,"--accept-on-select" , "--path", FILE])

        show_success_log("Captured image: "+FILE)

        self.quit()
        
    def kill(self, widget=None):
        if FILE and os.path.exists(FILE):
            os.remove(FILE)
        self.quit()


# This class is experimental. This would be later used to allow PicSeek to also act as a ScreenShot tool

class ScreenShot(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.carbon.picseek-screenshot')
        pass

    def do_activate(self):

        styler = Gtk.CssProvider()
        styler.load_from_path(PATH+"/style.css")
        display = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(display, styler, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.window = Gtk.Window(application=self)
        self.window.set_resizable(False)

        self.head = Gtk.HeaderBar()
        self.head.set_show_close_button(True)
        self.window.set_titlebar(self.head)

        self.capture_bt = Gtk.Button(label='Take Screenshot')

        self.head.pack_start(self.capture_bt)

        self.body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.bt_body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        self.label = Gtk.Label(label='Capture Area')

        self.screen_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.screen_icon = Gtk.Image.new_from_icon_name('computer', Gtk.IconSize.BUTTON)
        self.screen_icon.set_pixel_size(32)
        self.screen_text = Gtk.Label(label='Screen')

        self.screen_box.pack_start(self.screen_icon, True, True, 0)
        self.screen_box.pack_start(self.screen_text, True, True, 0)

        self.window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.window_icon = Gtk.Image.new_from_icon_name('window', Gtk.IconSize.BUTTON)
        self.window_icon.set_pixel_size(32)
        self.window_text = Gtk.Label(label='Window')

        self.window_box.pack_start(self.window_icon, True, True, 0)
        self.window_box.pack_start(self.window_text, True, True, 0)

        self.area_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.area_icon = Gtk.Image.new_from_icon_name('edit-select-all-symbolic', Gtk.IconSize.BUTTON)
        self.area_icon.set_pixel_size(25)
        self.area_text = Gtk.Label(label='Selection')

        self.area_box.pack_start(self.area_icon, True, True, 0)
        self.area_box.pack_start(self.area_text, True, True, 0)

        self.screen_bt = Gtk.Button()
        self.screen_bt.add(self.screen_box)

        self.window_bt = Gtk.Button()
        self.window_bt.add(self.window_box)

        self.area_bt = Gtk.Button()
        self.area_bt.add(self.area_box)

        self.bt_body.pack_start(self.screen_bt, True, True, 0)
        self.bt_body.pack_start(self.window_bt, True, True, 0)
        self.bt_body.pack_start(self.area_bt, True, True, 0)

        self.body.pack_start(self.label, False, False, 0)
        self.body.pack_start(self.bt_body, True, True, 0)

        self.capture_bt.set_name('search')
        self.body.set_name('body')
        self.label.set_name('head-label')
        self.screen_bt.set_name('selected')
        self.window_bt.set_name('option-bt')
        self.area_bt.set_name('option-bt')

        self.label.set_halign(Gtk.Align.START)

        self.capture_bt.connect('clicked', self.prepare_shoot)
        self.screen_bt.connect('clicked', self.replace_att, 'screen')
        self.window_bt.connect('clicked', self.replace_att, 'window')
        self.area_bt.connect('clicked', self.replace_att, 'area')

        self.window.add(self.body)
        self.window.show_all()
        return
    
    def replace_att(self, widget=None, target='screen'):
        global TARGET
        if TARGET and target:
            self.screen_bt.set_name('option-bt')
            self.window_bt.set_name('option-bt')
            self.area_bt.set_name('option-bt')
            if widget:
                widget.set_name('selected')
            TARGET = target
        else:
            pass

    def prepare_shoot(self, widget=None):
        self.shoot()
        return
    
    def shoot(self):
        global FILE
        global TARGET

        FILE = os.path.join(tempfile.gettempdir(), "picseek_capture.png")

        # close overlay first
        self.window.hide()

        # allow compositor to redraw screen
        while Gtk.events_pending():
            Gtk.main_iteration()

        time.sleep(0.15)

        if TARGET == 'screen':
            subprocess.run(["scrot", FILE])

        if TARGET == 'window':
            wid = subprocess.check_output("xwininfo | awk '/Window id/{print $4}'", shell=True).decode().strip()
            if wid:
                subprocess.run(['wmctrl', '-i', '-R', wid])
                subprocess.run(['scrot', '-u', FILE])

        self.kill()
    
    def kill(self, widget=None):
        self.quit()

if __name__ == "__main__":
        app = DrawCapture()
        app.run()

        if FILE and os.path.exists(FILE):
            user = AfterShotAPP()
            user.run(None)
