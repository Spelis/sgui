import string
import pyray as _rl
import inspect,datetime


class GUIState:
    Keyboard = []
    Mouse = []
    MouseWheel = False
    def get_window():
        if curwindow == None:
            raise Exception("you cant draw outside of a window")
        return curwindow
    Widgets = {}
    SpecialWindows = {}
    
_textmeasurecache = {}
    
def _measure_text(text,fs):
    key = (text,fs)
    if key not in _textmeasurecache:
        _textmeasurecache[key] = _rl.measure_text(text,fs)
    return _textmeasurecache[key]
    

def set_indent(value):
    global indent
    indent = value
    
def lerp(a,b,t):
    t *= _rl.get_frame_time()*30
    return a+(b-a)*t

global curwindow,winy,lastwinychange,winx,lastwinxchange,indent

def init():
    global curwindow,winy,lastwinychange,winx,lastwinxchange,indent
    indent = 0
    curwindow = None
    winy,lastwinychange,winx,lastwinxchange = 0,[],0,[]
    
def sameline():
    global winy, winx, lastwinxchange, lastwinychange, curwindow
    if len(lastwinxchange) == 0 or len(lastwinychange) == 0:
        return
    winy -= lastwinychange[-1]
    winx = lastwinxchange[-1]-curwindow.scroll_x

def cancel_sameline():
    global winy, lastwinychange,winx
    winy += lastwinychange[-1]
    winx = indent
    
def _log(text):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {text}")
    
def _get_class_name(depth=2):
    """Gets the class name of the caller.

    Args:
        depth (int, optional): stack depth. Defaults to 2.

    Returns:
        str: class name
    """
    caller_frame = inspect.stack()[depth][0] # this function gets called
    caller_locals = caller_frame.f_locals
    if 'self' in caller_locals:
        return str(caller_locals['self'].__class__.__name__)
    return str("")

class Window:
    def __init__(self,x,y,w,h,title,collapsed=False,resizable=True,movable=True,titlecolor=_rl.Color(0,255,255,255),scrollable=True):
        self.x = x
        self.y = y
        self.w = w+20
        self.h = h+30
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
        self.wintex = _rl.load_render_texture(1,1)
        self.scroll_x = 0
        self.scroll_y = 0
        self.scroll_x_float = 0
        self.scroll_y_float = 0
        self.realscroll_x = 0
        self.realscroll_y = 0
        self.maxscroll_x = 0
        self.titlebar = True
        self.titlebar_height = 15
        
    def __repr__(self):
        return f"<{'collapsed' if self.collapsed else 'expanded'} Window {self.title} [{self.x}, {self.y}, {self.w}, {self.h}]>"

    def __enter__(self):
        global curwindow,wintex,winy,lastwinychange,lastwinxchange
        curwindow = None
        _rl.unload_render_texture(self.wintex)
        self.wintex = _rl.load_render_texture(self.w,self.h)
        _rl.begin_texture_mode(self.wintex)
        _rl.set_trace_log_level(_rl.TraceLogLevel.LOG_NONE)
        if not self.collapsed:
            _rl.draw_rectangle(0,0,self.w,self.h,_rl.Color(20,20,20,255))
        curwindow = self
        winy = 1
        self.maxscroll_x = 1
        lastwinxchange = []
        lastwinychange = []

    def __exit__(self,*args):
        if self.titlebar:
            self.titlebar_height = 15
        else:
            self.titlebar_height = 0
        global curwindow,winy
        if not self.collapsed:
            _rl.draw_rectangle_lines_ex([0,self.titlebar_height,self.w,self.h-self.titlebar_height],5,_rl.Color(20,20,20,255))
            _rl.draw_rectangle_lines_ex([0,0,self.w,self.h],1,_rl.Color(40,40,40,255))
        if not self.collapsed:
            triangleh = self.h
            trianglec = _rl.Color(40,40,40,255)
        else:
            triangleh = 15
            trianglec = _rl.Color(0,255,255,255)
        if self.resizable:
            _rl.draw_triangle([0+self.w,0+triangleh],[0+self.w,0+triangleh-10],[0+self.w-10,0+triangleh],trianglec)
        mp = _rl.get_mouse_position()
        mpd = _rl.get_mouse_delta()
        dt = _rl.get_frame_time()*60
        if self.scrollable:
            if winy > self.h - (self.titlebar_height*2):
                scroll_height = max(30, (self.h / winy) * (self.h-(self.titlebar_height*2)))
                scroll_pos = (-self.scroll_y / max(winy, self.h)) * (self.h-(self.titlebar_height*2))
                _rl.draw_rectangle(self.w - 2, round(scroll_pos+self.titlebar_height), 2, round(scroll_height), _rl.Color(60,60,60,255))
                
                if _rl.check_collision_point_rec(mp, [self.x + self.w - 2, self.y + scroll_pos + self.titlebar_height, 2, scroll_height]):
                    if _rl.is_mouse_button_down(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                        self.realscroll_y += mpd.y * (winy / self.h)

            if self.maxscroll_x > self.w - 20:
                scroll_width = max(30, (self.w / self.maxscroll_x) * (self.w-20))
                scroll_pos = (-self.scroll_x / max(self.maxscroll_x, self.w)) * (self.w-20)
                _rl.draw_rectangle(round(scroll_pos), self.h - 2, round(scroll_width), 2, _rl.Color(60,60,60,255))
                
                if _rl.check_collision_point_rec(mp, [self.x + scroll_pos, self.y + self.h - 2, scroll_width, 2]):
                    if _rl.is_mouse_button_down(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                        self.realscroll_x += mpd.x * (self.maxscroll_x / self.w)


            
        # Update max horizontal scroll limit
        max_scroll_x = -(max(0, self.maxscroll_x - self.w + 20))
        if self.realscroll_x < max_scroll_x:
            self.realscroll_x = max_scroll_x        
        if self.titlebar:
            _rl.draw_rectangle(0,0,self.w,self.titlebar_height,_rl.Color(self.titlecolor.r//2,self.titlecolor.g//2,self.titlecolor.b//2,255))
            _rl.draw_rectangle_lines_ex([0,0,self.w,self.titlebar_height],1,self.titlecolor)
            _rl.draw_rectangle_rec([2,2,11,11],self.titlecolor)
            _rl.draw_text(self.title,self.titlebar_height,2,10,_rl.WHITE)
            if _rl.is_mouse_button_pressed(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                if _rl.check_collision_point_rec(mp, [self.x+3,self.y+3,10,10]):
                    self.collapsed = not self.collapsed
        mwm = _rl.get_mouse_wheel_move_v().y
        if self.scrollable:
            if _rl.check_collision_point_rec(mp, [self.x,self.y,self.w,self.h]):
                if _rl.is_key_down(_rl.KeyboardKey.KEY_LEFT_SHIFT):
                    self.realscroll_x += round(mwm*20)
                else:
                    self.realscroll_y += round(mwm*20)
        if self.realscroll_y > 0:
            self.realscroll_y = 0
        if self.realscroll_x > 0:
            self.realscroll_x = 0
        max_scroll = -(max(0, winy - self.h + (self.titlebar_height*2)))
        if self.realscroll_y < max_scroll:
            self.realscroll_y = max_scroll
        if self.realscroll_x < max_scroll_x:
            self.realscroll_x = max_scroll_x
        self.scroll_x_float = lerp(self.scroll_x_float, self.realscroll_x, 0.9)
        self.scroll_y_float = lerp(self.scroll_y_float, self.realscroll_y, 0.9)
        self.scroll_x = round(self.scroll_x_float)
        self.scroll_y = round(self.scroll_y_float)        
        if _rl.is_mouse_button_pressed(_rl.MouseButton.MOUSE_BUTTON_LEFT):
            if (not self.resizing) and self.movable:
                if self.titlebar:
                    if _rl.check_collision_point_rec(mp, [self.x,self.y,self.w,15]) or self.dragging:
                        self.dragging = True
            if self.resizable and not self.collapsed:
                if _rl.check_collision_point_rec(mp, [self.x+self.w-10,self.y+triangleh-10,10,10]) or self.resizing:
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
        _rl.draw_texture_pro(self.wintex.texture, [0,0,self.wintex.texture.width,-self.wintex.texture.height],[self.x,self.y,self.wintex.texture.width,self.wintex.texture.height], [0,0],0,_rl.Color(255,255,255,255))
        winy = 0
        self.widgetid = 0
        curwindow = None
        
    def gethover(self):
        mp = _rl.get_mouse_position()
        if _rl.check_collision_point_rec(mp, [self.x,self.y,self.w,self.h]):
            return True
        return False


class Widget:
    def __init__(self,x,y,w,h,*args):
        global winy,winx,lastwinxchange,lastwinychange,indent
        cw = curwindow
        self.x = x+cw.scroll_x
        self.y = y+cw.scroll_y
        self.vy = max(0, y+cw.scroll_y+20)  # Add titlebar height check
        self.w = w
        self.h = h
        self.y += 20
        self.x += 5
        self.off = _rl.Vector2(cw.x,cw.y)
        self.w = min(w,cw.w-10-winx-cw.scroll_x)
        self.vh = min(h,cw.h-25-winy-cw.scroll_y)
        if self.vy > cw.titlebar_height:  # Add top cutoff check
            self.vh = min(self.vh, self.y - self.vy + h)
        self.mp = _rl.get_mouse_position()
        xs = x+w
        if xs > cw.maxscroll_x:
            cw.maxscroll_x = xs
        winy += self.h+3
        lastwinychange.append(self.h+3)
        lastwinxchange.append(self.x+w+5)
        winx = indent
        if self.y > cw.h:
            return True
        #_log(f"Widget: {_get_class_name()} at {self.x},{self.y} by {self.w}x{self.h}")
        return False


class button(Widget):
    def __init__(self,w,label):
        self.pressed = False
        self.held = False
        if curwindow.collapsed:
            return
        if super().__init__(winx,winy,w,12):
            self = None
            return
        color = _rl.Color(128,128,128,0)
        fg = _rl.Color(255,255,255,255)
        if not curwindow.h < self.y+5:
            if _rl.check_collision_point_rec(self.mp, [self.x+self.off.x,self.vy+self.off.y,self.w,self.vh]):
                color.a = 128
                if _rl.is_mouse_button_down(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                    fg = (102,191,255,255)
                    self.held = True
                if _rl.is_mouse_button_released(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                    self.pressed = True
        _rl.draw_rectangle(self.x,self.vy,self.w,self.vh,color)
        _rl.draw_rectangle_lines_ex([self.x,self.vy,self.w,self.vh],1,fg)
        _rl.draw_text(label,self.x+2,self.y+1,10,fg)

class button_img(Widget):
    def __init__(self,w,h,image,source=None):
        self.pressed = False
        self.held = False
        if curwindow.collapsed:
            self = None
            return
        if super().__init__(winx,winy,w,h):
            self = None
            return
        if source is None:
            source = [0,0,image.width,image.height]
        color = _rl.Color(128,128,128,0)
        fg = _rl.Color(255,255,255,255)
        if _rl.check_collision_point_rec(self.mp, [self.x+self.off.x,self.y+self.off.y,self.w,self.h]):
            color.a = 128
            if _rl.is_mouse_button_down(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                fg = _rl.Color(102,191,255,255)
                self.held = True
            if _rl.is_mouse_button_released(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                self.pressed = True
        _rl.draw_rectangle(self.x,self.y,self.w,self.h,color)
        _rl.draw_texture_pro(image,source,[self.x,self.y,w,self.h],[0,0],0,_rl.Color(255,255,255,255))
        _rl.draw_rectangle_lines_ex([self.x,self.y,self.w,self.vh],1,fg)

class label(Widget):
    def __init__(self,text):
        if curwindow.collapsed:
            return
        w = _measure_text(text,10)
        h = (12 * (text.count('\n')+1))
        if super().__init__(winx,winy,w,h):
            self = None
            return
        _rl.draw_text(text,round(self.x),round(self.y),10,_rl.Color(255,255,255,255))
        
class sliderInfo:
    def __init__(self,value,pressed=False):
        self.value = value
        self.pressed = pressed
        self.textactive = False
    def __int__(self):
        return self.value
    
class colorInfo:
    def __init__(self,value,pickeractive=False):
        self.r = value[0]
        self.g = value[1]
        self.b = value[2]
        self.pickeractive = pickeractive
    def __int__(self):
        return (self.r,self.g,self.b,self.a)

class sliderInfo2D:
    def __init__(self,value,pressed=False):
        self.x = value[0]
        self.y = value[1]
        self.pressed = pressed

class TextInput:
    def __init__(self,value="",selected=False,cursor=-1,selection_start=-1):
        self.value = value
        self.selected = selected
        self.cursor = len(value)-1
        self.selection_start = selection_start
        
class textinput(Widget):
    def __init__(self,w:int,label:str,id:str,default="") -> TextInput:
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
        if super().__init__(winx,winy,w,12):
            self = None
            return
        self.w = max(self.w, _measure_text(self.value+" ",10)+5)
        if not curwindow.h < self.y+5:
            if _rl.check_collision_point_rec(self.mp, [self.x+self.off.x, self.y+self.off.y, self.w, self.vh]):
                bg.a = 128
                if _rl.is_mouse_button_down(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                    fg = _rl.Color(102, 191, 255, 255)
                    click_pos = self.mp.x - (self.x + self.off.x)
                    self.cursor = min(len(self.value), max(0, int(click_pos / 6)))
                    if not _rl.is_key_down(_rl.KeyboardKey.KEY_LEFT_SHIFT):
                        self.selection_start = self.cursor
                if _rl.is_mouse_button_released(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                    self.selected = True
            else:
                if _rl.is_mouse_button_down(_rl.MouseButton.MOUSE_BUTTON_LEFT):
                    self.selected = False
        _rl.draw_rectangle(self.x,self.y,self.w,self.vh,bg)
        if self.selected:
            GUIState.Keyboard += (string.ascii_letters + string.digits + string.punctuation).split()
            GUIState.Keyboard.append("Backspace")
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
                    self.value = self.value[:self.cursor+1] + charstr + self.value[self.cursor+1:]
                    self.cursor += 1
                self.selection_start = self.cursor
                
            if _rl.is_key_pressed(_rl.KeyboardKey.KEY_BACKSPACE) or _rl.is_key_pressed_repeat(_rl.KeyboardKey.KEY_BACKSPACE):
                if self.selection_start != self.cursor:
                    start = min(self.selection_start, self.cursor)
                    end = max(self.selection_start, self.cursor)
                    self.value = self.value[:start] + self.value[end:]
                    self.cursor = start
                    self.selection_start = start
                elif self.cursor >= 0:
                    self.value = self.value[:self.cursor] + self.value[self.cursor+1:]
                    self.cursor = max(0, self.cursor - 1)
                    self.selection_start = self.cursor
            
        if self.value == "":
            fg.a = 128
            _rl.draw_text(label,self.x+2,self.y+1,10,fg)
            fg.a = 255
            _rl.draw_text(("_" if round(_rl.get_time())%2 == 0 and self.selected else ""),self.x+2,self.y+1,10,fg)
        else:
            if self.selection_start != self.cursor:
                start = min(self.selection_start, self.cursor)
                end = max(self.selection_start, self.cursor)
                pre_text = self.value[:start]
                sel_text = self.value[start:end]
                post_text = self.value[end:]
                
                _rl.draw_text(pre_text,self.x+2,self.y+1,10,fg)
                sel_width = _measure_text(pre_text,10)
                _rl.draw_rectangle(self.x+2+sel_width,self.y+1,_measure_text(sel_text,10),10,_rl.Color(102,191,255,128))
                _rl.draw_text(sel_text,self.x+2+sel_width,self.y+1,10,fg)
                _rl.draw_text(post_text,self.x+2+sel_width+_measure_text(sel_text,10),self.y+1,10,fg)
            else:
                _rl.draw_text(self.value,self.x+2,self.y+1,10,fg)
                if self.selected and round(_rl.get_time())%2 == 0:
                    cursor_x = self.x+2+_measure_text(self.value[:self.cursor+1],10)
                    _rl.draw_text("_",cursor_x,self.y+1,10,fg)
                    
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
    def __init__(self,w:int,h:int,label:str,id:str,sens:float=0.005,default=[0,0]):
        self.id = id
        if f"sl2d_{id}" in GUIState.Widgets:
            self.obj = GUIState.Widgets[f"sl2d_{id}"]
        else:
            self.obj = sliderInfo2D(default,False)
            GUIState.Widgets[f"sl2d_{id}"] = self.obj
        value = [self.obj.x,self.obj.y]
        self.x = value[0]
        self.y = value[1]
        if curwindow.collapsed:
            return
        pressed = self.obj.pressed
        if super().__init__(winx,winy,w,h):
            self = None
            return
        mpd = _rl.get_mouse_delta()
        bg =  _rl.Color(128, 128, 128, 64)
        fg = _rl.Color(255, 255, 255, 255)
        if not curwindow.h < self.y+5:
            if _rl.check_collision_point_rec(self.mp, [self.x+self.off.x,self.y+self.off.y,self.w,self.vh]):
                bg = _rl.Color(128,128,128,128)
                if _rl.is_mouse_button_pressed(0):
                    pressed = True
        if _rl.is_mouse_button_up(0):
            pressed = False
        _rl.draw_rectangle(self.x, self.y, self.w, self.vh, bg)
        _rl.draw_rectangle_lines_ex([self.x,self.y,self.w,self.vh],1,fg)
        _rl.draw_text(f"{label}:\n{float(value[0]):.5}\n{float(value[1]):.5}",self.x+1,self.y+1,10,fg)
        if pressed:
            fg = (102, 191, 255, 255)
            value[0] += mpd.x*sens
            value[1] += mpd.y*sens
            _rl.set_mouse_position(int(self.x+self.off.x+w/2),int(self.y+self.off.y+h/2))
            value[0] = round(value[0],3)
            value[1] = round(value[1],3)
        self.x = value[0]
        self.y = value[1]
        GUIState.Widgets[f"sl2d_{id}"].pressed = pressed
        GUIState.Widgets[f"sl2d_{id}"].x = value[0]
        GUIState.Widgets[f"sl2d_{id}"].y = value[1]
    def limit(self,mini=None,maxi=None):
        id = self.id
        value =[GUIState.Widgets[f"sl2d_{id}"].x,GUIState.Widgets[f"sl2d_{id}"].y]
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
    def __init__(self,w,label,id,sens=0.005,pressed=False,default=0):
        self.id = id
        if f"sl_{id}" in GUIState.Widgets:
            self.obj = GUIState.Widgets[f"sl_{id}"]
        else:
            self.obj = sliderInfo(default,False)
            GUIState.Widgets[f"sl_{id}"] = self.obj
        value = self.obj.value
        pressed = self.obj.pressed
        textactive = self.obj.textactive
        self.value = value
        self.pressed = pressed
        self.textactive = textactive
        if curwindow.collapsed:
            return
        if super().__init__(winx,winy,w,12):
            self = None
            return
        mpd = _rl.get_mouse_delta()
        bg =  _rl.Color(128, 128, 128, 64)
        fg = _rl.Color(255, 255, 255, 255)
        pressed = pressed
        if not curwindow.h < self.y+5:
            if _rl.check_collision_point_rec(self.mp, [self.x+self.off.x, self.y+self.off.y, self.w, self.vh]):
                bg = _rl.Color(128,128,128,128)
                if _rl.is_mouse_button_pressed(0):
                    pressed = True
                if _rl.is_mouse_button_pressed(2):
                    textactive = not textactive
        if _rl.is_mouse_button_up(0):
            pressed = False
        _rl.draw_rectangle(self.x, self.y, self.w, self.vh, bg)
        _rl.draw_rectangle_lines_ex([self.x,self.y,self.w,self.vh],1,fg)
        _rl.draw_text(f"{label}:",self.x+1,self.y+1,10,fg)
        _rl.draw_text(f"{float(value):.5}",self.x+w-_measure_text(f"{float(value):.5}",10)-3,self.y+1,10,fg)
        if pressed:
            fg = (102, 191, 255, 255)
            value += mpd.x*sens
            value = round(value,3)
            dt = _rl.get_frame_time()*60
            _rl.set_mouse_position(int(self.x+self.off.x+w/2),int(self.y+self.off.y+6))
        self.value = value
        GUIState.Widgets[f"sl_{id}"].pressed = pressed
        GUIState.Widgets[f"sl_{id}"].value = value
        GUIState.Widgets[f"sl_{id}"].textactive = textactive
    def limit(self,mini=None,maxi=None):
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
    def __init__(self,w,h,color,border=False):
        if curwindow.collapsed:
            return
        if super().__init__(winx,winy,w,h):
            return
        _rl.draw_rectangle(self.x,self.y,self.w,self.vh,color)
        if border: _rl.draw_rectangle_lines_ex([self.x,self.y,self.w,self.vh],1,[color.r//2,color.g//2,color.b//2,255])
    
class colorpicker(Widget):
    def __init__(self,id,pressed=False,default=[0,0,0]):
        self.id = id
        if f"cp_{id}" in GUIState.Widgets:
            self.obj = GUIState.Widgets[f"cp_{id}"]
        else:
            self.obj = colorInfo(default,False)
            GUIState.Widgets[f"cp_{id}"] = self.obj
        value = [self.obj.r,self.obj.g,self.obj.b]
        pickeractive = self.obj.pickeractive
        self.value = _rl.Color(value[0],value[1],value[2],255)
        if curwindow.collapsed:
            return
        if super().__init__(winx,winy,15+(55)*3,12):
            return
        value[0] = round(slider(50,"R",id+"r",1,default=default[0]).limit(0,255).value)
        sameline()
        value[1] = round(slider(50,"G",id+"g",1,default=default[1]).limit(0,255).value)
        sameline()
        value[2] = round(slider(50,"B",id+"b",1,default=default[2]).limit(0,255).value)
        sameline()
        sc = solidcolor(12,12,_rl.Color(value[0],value[1],value[2],255),True)
        if not curwindow.h < sc.y+sc.h:
            if _rl.check_collision_point_rec(self.mp, [sc.x+self.off.x,sc.y+self.off.y,sc.w,sc.h]):
                if _rl.is_mouse_button_released(0):
                    pickeractive = not pickeractive
        self.value = _rl.Color(value[0],value[1],value[2],255)
        GUIState.Widgets[f"cp_{id}"].pickeractive = pickeractive
        GUIState.Widgets[f"cp_{id}"].r = value[0]
        GUIState.Widgets[f"cp_{id}"].g = value[1]
        GUIState.Widgets[f"cp_{id}"].b = value[2]
        

class image(Widget):
    def __init__(self,w,h,image,source=None):
        if curwindow.collapsed:
            return
        if super().__init__(winx,winy,w,h):
            self = None
            return
        if source == None:
            source = [0,0,image.width,image.height]
        _rl.draw_texture_pro(image,source,[self.x,self.y,w,self.h],[0,0],0,_rl.Color(255,255,255,255))

class collheadInfo:
    def __init__(self,collapsed,wincollapsed,indent,startx,starty):
        self.collapsed = collapsed
        self.wincollapsed = wincollapsed
        self.oldindent = indent
        self.startx = startx
        self.starty = starty

class collapsing_header(Widget):
    def __init__(self,w,label,id,collapsed = True,indentation=5):
        """Collapsing header widget. allows the user to collapse and expand widgets.

        Args:
            w (int): width of the widget
            label (str): label of the widget
            id (str): identifier for the widget
            collapsed (bool, optional): start of collapsed or expanded. Defaults to True.
            indentation (int, optional): amount to push widgets inside of the header to the right. Defaults to 5.
        """
        self.id = id
        self.w = w
        self.label = label
        self.indent = indent+indentation
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
        self.obj = collheadInfo(self.collapsed,self.wincollapsed,self.oldindent,0,0)
        GUIState.Widgets[f"ch_{id}"] = self.obj
            
        if self.collapsed:
            curwindow.collapsed = True
    def show(self):
        self.startx = winx
        self.starty = winy
        if curwindow.collapsed and self.wincollapsed:
            return False
        if super().__init__(winx,winy,self.w,15):
            self = None
            return
        _rl.draw_rectangle(self.x,self.y,self.w,self.vh,_rl.Color(0 if not self.collapsed else 128,128,128,255))
        _rl.draw_rectangle_lines_ex([self.x,self.y,self.w,self.vh],1,_rl.Color(0 if not self.collapsed else 255,255,255,255))
        _rl.draw_text(self.label,self.x+3,self.y+3,10,_rl.Color(255,255,255,255))
        _rl.gui_draw_icon(115 if self.collapsed else 116,self.x+self.w-16,self.y-1,1,_rl.Color(255,255,255,255))
        if not curwindow.h < self.y+5:
            if _rl.is_mouse_button_pressed(0):
                if _rl.check_collision_point_rec(self.mp,[self.x+self.off.x,self.y+self.off.y,self.w,self.vh]):
                    self.obj.collapsed = not self.obj.collapsed
        GUIState.Widgets[f"ch_{id}"] = collheadInfo(self.collapsed,self.wincollapsed,self.oldindent,self.startx,self.starty)
        if self.collapsed:
            return False
        set_indent(self.indent)
        return True

def reset_collapsing_header(id:str):
    self = GUIState.Widgets[f"ch_{id}"]
    #if not self.collapsed:
    _rl.draw_line(self.startx+1,self.starty+15,self.startx+1,winy-1+curwindow.scroll_y,_rl.Color(0,255,255,255))
    curwindow.collapsed = self.wincollapsed
    winx = self.oldindent
    lastwinxchange.append(self.oldindent)
    GUIState.Widgets[f"ch_{id}"] = self        
    set_indent(self.oldindent)
    
    
class checkbox_button(Widget):
    def __init__(self,label,id,value=False):
        """Circular toggle button widget.

        Args:
            label (str): label of the widget
            id (str): identifier for the widget
            value (bool, optional): value. Defaults to False.
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
        if super().__init__(winx,winy,12+_measure_text(label,10),12):
            self = None
            return
        
        if self.value:
            self.color = _rl.Color(0,255,255,255)
        else:
            self.color = _rl.Color(128,128,128,255)
        if not curwindow.h < self.y+5:
            if _rl.is_mouse_button_pressed(0):
                if _rl.check_collision_point_rec(self.mp,[self.x+self.off.x,self.y+self.off.y,self.w,self.vh]):
                    self.value = not self.value
        #_rl.draw_circle(self.x+6,self.y+6,5,self.color)
        #_rl.draw_circle_lines(self.x+6,self.y+6,5,_rl.Color(0,255,255,255))
        _rl.draw_rectangle(self.x,self.y+1,10,10,self.color)
        _rl.draw_rectangle_lines_ex([self.x,self.y+1,10,10],1,_rl.Color(0,255,255,255))
        _rl.draw_text(self.label,self.x+12,self.y+1,10,_rl.Color(255,255,255,255))
        GUIState.Widgets[f"cb_{id}"] = self
