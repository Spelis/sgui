Welcome to SGUI docs!
=====================

Introduction
------------

SGUI is a Python library for creating graphical user interfaces (GUIs). It uses the Raylib library for rendering and input

Installation
------------

Prerequisites
~~~~~~~~~~~~~

Before installing, make sure you have:

- Python 3.8+
- pip (Python package installer)

Installation
~~~~~~~~~~~~

.. code-block:: bash

    pip install spelis_sgui

Troubleshooting
~~~~~~~~~~~~~~~

If you encounter any issues during installation, please create an issue on the `GitHub repository <https://github.com/spelis/sgui>`_.

Getting started
---------------

Here's a quick guide to getting started with SGUI.

.. code-block:: python

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

API reference
-------------

.. autofunction:: sgui.init

.. autoclass:: sgui.Window
.. autoclass:: sgui.Widget

.. autoclass:: sgui.button
.. autoclass:: sgui.imgbutton
.. autoclass:: sgui.label
.. autoclass:: sgui.textinput
.. autoclass:: sgui.slider_vec2
.. autoclass:: sgui.slider
.. autoclass:: sgui.solidcolor
.. autoclass:: sgui.colorpicker
.. autoclass:: sgui.image
.. autoclass:: sgui.collapsingheader
    :members:
.. autofunction:: sgui.reset_collapsing_header
.. autoclass:: sgui.checkbox_button

.. autoclass:: sgui.GUIState
.. autofunction:: sgui.set_indent
.. autofunction:: sgui.sameline
.. autofunction:: sgui.cancel_sameline
.. autofunction:: sgui._log
