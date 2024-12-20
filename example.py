from pyray import *
import src as gui
import subprocess, os, platform

def open_file(filepath):
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))

init_window(1280,720,"SGUI Example")
gui.init()
win = gui.Window(10,10,200,150,"test")
win2 = gui.Window(10,250,200,150,"test2",Color(255,0,0,255))
testimg = load_texture("test.png")

timesclicked = 0
while not window_should_close():
    begin_drawing()
    clear_background(BLACK)
    draw_fps(10,10)
    with win:
        if gui.checkbox_button("hello","test",False).value:
            gui.sameline()
            if gui.checkbox_button("world","test2",False).value:
                gui.sameline()
                gui.label("Yipee!")
        if gui.button(100,f"Click me").pressed:
            timesclicked += 1
        gui.label("times clicked: " + str(timesclicked))
        if gui.button(100,"Hold me").held:
            gui.sameline()
            gui.label("Yipee!")
        gui.label("value of input: " + gui.textinput(100,"Type Something!","testinput").value)
        if gui.button_img(50,50,testimg).pressed:
            print("test")
        gui.sameline()
        gui.image(50,50,testimg)
        gui.slider_vec2(50,50,"test","2D slider???").limit(-10,10)
        g = gui.slider(100,"Limited Slider","test").limit(-10,10).value
        gui.label("value of slider = " + str(g))
        gui.slider(150,"Unlimited Slider","test2").value
        if gui.collapsing_header(100,"Click me","test").show():
            gui.label("I Collapse and Expand!")
            if gui.collapsing_header(100,"test","test2").show():
                for i in range(round(gui.slider(200,"Drag me for a surprise!","surprise",0.1).limit(0,None).value)):
                    gui.button(100,"Cool, right?")
                gui.label("This is a label!")
            gui.reset_collapsing_header("test2")
        gui.reset_collapsing_header("test")
        gui.button(150,"This is a useless button!")
    with win2:
        gui.label("another window...")
        if gui.button(100,"Open Source Code").pressed:
            open_file(__file__)
        win2.movable = gui.checkbox_button("Enable window move","winmove",True).value
        win2.resizable = gui.checkbox_button("Enable window resize","winres",True).value
        if gui.checkbox_button("Window size slider","winresize",False).value:
            s = gui.slider_vec2(50,50,"Window Size","winsize",1).limit(100,None)
            win2.w,win2.h = round(s.x),round(s.y)
        win2.titlecolor = gui.colorpicker("test",default=[0,255,255]).value
        

    end_drawing()
