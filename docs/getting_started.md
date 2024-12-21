Getting started
===============

Heres a quick guide to getting started with SGUI.

```py
import sgui as gui
from pyray import * # Raylib

init_window(800,600,"SGUI Example")
win = gui.Window(10,10,150,150,"My Window!")

while not window_should_close():
    begin_drawing()
    clear_background(BLACK)
    with win:
        gui.label("Hello World!")
    end_drawing()

```
