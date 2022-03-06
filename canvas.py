from tkinter import *

class Overlay():

    def __init__(self):
        self.root = Tk()
        self.root.geometry("1920x1080")
        self.root.attributes("-alpha", 0.3, "-fullscreen", True)
        self.canvas = Canvas(self.root, width=1920, height=1080)
        self.canvas.pack()

    def draw(self, cordinates):
        for i in cordinates:
            self.canvas.create_rectangle(i[0], i[1], i[0]+50, i[1]+15,fill="red")
        self.root.mainloop()

if __name__ == "__main__":
    o = Overlay()
    o.draw()