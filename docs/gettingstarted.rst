Getting started
===============

Here's a quick example to getting started with SGUI.

.. code-block:: python

    import sgui as gui
    from pyray import * # Raylib

    init_window(800,600,"SGUI Example")
    gui.init() # initialize the library after raylib
    win = gui.Window(10,10,150,150,"My Window!") # create a window

    while not window_should_close(): # raylib drawing functions
        begin_drawing()
        clear_background(BLACK)
        with win: # this is a context manager that sets the window as the current window
            gui.label("Hello World!") # displays a little label inside the window
        end_drawing()
