import string
import pyray as _rl
import inspect, datetime
import datetime


class GUIState:
    """GUI state, example usage might be to edit widget values or see if a widget uses a keyboard key."""

    Keyboard = []
    Mouse = []
    MouseWheel = False
    Widgets = {}
    SpecialWindows = {}
    SelectedWidget = 0
    Curwidget = 0
    Notifications = []
    NotifHeight = []

    def get_is_current():
        if GUIState.SelectedWidget == GUIState.Curwidget and curwindow.selected:
            return True

    def get_window():
        if curwindow == None:
            raise Exception("you cant draw outside of a window")
        return curwindow


_textmeasurecache = {}


def _measure_text(text, fs):
    key = (text, fs)
    if key not in _textmeasurecache:
        _textmeasurecache[key] = _rl.measure_text(text, fs)
    return _textmeasurecache[key]


def set_indent(value):
    """Sets the indent level for widgets. Default is 0."""
    global indent
    indent = value


def lerp(a, b, t):
    t *= _rl.get_frame_time() * 30
    return a + (b - a) * t


_imagecache: dict[str, _rl.Texture2D] = {}


def _cached_image(fp):
    if fp not in _imagecache:
        _imagecache[fp] = _rl.load_texture(fp)
    return _imagecache[fp]


mousecur_wait = _rl.MouseCursor.MOUSE_CURSOR_DEFAULT


def set_mouse_cursor(cursor):
    """Sets the mouse cursor.
    Args:
        cursor (_rl.MouseCursor): The cursor to set.
    """
    global mousecur_wait
    mousecur_wait = cursor


global curwindow, winy, lastwinychange, winx, lastwinxchange, indent


def init():
    """Initializes the GUI system. Must be called before any other GUI functions."""
    global curwindow, winy, lastwinychange, winx, lastwinxchange, indent
    indent = 0
    curwindow = None
    winy, lastwinychange, winx, lastwinxchange = 0, [], 0, []


def sameline():
    """Puts widgets next to eachother"""
    global winy, winx, lastwinxchange, lastwinychange, curwindow
    if len(lastwinxchange) == 0 or len(lastwinychange) == 0:
        return
    winy -= lastwinychange[-1]
    winx = lastwinxchange[-1] - curwindow.scroll_x


def cancel_sameline():
    """Cancels the last sameline call."""
    global winy, lastwinychange, winx
    winy += lastwinychange[-1]
    winx = indent


def _log(text):
    """Prints a log message with a timestamp and what function called it."""
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {_get_class_name} {text}")


def _get_class_name(depth=2):
    """Gets the class name of the caller.

    Args:
        depth (int, optional): stack depth. Defaults to 2.

    Returns:
        str: class name
    """
    caller_frame = inspect.stack()[depth][0]  # this function gets called
    caller_locals = caller_frame.f_locals
    if "self" in caller_locals:
        return str(caller_locals["self"].__class__.__name__)
    return str("")


def NotifTick():
    """Ticks the notification system. Must be called every frame."""
    for i in GUIState.Notifications:
        # Calculate animation offset
        time_remaining = (i["duration"] - datetime.datetime.now()).total_seconds()
        xoff = min(300 * time_remaining, 0) if time_remaining < 1 else 0
        if time_remaining < 0:
            GUIState.NotifHeight.pop(GUIState.Notifications.index(i))
            GUIState.Notifications.remove(i)
            continue

        # Draw notification
        w = _measure_text(max(i["title"], i["text"]), 10) + 10
        h = GUIState.NotifHeight[GUIState.Notifications.index(i)]
        y_pos = sum(GUIState.NotifHeight[: GUIState.Notifications.index(i)]) * 1.1 + 10
        x_pos = _rl.get_screen_width() - 10 - w + xoff

        a = 255 - round(0 if time_remaining > 1 else 255 * (1 - time_remaining))

        if (
            _rl.check_collision_point_rec(
                _rl.get_mouse_position(), [x_pos, y_pos, w, h]
            )
            and _rl.is_mouse_button_pressed(_rl.MouseButton.MOUSE_BUTTON_LEFT)
            and not i["clicked"]
        ):
            i["duration"] = datetime.datetime.now() + datetime.timedelta(seconds=1)
            i["clicked"] = True

        _rl.draw_rectangle_rec([x_pos, y_pos, w, h], _rl.Color(40, 40, 40, a))
        _rl.draw_rectangle_lines_ex([x_pos, y_pos, w, h], 2, _rl.Color(0, 255, 255, a))
        _rl.draw_text(
            i["title"],
            round(x_pos + 5),
            round(y_pos + 2),
            10,
            _rl.Color(255, 255, 255, a),
        )
        _rl.draw_text(
            i["text"],
            round(x_pos + 5),
            round(y_pos + 12),
            10,
            _rl.Color(255, 255, 255, a),
        )

        if not i["clicked"]:
            progress = 0 - (time_remaining / i["total"]) * 1000
            _rl.draw_line(
                round(x_pos),
                round(y_pos + GUIState.NotifHeight[GUIState.Notifications.index(i)]),
                round(x_pos - (w * progress)),
                round(y_pos + GUIState.NotifHeight[GUIState.Notifications.index(i)]),
                _rl.Color(255, 255, 255, a),
            )


def notify(title, text, duration):
    """Creates a notification."""
    # if _rl.is_window_focused():
    #    n = notify2.Notification(title,text,duration)
    #    n.set_timeout(duration)
    #    n.show()
    # couldnt install notify2 on my machine so f**k this shit
    duration *= 1000
    n = {
        "title": title,
        "text": text,
        "duration": datetime.datetime.now() + datetime.timedelta(milliseconds=duration),
        "total": duration,
        "clicked": False,
    }
    h = (text.count("\n") + 3) * 10
    GUIState.Notifications.append(n)
    GUIState.NotifHeight.append(h)


class Window:
    def __init__(
        self,
        x,
        y,
        w,
        h,
        title,
        collapsed=False,
        resizable=True,
        movable=True,
        titlecolor=_rl.Color(0, 255, 255, 255),
        scrollable=True,
    ):
        """A draggable, resizable window container for GUI widgets.

        Args:
            x (int): Initial x position of window
            y (int): Initial y position of window
            w (int): Width of window content area
            h (int): Height of window content area
            title (str): Window title text
            collapsed (bool, optional): Start collapsed state. Defaults to False.
            resizable (bool, optional): Allow window resizing. Defaults to True.
            movable (bool, optional): Allow window dragging. Defaults to True.
            titlecolor (_rl.Color, optional): Color of title bar. Defaults to cyan.
            scrollable (bool, optional): Enable content scrolling. Defaults to True.
        """
        self.x = x
        self.y = y
        self.w = w + 20
        self.h = h + 30
        self.title = title
        self.titlecolor = titlecolor
        self.collapsed = collapsed
        self.resizable = resizable
        self.movable = movable
        self.scrollable = scrollable
        self.resizing = False
        self.dragging = False
        self.drag_x = 0
        self.drag_y = 0
        self.wintex = _rl.load_render_texture(1, 1)
        self.scroll_x = 0
        self.scroll_y = 0
        self.scroll_x_float = 0
        self.scroll_y_float = 0
        self.realscroll_x = 0
        self.realscroll_y = 0
        self.maxscroll_x = 0
        self.titlebar = True
        self.titlebar_height = 15
        self.selected = False

    def __repr__(self):
        return f"<{'collapsed' if self.collapsed else 'expanded'} Window {self.title} [{self.x}, {self.y}, {self.w}, {self.h}]>"

    def __enter__(self):
        global curwindow, wintex, winy, lastwinychange, lastwinxchange
        curwindow = None
        _rl.unload_render_texture(self.wintex)
        self.wintex = _rl.load_render_texture(self.w, self.h)
        _rl.begin_texture_mode(self.wintex)
        _rl.set_trace_log_level(_rl.TraceLogLevel.LOG_NONE)
        if not self.collapsed:
            _rl.draw_rectangle(0, 0, self.w, self.h, _rl.Color(20, 20, 20, 255))
        curwindow = self
        winy = 1
        self.maxscroll_x = 1
        GUIState.Curwidget = 0
        lastwinxchange = []
        lastwinychange = []

    def __exit__(self, *args):
        if self.titlebar:
            self.titlebar_height = 15
        else:
            self.titlebar_height = 0
        global curwindow, winy
        if not self.collapsed:
            _rl.draw_rectangle_lines_ex(
                [0, self.titlebar_height, self.w, self.h - self.titlebar_height],
                5,
                _rl.Color(20, 20, 20, 255),
            )
            _rl.draw_rectangle_lines_ex(
                [0, 0, self.w, self.h], 1, _rl.Color(40, 40, 40, 255)
            )
        if not self.collapsed:
            triangleh = self.h
            trianglec = _rl.Color(40, 40, 40, 255)
        else:
            triangleh = 15
            trianglec = _rl.Color(0, 255, 255, 255)
        if self.resizable:
            _rl.draw_triangle(
                [0 + self.w, 0 + triangleh],
                [0 + self.w, 0 + triangleh - 10],
                [0 + self.w - 10, 0 + triangleh],
                trianglec,
            )
        mp = _rl.get_mouse_position()
        mpd = _rl.get_mouse_delta()
        dt = _rl.get_frame_time() * 60
        if self.scrollable:
            if winy > self.h - (self.titlebar_height * 2):
                scroll_height = max(
                    30, (self.h / winy) * (self.h - (self.titlebar_height * 2))
                )
                scroll_pos = (-self.scroll_y / max(winy, self.h)) * (
                    self.h - (self.titlebar_height * 2)
                )
                _rl.draw_rectangle(
                    self.w - 2,
                    round(scroll_pos + self.titlebar_height),
                    2,
                    round(scroll_height),
                    _rl.Color(60, 60, 60, 255),
                )

                if _rl.check_collision_point_rec(
                    mp,
                    [
                        self.x + self.w - 2,
                        self.y + scroll_pos + self.titlebar_height,
                        2,
                        scroll_height,
                    ],
                ):
                    if _rl.is_mouse_button_down(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                        self.realscroll_y -= mpd.y * (winy / self.h)

            if self.maxscroll_x > self.w - 20:
                scroll_width = max(30, (self.w / self.maxscroll_x) * (self.w - 20))
                scroll_pos = (-self.scroll_x / max(self.maxscroll_x, self.w)) * (
                    self.w - 20
                )
                _rl.draw_rectangle(
                    round(scroll_pos),
                    self.h - 2,
                    round(scroll_width),
                    2,
                    _rl.Color(60, 60, 60, 255),
                )

                if _rl.check_collision_point_rec(
                    mp, [self.x + scroll_pos, self.y + self.h - 2, scroll_width, 2]
                ):
                    if _rl.is_mouse_button_down(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                        self.realscroll_x += mpd.x * (self.maxscroll_x / self.w)

        # Update max horizontal scroll limit
        max_scroll_x = -(max(0, self.maxscroll_x - self.w + 20))
        if self.realscroll_x < max_scroll_x:
            self.realscroll_x = max_scroll_x
        if self.titlebar:
            color = self.titlecolor
            if not self.selected:
                color = _rl.Color(128, 128, 128, 255)
            _rl.draw_rectangle(
                0,
                0,
                self.w,
                self.titlebar_height,
                _rl.Color(color.r // 2, color.g // 2, color.b // 2, 255),
            )
            _rl.draw_rectangle_lines_ex([0, 0, self.w, self.titlebar_height], 1, color)
            _rl.draw_rectangle_rec([2, 2, 11, 11], color)
            _rl.draw_text(self.title, self.titlebar_height, 2, 10, _rl.WHITE)
            if _rl.is_mouse_button_pressed(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                if _rl.check_collision_point_rec(mp, [self.x + 3, self.y + 3, 10, 10]):
                    self.collapsed = not self.collapsed
        mwm = _rl.get_mouse_wheel_move_v().y
        if self.scrollable:
            if _rl.check_collision_point_rec(mp, [self.x, self.y, self.w, self.h]):
                if _rl.is_key_down(_rl.KeyboardKey.KEY_LEFT_SHIFT):
                    self.realscroll_x += round(mwm * 20)
                else:
                    self.realscroll_y += round(mwm * 20)
        if self.realscroll_y > 0:
            self.realscroll_y = 0
        if self.realscroll_x > 0:
            self.realscroll_x = 0
        max_scroll = -(max(0, winy - self.h + (self.titlebar_height * 2)))
        if self.realscroll_y < max_scroll:
            self.realscroll_y = max_scroll
        if self.realscroll_x < max_scroll_x:
            self.realscroll_x = max_scroll_x
        self.scroll_x_float = lerp(self.scroll_x_float, self.realscroll_x, 0.9)
        self.scroll_y_float = lerp(self.scroll_y_float, self.realscroll_y, 0.9)
        self.scroll_x = round(self.scroll_x_float)
        self.scroll_y = round(self.scroll_y_float)
        if self.selected:
            GUIState.Keyboard.append("Enter")
            GUIState.Keyboard.append("Up")
            GUIState.Keyboard.append("Down")
            if _rl.is_key_pressed(_rl.KeyboardKey.KEY_DOWN):
                GUIState.SelectedWidget += 1
            if _rl.is_key_pressed(_rl.KeyboardKey.KEY_UP):
                GUIState.SelectedWidget -= 1
            GUIState.SelectedWidget %= GUIState.Curwidget + 1
        if _rl.is_mouse_button_pressed(_rl.MouseButton.MOUSE_BUTTON_LEFT):
            if self.gethover():
                self.selected = True
            else:
                GUIState.SelectedWidget = 0
                self.selected = False
            if (not self.resizing) and self.movable:
                if self.titlebar:
                    if (
                        _rl.check_collision_point_rec(mp, [self.x, self.y, self.w, 15])
                        or self.dragging
                    ):
                        self.dragging = True
            if self.resizable and not self.collapsed:
                if (
                    _rl.check_collision_point_rec(
                        mp, [self.x + self.w - 10, self.y + triangleh - 10, 10, 10]
                    )
                    or self.resizing
                ):
                    self.resizing = True
        if self.resizing and self.resizable:
            self.w += round(mpd.x)
            if not self.collapsed:
                self.h += round(mpd.y)
            if self.w < 30:
                self.w = 30
            if self.h < 30:
                self.h = 30
        if self.dragging and self.movable:
            self.x += round(mpd.x)
            self.y += round(mpd.y)
        if _rl.is_mouse_button_up(0):
            self.dragging = False
            self.resizing = False
        _rl.end_texture_mode()
        _rl.draw_texture_pro(
            self.wintex.texture,
            [0, 0, self.wintex.texture.width, -self.wintex.texture.height],
            [self.x, self.y, self.wintex.texture.width, self.wintex.texture.height],
            [0, 0],
            0,
            _rl.Color(255, 255, 255, 255),
        )
        winy = 0
        self.widgetid = 0
        curwindow = None
        # this didnt work so well...
        # _rl.set_mouse_cursor(mousecur_wait)

    def gethover(self):
        mp = _rl.get_mouse_position()
        if _rl.check_collision_point_rec(mp, [self.x, self.y, self.w, self.h]):
            return True
        return False


class Widget:
    def __init__(self, x, y, w, h, *args):
        """Base class for all widgets. Useful for creating custom widgets."""
        global winy, winx, lastwinxchange, lastwinychange, indent
        cw = curwindow
        self.x = x + cw.scroll_x
        self.y = y + cw.scroll_y
        self.vy = max(0, y + cw.scroll_y + 20)  # Add titlebar height check
        self.w = w
        self.h = h
        self.y += 20
        self.x += 5
        self.off = _rl.Vector2(cw.x, cw.y)
        self.w = min(w, cw.w - 10 - winx - cw.scroll_x)
        self.vh = min(h, cw.h - 25 - winy - cw.scroll_y)
        if self.vy > cw.titlebar_height:  # Add top cutoff check
            self.vh = min(self.vh, self.y - self.vy + h)
        self.mp = _rl.get_mouse_position()
        xs = x + w
        if xs > cw.maxscroll_x:
            cw.maxscroll_x = xs
        winy += self.h + 3
        lastwinychange.append(self.h + 3)
        lastwinxchange.append(self.x + w + 5)
        winx = indent
        GUIState.Curwidget += 1
        if self.y > cw.h:
            return True
        # _log(f"Widget: {_get_class_name()} at {self.x},{self.y} by {self.w}x{self.h}")
        return False

    def getpressed():
        return (
            GUIState.get_is_current()
            and _rl.is_key_pressed(_rl.KeyboardKey.KEY_ENTER)
            and curwindow.selected
        )

    def getheld():
        return (
            GUIState.get_is_current()
            and _rl.is_key_down(_rl.KeyboardKey.KEY_ENTER)
            and curwindow.selected
        )


class frame(Widget):
    def __init__(self, w, h):
        """Standard frame widget.

        Args:
            w (int): width of the Widget
            h (int): height of the Widget
        """
        global curwindow, winx, winy
        super().__init__(winx, winy, w, 20)
        self.wintex = _rl.load_render_texture(w, h)
        self.cw = curwindow
        self.collapsed = False
        self.scroll_x = self.cw.scroll_x
        self.scroll_y = self.cw.scroll_y
        self.maxscroll_x = 0
        self.maxscroll_y = 0
        self.titlebar_height = 20
        self.x = winx + self.cw.scroll_x
        self.y = winy + self.cw.scroll_y
        self.w = w
        self.h = h
        self.selected = True

    def __enter__(self):
        global curwindow, winx, winy
        self.winx = winx
        self.winy = winy + self.h
        winy = 0
        winx = 0
        curwindow = self
        _rl.end_texture_mode()  # stop drawing to window surface
        _rl.begin_texture_mode(self.wintex)
        _rl.draw_rectangle(0, 0, self.w, self.h, _rl.Color(20, 20, 20, 255))
        _rl.draw_rectangle_lines_ex(
            [0, 0, self.w - 1, self.h - 1], 1, _rl.Color(40, 40, 40, 255)
        )

    def __exit__(self, *args):
        global curwindow, winx, winy
        _rl.end_texture_mode()
        curwindow = self.cw
        _rl.begin_texture_mode(self.cw.wintex)  # resume drawing to window
        _rl.draw_texture_pro(
            self.wintex.texture,
            [0, 0, self.wintex.texture.width, -self.wintex.texture.height],
            [self.x, self.y, self.wintex.texture.width, self.wintex.texture.height],
            [0, 0],
            0,
            _rl.Color(255, 255, 255, 255),
        )
        _rl.unload_render_texture(self.wintex)
        winx = self.winx
        winy = self.winy


class button(Widget):
    def __init__(self, w, label):
        """Standard button widget with text label.

        Args:
            w (int): Width of the button in pixels
            label (str): Text to display on the button
        """
        self.pressed = False
        self.held = False
        if curwindow.collapsed:
            return
        if super().__init__(winx, winy, w, 12):
            self = None
            return
        color = _rl.Color(128, 128, 128, 0)
        fg = _rl.Color(255, 255, 255, 255)
        if not curwindow.h < self.y + 5:
            if _rl.check_collision_point_rec(
                self.mp, [self.x + self.off.x, self.vy + self.off.y, self.w, self.vh]
            ):
                set_mouse_cursor(_rl.MouseCursor.MOUSE_CURSOR_POINTING_HAND)
                color.a = 128
                if _rl.is_mouse_button_down(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                    fg = (102, 191, 255, 255)
                    self.held = True
                if _rl.is_mouse_button_released(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                    self.pressed = True
                    GUIState.SelectedWidget = GUIState.Curwidget
        if Widget.getpressed():
            self.pressed = True
        if GUIState.SelectedWidget == GUIState.Curwidget:
            fg = (102, 191, 255, 255)
        if Widget.getheld():
            self.held = True
        _rl.draw_rectangle(self.x, self.vy, self.w, self.vh, color)
        _rl.draw_rectangle_lines_ex([self.x, self.vy, self.w, self.vh], 1, fg)
        _rl.draw_text(label, self.x + 2, self.y + 1, 10, fg)


class button_img(Widget):
    def __init__(self, w, h, fp, source=None):
        """Image button widget that displays an image instead of text.

        Args:
            w (int): Width of the button in pixels
            h (int): Height of the button in pixels
            fp (str): File path to the image
            source (list, optional): Source rectangle [x,y,w,h] for image. Defaults to None.
        """
        self.pressed = False
        self.held = False
        image = _cached_image(fp)
        if curwindow.collapsed:
            self = None
            return
        if super().__init__(winx, winy, w, h):
            self = None
            return
        if source is None:
            source = [0, 0, image.width, image.height]
        color = _rl.Color(128, 128, 128, 0)
        fg = _rl.Color(255, 255, 255, 255)
        if _rl.check_collision_point_rec(
            self.mp, [self.x + self.off.x, self.y + self.off.y, self.w, self.h]
        ):
            color.a = 128
            if _rl.is_mouse_button_down(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                fg = _rl.Color(102, 191, 255, 255)
                self.held = True
            if _rl.is_mouse_button_released(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                self.pressed = True
                GUIState.SelectedWidget = GUIState.Curwidget
        if GUIState.SelectedWidget == GUIState.Curwidget:
            fg = (102, 191, 255, 255)
        if Widget.getpressed():
            self.pressed = True
        if Widget.getheld():
            self.held = True
        _rl.draw_rectangle(self.x, self.y, self.w, self.h, color)
        _rl.draw_texture_pro(
            image,
            source,
            [self.x, self.y, w, self.h],
            [0, 0],
            0,
            _rl.Color(255, 255, 255, 255),
        )
        _rl.draw_rectangle_lines_ex([self.x, self.y, self.w, self.vh], 1, fg)


class button_icon(Widget):
    def __init__(self, w, h, label, fp, source=None):
        """Button widget with both a label and an image.

        Args:
            w (int): Width of the button in pixels
            h (int): Height of the button in pixels
            label (str): Text to display on the button
            fp (str): File path to the image
            source (list, optional): Source rectangle [x,y,w,h] for image. Defaults to None.
        """
        h = max(h, 10)
        self.pressed = False
        self.held = False
        image = _cached_image(fp)
        if curwindow.collapsed:
            self = None
            return
        if super().__init__(winx, winy, w, h + 2):
            self = None
            return
        if source is None:
            source = [0, 0, image.width, image.height]
        color = _rl.Color(128, 128, 128, 0)
        fg = _rl.Color(255, 255, 255, 255)
        if _rl.check_collision_point_rec(
            self.mp, [self.x + self.off.x, self.y + self.off.y, self.w, self.h]
        ):
            color.a = 128
            if _rl.is_mouse_button_down(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                fg = _rl.Color(102, 191, 255, 255)
                self.held = True
            if _rl.is_mouse_button_released(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                self.pressed = True
                GUIState.SelectedWidget = GUIState.Curwidget
        if GUIState.SelectedWidget == GUIState.Curwidget:
            fg = (102, 191, 255, 255)
        if Widget.getpressed():
            self.pressed = True
        if Widget.getheld():
            self.held = True
        _rl.draw_rectangle(self.x, self.y, self.w, self.h, color)
        _rl.draw_texture_pro(
            image,
            source,
            [self.x + 1, self.y + 1, h, h],
            [0, 0],
            0,
            _rl.Color(255, 255, 255, 255),
        )
        _rl.draw_rectangle_lines_ex([self.x, self.y, self.w, self.vh], 1, fg)
        _rl.draw_text(label, self.x + 2 + h, self.y + (self.h // 2) - 5, 10, fg)


class label(Widget):
    def __init__(self, text):
        """Text label widget for displaying static text.

        Args:
            text (str): Text content to display
        """
        if curwindow.collapsed:
            return
        w = _measure_text(text, 10) + 2
        h = 12 * (text.count("\n") + 1)
        if super().__init__(winx, winy, w, h):
            self = None
            return
        if GUIState.SelectedWidget == GUIState.Curwidget:
            _rl.draw_rectangle_lines_ex(
                [self.x, self.y, self.w, self.h], 1, _rl.Color(102, 191, 255, 255)
            )
        _rl.draw_text(
            text, round(self.x + 1), round(self.y), 10, _rl.Color(255, 255, 255, 255)
        )


class sliderInfo:
    def __init__(self, value, pressed=False):
        self.value = value
        self.pressed = pressed
        self.textactive = False

    def __int__(self):
        return self.value


class colorInfo:
    def __init__(self, value, pickeractive=False):
        self.r = value[0]
        self.g = value[1]
        self.b = value[2]
        self.pickeractive = pickeractive

    def __int__(self):
        return (self.r, self.g, self.b, self.a)


class sliderInfo2D:
    def __init__(self, value, pressed=False):
        self.x = value[0]
        self.y = value[1]
        self.pressed = pressed


class TextInput:
    def __init__(self, value="", selected=False, cursor=-1, selection_start=-1):
        self.value = value
        self.selected = selected
        self.cursor = len(value) - 1
        self.selection_start = selection_start


class textinput(Widget):
    def __init__(self, w: int, label: str, id: str, default="") -> TextInput:
        """Text input field widget for editable text.

        Args:
            w (int): Width of the input field
            label (str): Placeholder text when empty
            id (str): Unique identifier for this input
            default (str, optional): Default text value. Defaults to empty string.

        Returns:
            TextInput: TextInput object containing the input state
        """
        bg = _rl.Color(128, 128, 128, 64)
        fg = _rl.Color(255, 255, 255, 255)
        if f"ti_{id}" in GUIState.Widgets:
            self.obj = GUIState.Widgets[f"ti_{id}"]
        else:
            self.obj = TextInput(default)
            GUIState.Widgets[f"ti_{id}"] = self.obj
        self.selected = self.obj.selected
        self.cursor = self.obj.cursor
        self.value = self.obj.value
        self.selection_start = self.obj.selection_start
        if curwindow.collapsed:
            return
        if super().__init__(winx, winy, w, 12):
            self = None
            return
        self.w = max(self.w, _measure_text(self.value + " ", 10) + 5)
        if not curwindow.h < self.y + 5:
            if _rl.check_collision_point_rec(
                self.mp, [self.x + self.off.x, self.y + self.off.y, self.w, self.vh]
            ):
                bg.a = 128
                if _rl.is_mouse_button_down(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                    fg = _rl.Color(102, 191, 255, 255)
                    click_pos = self.mp.x - (self.x + self.off.x)

                    # Calculate cursor position based on text width
                    cursor_pos = 0
                    for i in range(len(self.value)):
                        if _measure_text(self.value[: i + 1], 10) > click_pos:
                            break
                        cursor_pos = i

                    self.cursor = cursor_pos
                    self.selection_start = cursor_pos
                if _rl.is_mouse_button_released(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                    self.selected = True
                    GUIState.SelectedWidget = GUIState.Curwidget
            else:
                if _rl.is_mouse_button_down(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                    self.selected = False
        if GUIState.SelectedWidget == GUIState.Curwidget:
            fg = _rl.Color(102, 191, 255, 255)
        if Widget.getpressed():
            self.selected = not self.selected
        _rl.draw_rectangle(self.x, self.y, self.w, self.vh, bg)
        if self.selected:
            GUIState.Keyboard += (
                string.ascii_letters + string.digits + string.punctuation
            ).split()
            GUIState.Keyboard.extend(["Backspace", "Left", "Right"])
            charint = _rl.get_char_pressed()
            charstr = chr(charint)

            if _rl.is_key_pressed(_rl.KeyboardKey.KEY_LEFT):
                self.cursor = max(0, self.cursor - 1)
                if not _rl.is_key_down(_rl.KeyboardKey.KEY_LEFT_SHIFT):
                    self.selection_start = self.cursor
            if _rl.is_key_pressed(_rl.KeyboardKey.KEY_RIGHT):
                self.cursor = min(len(self.value), self.cursor + 1)
                if not _rl.is_key_down(_rl.KeyboardKey.KEY_LEFT_SHIFT):
                    self.selection_start = self.cursor

            if charint != 0:
                if self.selection_start != self.cursor:
                    start = min(self.selection_start, self.cursor)
                    end = max(self.selection_start, self.cursor)
                    self.value = self.value[:start] + charstr + self.value[end:]
                    self.cursor = start + 1
                else:
                    self.value = (
                        self.value[: self.cursor + 1]
                        + charstr
                        + self.value[self.cursor + 1 :]
                    )
                    self.cursor += 1
                self.selection_start = self.cursor

            if _rl.is_key_pressed(
                _rl.KeyboardKey.KEY_BACKSPACE
            ) or _rl.is_key_pressed_repeat(_rl.KeyboardKey.KEY_BACKSPACE):
                if self.selection_start != self.cursor:
                    start = min(self.selection_start, self.cursor)
                    end = max(self.selection_start, self.cursor)
                    self.value = self.value[:start] + self.value[end:]
                    self.cursor = start
                    self.selection_start = start
                elif self.cursor >= 0:
                    self.value = (
                        self.value[: self.cursor] + self.value[self.cursor + 1 :]
                    )
                    self.cursor = max(0, self.cursor - 1)
                    self.selection_start = self.cursor
        self.cursor = min(len(self.value) - 1, self.cursor)
        self.selection_start = min(len(self.value) - 1, self.selection_start)
        if self.value == "":
            fg.a = 128
            _rl.draw_text(label, self.x + 2, self.y + 1, 10, fg)
            fg.a = 255
            _rl.draw_text(
                ("_" if round(_rl.get_time()) % 2 == 0 and self.selected else ""),
                self.x + 2,
                self.y + 1,
                10,
                fg,
            )
        else:
            if self.selection_start != self.cursor:
                start = min(self.selection_start, self.cursor)
                end = max(self.selection_start, self.cursor)
                pre_text = self.value[:start]
                sel_text = self.value[start:end]
                post_text = self.value[end:]

                _rl.draw_text(pre_text, self.x + 2, self.y + 1, 10, fg)
                sel_width = _measure_text(pre_text, 10)
                _rl.draw_rectangle(
                    self.x + 2 + sel_width,
                    self.y + 1,
                    _measure_text(sel_text, 10),
                    10,
                    _rl.Color(102, 191, 255, 128),
                )
                _rl.draw_text(sel_text, self.x + 2 + sel_width, self.y + 1, 10, fg)
                _rl.draw_text(
                    post_text,
                    self.x + 2 + sel_width + _measure_text(sel_text, 10),
                    self.y + 1,
                    10,
                    fg,
                )
            else:
                _rl.draw_text(self.value, self.x + 2, self.y + 1, 10, fg)
                if self.selected and round(_rl.get_time()) % 2 == 0:
                    cursor_x = (
                        self.x + 2 + _measure_text(self.value[: self.cursor + 1], 10)
                    )
                    _rl.draw_rectangle(
                        cursor_x, self.y + 1, 2, 10, fg
                    )  # Thicker cursor line
        _rl.draw_rectangle_lines_ex(
            [self.x, self.y, self.w, self.vh],
            1,
            fg,
        )
        GUIState.Widgets[f"ti_{id}"].value = self.value
        GUIState.Widgets[f"ti_{id}"].selected = self.selected
        GUIState.Widgets[f"ti_{id}"].cursor = self.cursor
        GUIState.Widgets[f"ti_{id}"].selection_start = self.selection_start


class slider_vec2(Widget):
    def __init__(
        self, w: int, h: int, label: str, id: str, sens: float = 0.005, default=[0, 0]
    ):
        """2D vector slider widget for X/Y coordinate input.

        Args:
            w (int): Width of the slider
            h (int): Height of the slider
            label (str): Label text
            id (str): Unique identifier
            sens (float, optional): Mouse sensitivity. Defaults to 0.005.
            default (list, optional): Default [x,y] values. Defaults to [0,0].
        """
        self.id = id
        if f"sl2d_{id}" in GUIState.Widgets:
            self.obj = GUIState.Widgets[f"sl2d_{id}"]
        else:
            self.obj = sliderInfo2D(default, False)
            GUIState.Widgets[f"sl2d_{id}"] = self.obj
        value = [self.obj.x, self.obj.y]
        self.x = value[0]
        self.y = value[1]
        if curwindow.collapsed:
            return
        pressed = self.obj.pressed
        if super().__init__(winx, winy, w, h):
            self = None
            return
        mpd = _rl.get_mouse_delta()
        bg = _rl.Color(128, 128, 128, 64)
        fg = _rl.Color(255, 255, 255, 255)
        if not curwindow.h < self.y + 5:
            if _rl.check_collision_point_rec(
                self.mp, [self.x + self.off.x, self.y + self.off.y, self.w, self.vh]
            ):
                bg = _rl.Color(128, 128, 128, 128)
                if _rl.is_mouse_button_pressed(0):
                    GUIState.SelectedWidget = GUIState.Curwidget
                    pressed = True
        if _rl.is_mouse_button_up(0):
            pressed = False
        if Widget.getpressed():
            pressed = True
        _rl.draw_rectangle(self.x, self.y, self.w, self.vh, bg)
        _rl.draw_rectangle_lines_ex([self.x, self.y, self.w, self.vh], 1, fg)
        _rl.draw_text(
            f"{label}:\n{float(value[0]):.5}\n{float(value[1]):.5}",
            self.x + 1,
            self.y + 1,
            10,
            fg,
        )
        if pressed:
            fg = (102, 191, 255, 255)
            value[0] += mpd.x * sens
            value[1] += mpd.y * sens
            _rl.set_mouse_position(
                int(self.x + self.off.x + w / 2), int(self.y + self.off.y + h / 2)
            )
            value[0] = round(value[0], 3)
            value[1] = round(value[1], 3)
        self.x = value[0]
        self.y = value[1]
        GUIState.Widgets[f"sl2d_{id}"].pressed = pressed
        GUIState.Widgets[f"sl2d_{id}"].x = value[0]
        GUIState.Widgets[f"sl2d_{id}"].y = value[1]

    def limit(self, mini=None, maxi=None):
        id = self.id
        value = [GUIState.Widgets[f"sl2d_{id}"].x, GUIState.Widgets[f"sl2d_{id}"].y]
        if mini is not None:
            if value[0] < mini:
                value[0] = mini
            if value[1] < mini:
                value[1] = mini
        if maxi is not None:
            if value[0] > maxi:
                value[0] = maxi
            if value[1] > maxi:
                value[1] = maxi
        GUIState.Widgets[f"sl2d_{id}"].x = value[0]
        GUIState.Widgets[f"sl2d_{id}"].y = value[1]
        return self


class slider(Widget):
    def __init__(self, w, label, id, sens=0.005, pressed=False, default=0):
        """Single value slider widget for numeric input.

        Args:
            w (int): Width of the slider
            label (str): Label text
            id (str): Unique identifier
            sens (float, optional): Mouse sensitivity. Defaults to 0.005.
            pressed (bool, optional): Initial pressed state. Defaults to False.
            default (int, optional): Default value. Defaults to 0.
        """
        self.id = id
        if f"sl_{id}" in GUIState.Widgets:
            self.obj = GUIState.Widgets[f"sl_{id}"]
        else:
            self.obj = sliderInfo(default, False)
            GUIState.Widgets[f"sl_{id}"] = self.obj
        value = self.obj.value
        pressed = self.obj.pressed
        textactive = self.obj.textactive
        self.value = value
        self.pressed = pressed
        self.textactive = textactive
        if curwindow.collapsed:
            return
        if super().__init__(winx, winy, w, 12):
            self = None
            return
        mpd = _rl.get_mouse_delta()
        bg = _rl.Color(128, 128, 128, 64)
        fg = _rl.Color(255, 255, 255, 255)
        if not curwindow.h < self.y + 5:
            if _rl.check_collision_point_rec(
                self.mp, [self.x + self.off.x, self.y + self.off.y, self.w, self.vh]
            ):
                bg = _rl.Color(128, 128, 128, 128)
                if _rl.is_mouse_button_pressed(0):
                    pressed = True
                    GUIState.SelectedWidget = GUIState.Curwidget
                if _rl.is_mouse_button_pressed(2):
                    textactive = not textactive
        if _rl.is_mouse_button_up(0):
            pressed = False
        if Widget.getpressed():
            pressed = True
        _rl.draw_rectangle(self.x, self.y, self.w, self.vh, bg)
        _rl.draw_rectangle_lines_ex([self.x, self.y, self.w, self.vh], 1, fg)
        _rl.draw_text(f"{label}:", self.x + 1, self.y + 1, 10, fg)
        _rl.draw_text(
            f"{float(value):.5}",
            self.x + w - _measure_text(f"{float(value):.5}", 10) - 3,
            self.y + 1,
            10,
            fg,
        )
        if pressed:
            fg = (102, 191, 255, 255)
            value += mpd.x * sens
            value = round(value, 3)
            dt = _rl.get_frame_time() * 60
            _rl.set_mouse_position(
                int(self.x + self.off.x + w / 2), int(self.y + self.off.y + 6)
            )
        self.value = value
        GUIState.Widgets[f"sl_{id}"].pressed = pressed
        GUIState.Widgets[f"sl_{id}"].value = value
        GUIState.Widgets[f"sl_{id}"].textactive = textactive

    def limit(self, mini=None, maxi=None):
        id = self.id
        value = GUIState.Widgets[f"sl_{id}"].value
        if mini is not None:
            if value < mini:
                value = mini
        if maxi is not None:
            if value > maxi:
                value = maxi
        GUIState.Widgets[f"sl_{id}"].value = value
        self.value = value
        return self


class solidcolor(Widget):
    def __init__(self, w, h, color, border=False):
        """Solid color rectangle widget.

        Args:
            w (int): Width of rectangle
            h (int): Height of rectangle
            color (list): RGB color values [r,g,b]
            border (bool, optional): Draw border around rectangle. Defaults to False.
        """
        if curwindow.collapsed:
            return
        if super().__init__(winx, winy, w, h):
            return
        _rl.draw_rectangle(self.x, self.y, self.w, self.vh, color)
        if border:
            _rl.draw_rectangle_lines_ex(
                [self.x, self.y, self.w, self.vh],
                1,
                [color.r // 2, color.g // 2, color.b // 2, 255],
            )


class colorpicker(Widget):
    def __init__(self, id, default=[0, 0, 0]):
        """RGB color picker widget with sliders.

        Args:
            id (str): Unique identifier
            default (list, optional): Default RGB color values. Defaults to [0,0,0].
        """
        self.id = id
        if f"cp_{id}" in GUIState.Widgets:
            self.obj = GUIState.Widgets[f"cp_{id}"]
        else:
            self.obj = colorInfo(default, False)
            GUIState.Widgets[f"cp_{id}"] = self.obj
        value = [self.obj.r, self.obj.g, self.obj.b]
        pickeractive = self.obj.pickeractive
        self.value = _rl.Color(value[0], value[1], value[2], 255)
        if curwindow.collapsed:
            return
        if super().__init__(winx, winy, 15 + (55) * 3, 12):
            return
        value[0] = round(
            slider(50, "R", id + "r", 1, default=default[0]).limit(0, 255).value
        )
        sameline()
        value[1] = round(
            slider(50, "G", id + "g", 1, default=default[1]).limit(0, 255).value
        )
        sameline()
        value[2] = round(
            slider(50, "B", id + "b", 1, default=default[2]).limit(0, 255).value
        )
        sameline()
        sc = solidcolor(12, 12, _rl.Color(value[0], value[1], value[2], 255), True)
        self.value = _rl.Color(value[0], value[1], value[2], 255)
        GUIState.Widgets[f"cp_{id}"].r = value[0]
        GUIState.Widgets[f"cp_{id}"].g = value[1]
        GUIState.Widgets[f"cp_{id}"].b = value[2]


class image(Widget):
    def __init__(self, w: int, h: int, fp: str, source: list = None):
        """Image display widget.

        Args:
            w (int): Width to display image
            h (int): Height to display image
            fp (str): File path to image
            source (list, optional): Source rectangle [x,y,w,h]. Defaults to None for full image.
        """
        image = _cached_image(fp)
        if curwindow.collapsed:
            return
        if super().__init__(winx, winy, w, h):
            self = None
            return
        if source == None:
            source = [0, 0, image.width, image.height]
        _rl.draw_texture_pro(
            image,
            source,
            [self.x, self.y, w, self.h],
            [0, 0],
            0,
            _rl.Color(255, 255, 255, 255),
        )


class collheadInfo:
    def __init__(self, collapsed, wincollapsed, indent, startx, starty):
        self.collapsed = collapsed
        self.wincollapsed = wincollapsed
        self.oldindent = indent
        self.startx = startx
        self.starty = starty


class collapsing_header(Widget):
    def __init__(self, w, label, id, collapsed=True, indentation=5):
        """Collapsible section header widget.

        Args:
            w (int): Width of header
            label (str): Header text
            id (str): Unique identifier
            collapsed (bool, optional): Initial collapsed state. Defaults to True.
            indentation (int, optional): Child widget indent pixels. Defaults to 5.
        """
        self.id = id
        self.w = w
        self.label = label
        self.indent = indent + indentation
        self.oldindent = indent
        self.id = id
        self.wincollapsed = curwindow.collapsed
        if f"ch_{id}" in GUIState.Widgets:
            self.obj = GUIState.Widgets[f"ch_{id}"]
            self.collapsed = self.obj.collapsed
            self.oldindent = self.obj.oldindent
        else:
            self.collapsed = collapsed
            self.oldindent = indent
        self.obj = collheadInfo(self.collapsed, self.wincollapsed, self.oldindent, 0, 0)
        GUIState.Widgets[f"ch_{id}"] = self.obj

        if self.collapsed:
            curwindow.collapsed = True

    def show(self):
        """Displays the header."""
        self.startx = winx
        self.starty = winy
        if curwindow.collapsed and self.wincollapsed:
            return False
        if super().__init__(winx, winy, self.w, 15):
            self = None
            return
        if not curwindow.h < self.y + 5:
            if _rl.is_mouse_button_pressed(0):
                if _rl.check_collision_point_rec(
                    self.mp, [self.x + self.off.x, self.y + self.off.y, self.w, self.vh]
                ):
                    self.obj.collapsed = not self.obj.collapsed
                    GUIState.SelectedWidget = GUIState.Curwidget
        color = _rl.Color(0 if not self.collapsed else 255, 255, 255, 255)
        if GUIState.SelectedWidget == GUIState.Curwidget:
            color = _rl.Color(102, 191, 255, 255)
        if Widget.getpressed():
            self.obj.collapsed = not self.obj.collapsed
        _rl.draw_rectangle(
            self.x,
            self.y,
            self.w,
            self.vh,
            [color.r // 2, color.g // 2, color.b // 2, 255],
        )
        _rl.draw_rectangle_lines_ex([self.x, self.y, self.w, self.vh], 1, color)
        _rl.draw_text(
            self.label, self.x + 3, self.y + 3, 10, _rl.Color(255, 255, 255, 255)
        )
        _rl.gui_draw_icon(
            115 if self.collapsed else 116,
            self.x + self.w - 16,
            self.y - 1,
            1,
            _rl.Color(255, 255, 255, 255),
        )
        GUIState.Widgets[f"ch_{id}"] = collheadInfo(
            self.collapsed, self.wincollapsed, self.oldindent, self.startx, self.starty
        )
        if self.collapsed:
            return False
        set_indent(self.indent)
        return True


def reset_collapsing_header(id: str):
    """Resets the collapsing header to its original state.

    Args:
        id (str): collapsing header identifier
    """
    self = GUIState.Widgets[f"ch_{id}"]
    _rl.draw_line(
        self.startx + 1,
        self.starty + 15,
        self.startx + 1,
        winy - 1 + curwindow.scroll_y,
        _rl.Color(0, 255, 255, 255),
    )
    curwindow.collapsed = self.wincollapsed
    winx = self.oldindent
    lastwinxchange.append(self.oldindent)
    GUIState.Widgets[f"ch_{id}"] = self
    set_indent(self.oldindent)


class checkbox_button(Widget):
    def __init__(self, label, id, value=False):
        """Checkbox toggle button widget.

        Args:
            label (str): Label text
            id (str): Unique identifier
            value (bool, optional): Initial checked state. Defaults to False.
        """
        self.id = id
        self.label = label
        self.value = value
        if f"cb_{id}" in GUIState.Widgets:
            self.obj = GUIState.Widgets[f"cb_{id}"]
            self.value = self.obj.value
        else:
            GUIState.Widgets[f"cb_{id}"] = self
        if curwindow.collapsed:
            return
        if super().__init__(winx, winy, 12 + _measure_text(label, 10), 12):
            self = None
            return

        if self.value:
            self.color = _rl.Color(0, 255, 255, 255)
        else:
            self.color = _rl.Color(128, 128, 128, 255)
        if not curwindow.h < self.y + 5:
            if _rl.is_mouse_button_pressed(0):
                if _rl.check_collision_point_rec(
                    self.mp, [self.x + self.off.x, self.y + self.off.y, self.w, self.vh]
                ):
                    self.value = not self.value
                    GUIState.SelectedWidget = GUIState.Curwidget
        if Widget.getpressed():
            self.value = not self.value
        _rl.draw_rectangle(self.x, self.y + 1, 10, 10, self.color)
        _rl.draw_rectangle_lines_ex(
            [self.x, self.y + 1, 10, 10], 1, _rl.Color(0, 255, 255, 255)
        )
        if GUIState.get_is_current():
            _rl.draw_rectangle_lines_ex(
                [self.x, self.y, self.w, self.h], 1, _rl.Color(255, 255, 255, 255)
            )
        _rl.draw_text(
            self.label, self.x + 12, self.y + 1, 10, _rl.Color(255, 255, 255, 255)
        )
        GUIState.Widgets[f"cb_{id}"] = self
