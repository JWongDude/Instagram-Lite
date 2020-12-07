from tkinter import * 
from tkinter import ttk
from ImageDisplay import ImageDisplay
from SplineDisplay import SplineDisplay
from SlideDisplay import SlideDisplay

class ImageEditor() :
    def __init__(self, image_path) :
        self.root = Tk()
        #Header
        self.header = Canvas(self.root, height = 40, width = 900, bg="gray75")
        self.header.create_text(80, 20, text="Instagram", font=("TKFont", 20))
        self.header.grid(row=0, columnspan=4)

        #Editor Elements
        self.image_path = image_path
        self.image_display = ImageDisplay(self.root, image_path, grid_setting=(1,0))
        self.spline_display = SplineDisplay(self.root, self.image_display, grid_setting=(2,1))
        self.slide_display = SlideDisplay(self.root, self.image_display, grid_setting=(2,0))

        #Signature
        self.label = ttk.Label(text="Jonathan Wong \nUniversity of Washington\nEE440: Image Processing", 
                                font=('TkMenuFont', 15))                      
        self.label.grid(row=3, column=0, sticky=(N))

        #Reset 
        self.reset = ttk.Button(text="Reset", command=self._reset)
        self.reset.grid(row=2, sticky=(S,E))

        self.root.mainloop()

    def _reset(self) :
        self.image_display = ImageDisplay(self.root, self.image_path, grid_setting=(1,0))
        self.spline_display = SplineDisplay(self.root, self.image_display, grid_setting=(2,1))
        self.slide_display = SlideDisplay(self.root, self.image_display, grid_setting=(2,0)) 

if __name__ == "__main__" :
    #image_editor = ImageEditor("baseball.JPG")
    image_editor = ImageEditor("test.JPG")