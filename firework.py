#! /Library/Frameworks/Python.framework/Versions/3.7/bin/python3
from tkinter import *
from random import randint, random

class Firework:
    def __init__(self, canvas, color, lifespan=500, seed=True, pos=None):
        self.vel = [0,-(random()*8+7)] if seed else [4*random()-2, 4*random()-2]
        self.acc = [0,0]
        self.color, self.seed, self.lifespan = color, seed, lifespan
        self.canvas = canvas
        self.id = canvas.create_oval(0, 0, 5, 5, fill=color, width=0)
        if seed:
            self.canvas.move(self.id, randint(0,885), 550)
        else:
            self.canvas.move(self.id, pos[0], pos[1])

    def update(self):
        self.vel = [v+a for v,a in zip(self.vel,self.acc)]
        self.acc = [0,0.2]
        self.canvas.move(self.id, self.vel[0], self.vel[1])
        self.lifespan -= 1
        if self.vel[1] >= 0 and self.seed == True:
            part = [Firework(self.canvas,self.color,lifespan=40,seed=False,pos=self.canvas.coords(self.id)) for _ in range(30)]
            for p in part:
                p.update()
            newFirework = Firework(self.canvas, self.color)
            newFirework.update()
            self.canvas.delete(self.id)
        elif self.lifespan == 0:
            self.canvas.delete(self.id)
        else:
            self.canvas.after(25, self.update)

def main():
    # initialize root
    root = Tk()
    root.title("Fireworks")
    root.geometry('890x550')
    root.configure(bg='#1F1F1F')
    root.wm_attributes("-topmost", 1)

    # Create screen label
    label = Label(root, text='Game Over', pady=8, bg='#474747', fg='#FFFFFF', font=('Helvetica', 24, "bold"))
    label.pack(side='top', fill='both')

    # Create canvas
    canvas = Canvas(root, width=890, height=550, bg='#1F1F1F', highlightthickness=0)
    canvas.pack()

    # Create canvas
    colors = ['magenta', 'yellow', 'green', 'blue', 'red']
    fireworks = [Firework(canvas,color=colors[i%5]) for i in range(15)]
    for firework in fireworks:
        firework.update()

    root.mainloop()

def aux(root, score):

    if score > 24:
        msg = 'Your fireworks were legendary.\n Everyone was speachless and will remember them forever.'
    elif score > 20:
        msg = 'Your fireworks were amazing. They will be talking about them for weeks.'
    elif score > 15:
        msg = 'Your fireworks were excellent and crowd pleasing.'
    elif score > 10:
        msg = 'Your fireworks were an honorable attempt, but quickly forgotten.'
    elif score > 5:
        msg = 'Your fireworks were mediocre.\nThere was just a hint of scattered applause.'
    else:
        msg = 'Your fireworks were horrible and booed by the crowd.'

    msg = f'{msg}\n\nYou scored {score} points out of 25.\n\nThank you for playing!'

    # Create canvas
    canvas = Canvas(root, width=890, height=500, bg='#1F1F1F', highlightthickness=0)
    canvas.create_text(445, 225, fill='#FFFFFF', text=msg, justify='center', font=('Helvetica', 18))
    canvas.grid(column=0, row=1)

    # Create canvas
    colors = ['magenta', 'yellow', 'green', 'blue', 'red']
    fireworks = [Firework(canvas,color=colors[i%5]) for i in range(10)]
    for firework in fireworks:
        firework.update()

if __name__=='__main__':
    main()

################################################################################

# import tkinter as tk
#
# class SampleApp(tk.Tk):
#     def __init__(self):
#         tk.Tk.__init__(self)
#         self._frame = None
#         self.switch_frame(StartPage)
#
#     def switch_frame(self, frame_class):
#         new_frame = frame_class(self)
#         if self._frame is not None:
#             self._frame.destroy()
#         self._frame = new_frame
#         self._frame.pack()
#
# class StartPage(tk.Frame):
#     def __init__(self, master):
#         tk.Frame.__init__(self, master)
#         tk.Label(self, text="Start page", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", pady=5)
#         tk.Button(self, text="Go to page one",
#                   command=lambda: master.switch_frame(PageOne)).pack()
#         tk.Button(self, text="Go to page two",
#                   command=lambda: master.switch_frame(PageTwo)).pack()
#
# class PageOne(tk.Frame):
#     def __init__(self, master):
#         tk.Frame.__init__(self, master)
#         tk.Frame.configure(self,bg='blue')
#         tk.Label(self, text="Page one", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", pady=5)
#         tk.Button(self, text="Go back to start page",
#                   command=lambda: master.switch_frame(StartPage)).pack()
#
# class PageTwo(tk.Frame):
#     def __init__(self, master):
#         tk.Frame.__init__(self, master)
#         tk.Frame.configure(self,bg='red')
#         tk.Label(self, text="Page two", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", pady=5)
#         tk.Button(self, text="Go back to start page",
#                   command=lambda: master.switch_frame(StartPage)).pack()
#
# if __name__ != "__main__":
#     app = SampleApp()
#     app.mainloop()

##############################################################################
#
# from tkinter import *
# import random
# import time
#
# root = Tk()
# root.title = "Game"
# root.resizable(0,0)
# root.wm_attributes("-topmost", 1)
#
# canvas = Canvas(root, width=500, height=400, bd=0, highlightthickness=0)
# canvas.pack()
#
# class Ball:
#     def __init__(self, canvas, color):
#         self.canvas = canvas
#         self.id = canvas.create_oval(10, 10, 25, 25, fill=color)
#         self.canvas.move(self.id, 245, 100)
#
#         self.canvas.bind("<Button-1>", self.canvas_onclick)
#         self.text_id = self.canvas.create_text(300, 200, anchor='se')
#         self.canvas.itemconfig(self.text_id, text='Hello There')
#
#     def canvas_onclick(self, event):
#         self.canvas.itemconfig(
#             self.text_id,
#             text=f'You clicked at ({event.x}, {event.y})'
#         )
#
#     def draw(self):
#         self.canvas.move(self.id, 1, -1)
#         self.canvas.after(50, self.draw)
#
# ball = Ball(canvas, "red")
# ball.draw()  #Changed per Bryan Oakley's comment.
# root.mainloop()

################################################################################

# from tkinter import *
#
# canvas_width = 500
# canvas_height = 150
#
#
# def paint(event):
#     python_green = '#00FFFF'
#     x1, y1 = (event.x - 1), (event.y - 1)
#     x2, y2 = (event.x + 1), (event.y + 1)
#     w.create_oval(x1, y1, x2, y2, fill=python_green, width=0)
#
#
#
# master = Tk()
# master.title("Points")
# w = Canvas(master,
#            width=canvas_width,
#            height=canvas_height)
# w.pack(expand=YES, fill=BOTH)
# w.bind("<B1-Motion>", paint)
#
# message = Label(master, text="Press and Drag the mouse to draw")
# message.pack(side=BOTTOM)
#
# mainloop()
