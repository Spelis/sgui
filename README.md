# SGUI - Spelis's GUI Library

A lightweight and easy-to-use GUI library made by Spelis (Me :3) inspired by the [ImGui](https://github.com/ocornut/imgui) library. The library is written in Python and uses the [Raylib](https://github.com/raysan5/raylib) library for rendering.

### Contributions are very welcome! :D

## Features
- Minimal dependencies
- Easy to use and integrate

## Installation
### Manual (GitHub)
1. Clone the repo: `git clone https://github.com/Spelis/sgui.git` at a location accessible to your project or script.
2. Install raylib: `pip install raylib`
3. Import the library: `import sgui`
### PyPI
- yeah, no i haven't gotten around to putting it on PyPI yet.

## Example Usage
```python
import sgui as gui
from pyray import *

# initialize raylib
init_window(800,600,"SGUI Example")
gui.init()
window = gui.Window(10,10,150,150,"Example Window")

while not window_should_close(): # raylib window loop and drawing
    begin_drawing()
    clear_background(BLACK)

    with window: # my gui library :)
        if gui.button(100,"Example Button"):
            print("Button was pressed!")

    end_drawing()

close_window()
```
