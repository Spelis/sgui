# SGUI - Spelis's GUI Library

A lightweight and easy-to-use GUI library inspired by the [ImGui](https://github.com/ocornut/imgui) library. The library is written in Python and uses the [Raylib](https://github.com/raysan5/raylib) library for rendering.

### Contributions are very welcome! :D

## Features
- Minimal dependencies
- Easy to use and integrate

## Installation
### Manual (GitHub)
1. Clone the repo: `git clone https://github.com/Spelis/sgui.git` and `cd` into it.
2. Install dependencies: `pip install -r requirements.txt`
3. Build Package: `py -m build`
4. Install Package: `pip install .`
### PyPI
1. Install the package: `pip install spelis-sgui`
2. Import the library: 

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
