from tkinter import *  
from tkinter import ttk
import cv2
import PIL.Image, PIL.ImageTk

DEFAULT_FRAME_HEIGHT = 400
DEFAULT_FRAME_WIDTH = 400

class ImageDisplay() :
    def __init__(self, root, image_path, grid_setting=(0,0)) :
        #Initialize Display Frame
        self.display_frame = Canvas(root)
        self.display_frame.grid(row=grid_setting[0], column=grid_setting[1],
                                rowspan=1, columnspan=2)

        #Initialize Image Frames
        self.original = ImageFrame(self.display_frame, image_path,
                                    msg="Original", grid_cell=(0, 0), grid_span=(1, 1))
        self.edited = ImageFrame(self.display_frame, image_path, 
                                    msg="Edited", grid_cell=(0, 1), grid_span=(1, 1))

        #Active widget:
        self.active_widget = None

class ImageFrame() :
    def __init__(self, parent, image_path, msg, grid_cell=(0,0), grid_span=(1,1)) :
        #Load Images into cv2 editing engine
        self.cv_image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
        self.height, self.width, _ = self.cv_image.shape

         #Fit to window size for visual appeal
        a1 = float(DEFAULT_FRAME_HEIGHT / self.height)
        a2 = float(DEFAULT_FRAME_WIDTH / self.width)
        #Apply minimal-change aspect ratio, the larger a
        if a1 > a2 : 
            dim = (int(self.width * a1), int(self.height * a1))
        else: 
            dim = (int(self.width * a2), int(self.height * a2))

        self.cv_image = cv2.resize(self.cv_image, dim)
        self.height, self.width, _ = self.cv_image.shape

        red, green, blue = cv2.split(self.cv_image)
        self.color_planes = dict([("red", red), 
                                  ("green", green), 
                                  ("blue", blue)])

        #Convert Images into PIL for display 
        self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.cv_image)) 
        
        #Prepare Image Frame
        self.image_frame = ttk.Frame(parent)
        self.image_frame['padding'] = (20,20)
        # self.image_frame.grid(column=grid_cell[1], row=grid_cell[0], 
        #                         columnspan=grid_span[1], rowspan=grid_span[0])
        
        self.image_frame.pack(side=LEFT)

        self.image_canvas = Canvas(self.image_frame, height=DEFAULT_FRAME_HEIGHT, 
                                                        width=DEFAULT_FRAME_WIDTH)

        #Place Image inside Frame
        self.image_canvas.create_image((DEFAULT_FRAME_WIDTH//2, DEFAULT_FRAME_HEIGHT//2),
                                         image=self.photo)
        self.image_canvas.pack()

        #Labels
        self.label = self.image_canvas.create_text(DEFAULT_FRAME_WIDTH // 2, DEFAULT_FRAME_HEIGHT - 40,
                        text=msg, anchor='n', font=('TkMenuFont', 15))

    def update_photo(self) :
        self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.cv_image))
        self.image_canvas.create_image((DEFAULT_FRAME_WIDTH//2, DEFAULT_FRAME_HEIGHT//2), 
                                            image=self.photo)
        self.image_canvas.create_text(DEFAULT_FRAME_WIDTH // 2, DEFAULT_FRAME_HEIGHT - 40,
                        text="Edited", anchor='n', font=('TkMenuFont', 15))

# if __name__ == "__main__" :
#     top = Tk()
#     # image = ImageDisplay(top, "lena.bmp")
#     image = ImageDisplay(top, "baseball.JPG")
#     top.mainloop()