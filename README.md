# SGUI - Spelis's GUI Library 
![PyPI - Version](https://img.shields.io/pypi/v/spelis_sgui)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/spelis_sgui)
![GitHub repo size](https://img.shields.io/github/repo-size/spelis/sgui)


A lightweight and easy-to-use GUI library inspired by the [ImGui](https://github.com/ocornut/imgui) library. The library is written in Python and uses the [Raylib](https://github.com/raysan5/raylib) library for rendering.

[Documentation](https://sgui.readthedocs.io/en/latest/)

### Contributions are very welcome! :D

## Features
- Minimal dependencies
- Easy to use and integrate

## Installation
1. Install the package: `pip install spelis-sgui`
2. Import the library: `import sgui as gui`
3. If something went wrong and raylib (pyray) isnt installed, run this command: `pip install raylib`

## Example Usage
```python
import sgui as gui
from pyray import * # Raylib

init_window(800,600,"SGUI Example")
gui.init() # initialize the library after raylib
win = gui.Window(10,10,150,150,"My Window!") # create a window

while not window_should_close(): # raylib drawing functions
    begin_drawing()
    clear_background(BLACK)
    gui.NotifTick() # update the notifications (optional)
    with win: # this is a context manager that sets the window as the current window
        gui.label("Hello World!") # displays a little label inside the window
    end_drawing()

close_window()
```
