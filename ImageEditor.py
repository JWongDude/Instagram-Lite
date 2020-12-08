from tkinter import * 
from tkinter import ttk
from tkinter import filedialog
from PIL import Image
from ImageDisplay import ImageDisplay
from SplineDisplay import SplineDisplay
from SlideDisplay import SlideDisplay

class ImageEditor() :
    def __init__(self, image_path) :
        self.root = Tk()
        #Header
        self.header = Canvas(self.root, height = 40, width = 900, bg="gray75")
        self.header.create_text(110, 20, text="Instagram Lite", font=("TKFont", 20))
        self.header.grid(row=0, columnspan=4)

        #Editor Elements
        self.image_path = image_path
        self.image_display = ImageDisplay(self.root, image_path, grid_setting=(1,0))
        self.spline_display = SplineDisplay(self.root, self.image_display, grid_setting=(2,1))
        self.slide_display = SlideDisplay(self.root, self.image_display, grid_setting=(2,0))

        #Button Panel: 
        self.button_frame = ttk.Frame(self.root, height=20) #Determine size if need be
        self.button_frame.grid(row=2, sticky=(S,E))

        #Load
        self.load = ttk.Button(self.button_frame, text="Load", command=self._load)
        self.load.grid(row=0, column=0)

        #Save
        self.save = ttk.Button(self.button_frame, text="Save", command=self._save)
        self.save.grid(row=0, column=1, padx=30)

        #Reset 
        self.reset = ttk.Button(self.button_frame, text="Reset", command=self._reset)
        self.reset.grid(row=0, column=2)

        #Signature
        self.label = ttk.Label(text="\nJonathan Wong \nUniversity of Washington\nEE440: Image Processing", 
                                font=('TkMenuFont', 15))                      
        self.label.grid(row=3, column=0, sticky=(N))

        self.root.mainloop()

    def _reset(self) :
        self.image_display = ImageDisplay(self.root, self.image_path, grid_setting=(1,0))
        self.spline_display = SplineDisplay(self.root, self.image_display, grid_setting=(2,1))
        self.slide_display = SlideDisplay(self.root, self.image_display, grid_setting=(2,0)) 

    def _load(self):
        filename = filedialog.askopenfilename()
        if not filename:
            return
        self.image_path = filename
        self.image_display = ImageDisplay(self.root, self.image_path, grid_setting=(1,0))
        self.spline_display = SplineDisplay(self.root, self.image_display, grid_setting=(2,1))
        self.slide_display = SlideDisplay(self.root, self.image_display, grid_setting=(2,0))

    def _save(self):
        filename = filedialog.asksaveasfile(mode='w', defaultextension=".jpg")
        if not filename:
            return
        photo = Image.fromarray(self.image_display.edited.cv_image)
        photo.save(filename)


if __name__ == "__main__" :
    #image_editor = ImageEditor("baseball.JPG")
    image_editor = ImageEditor("test.JPG")