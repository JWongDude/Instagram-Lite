from tkinter import * 
from tkinter import ttk
import numpy as np
import cv2
from ImageDisplay import ImageDisplay

MIN_CONTRAST = 0.5
MAX_CONTRAST = 1.5
MIN_BRIGHTNESS = -50
MAX_BRIGHTNESS = 50
MAX_SHARPNESS = 5  #Min sharpness is 0

class SlideDisplay() :
    def __init__(self, root, image_display, grid_setting=(1,0)):
        #Initialize Frame
        self.frame = ttk.Frame(root)
        self.frame.grid(row=grid_setting[0], column=grid_setting[1], sticky=(N,E))
        
        #Grab that Image
        self.image_display = image_display
        self.ref_image = image_display.edited.cv_image
        self.new_image = self.ref_image.copy()

        #References for Computation:
        self.identity = np.arange(0.0,256.0)
        self.active_func = None
        self.previous_sharpness = 0
        self.buffer_sharpness = 0

        #Initialize Sliders (Boring Stuff, you can skip reading this part)
        self.brightness = ttk.Scale(self.frame, from_=MIN_BRIGHTNESS, to=MAX_BRIGHTNESS, 
                                    value=(MIN_BRIGHTNESS + MAX_BRIGHTNESS) // 2,
                                    orient=HORIZONTAL, length=300,
                                    command=self.adjust_brightness)
        self.brightness.grid(row=0, column=0, columnspan=3) 
        self.b_label = ttk.Label(self.frame, text="Brightness")
        self.b_label.grid(row=1, column=1)

        self.b1 = ttk.Label(self.frame, text="-50")
        self.b1.grid(row=1, column=0, sticky=(W))

        self.b2 = ttk.Label(self.frame, text="50")
        self.b2.grid(row=1, column=2, sticky=(E))

        self.contrast = ttk.Scale(self.frame, from_=MIN_CONTRAST, to=MAX_CONTRAST, 
                                    value=(MIN_CONTRAST + MAX_CONTRAST) // 2,
                                    orient=HORIZONTAL, length=300,
                                    command=self.adjust_contrast)
        self.contrast.grid(row=2, column=0, columnspan=3)
        self.c_label = ttk.Label(self.frame, text="Contrast")
        self.c_label.grid(row=3, column=1)

        self.c1 = ttk.Label(self.frame, text="-50")
        self.c1.grid(row=3, column=0, sticky=(W))

        self.c2 = ttk.Label(self.frame, text="50")
        self.c2.grid(row=3, column=2, sticky=(E))

        self.sharpness = ttk.Scale(self.frame, from_=0, to=MAX_SHARPNESS, 
                                    value=0,
                                    orient=HORIZONTAL, length=300,
                                    command=self.adjust_sharpness)
        self.sharpness.grid(row=4, column=0, columnspan=3)
        self.s_label = ttk.Label(self.frame, text="Sharpness")
        self.s_label.grid(row=5, column=1)

        self.s1 = ttk.Label(self.frame, text="0")
        self.s1.grid(row=5, column=0, sticky=(W))

        self.s2 = ttk.Label(self.frame, text="100")
        self.s2.grid(row=5, column=2, sticky=(E))

    """Computational Methods"""
    #Applying Formula, f(x) = ax + b
    # a = contrast
    # b = brightness
    #Convert grayscale to color and publish to image.
    def adjust_brightness(self, b) :
        #Grab current edit:
        if (self.image_display.active_widget != "brightness") :
            self.ref_image = self.image_display.edited.cv_image
            self.new_image = self.ref_image.copy()
            self.image_display.active_widget = "brightness"

        self.active_func = self.identity + round(float(b),1)
        self._filter()
        self._apply_transformation()
        self._publish_photo()

    #Applying Formula, f(x) = ax + b
    # a = contrast
    # b = brightness
    def adjust_contrast(self, a):
        #Grab current edit:
        if (self.image_display.active_widget != "contrast") :
            self.ref_image = self.image_display.edited.cv_image
            self.new_image = self.ref_image.copy()  
            self.image_display.active_widget = "contrast"

        self.active_func = self.identity * round(float(a),1)
        self._filter()
        self._apply_transformation()
        self._publish_photo()

    #High Boost Filter
    def adjust_sharpness(self, k):
        #Grab current edit:
        if (self.image_display.active_widget != "sharpness") :
            self.ref_image = self.image_display.edited.cv_image
            self.new_image = self.ref_image.copy()  
            self.image_display.active_widget = "sharpness"
            self.previous_sharpness = self.buffer_sharpness
        
        #Make a dummy image
        hsv_image = cv2.cvtColor(self.ref_image, cv2.COLOR_RGB2HSV)        
        value = hsv_image[:,:,2]
        value_new = value.copy()

        #Algorithm
        c = round(float(k),1)
        laplacian = np.array([[0, -1, 0],
                              [-1,  4, -1],
                              [0, -1, 0]])
  
        identity = np.array([[0, 0, 0],
                            [0, 1, 0],
                            [0, 0, 0]])

        filtered = cv2.filter2D(value_new, -1, 
                    identity + ((c - self.previous_sharpness) * laplacian))
        hsv_image[:,:,2] = filtered
        self.new_image = hsv_image

        self._publish_photo()

        #Save current sharpness for unsharpening 
        self.buffer_sharpness = c

    """Helper Methods"""
    def _filter(self):
        #Threshold to 255:
        for i in range(256) :
            if (self.active_func[i] > 255):
                self.active_func[i] = 255
            elif (self.active_func[i] < 0):
                self.active_func[i] = 0    
        #Alternatively, use "walrus operator"
        self.active_func = self.active_func.astype(int)

    def _apply_transformation(self) :
        #Make a dummy image
        hsv_image = cv2.cvtColor(self.ref_image, cv2.COLOR_RGB2HSV)        
        value = hsv_image[:,:,2]
        value_new = value.copy()

        #Operate
        xrange, yrange = value.shape
        for x in range(xrange) :
            for y in range(yrange) :
                v = value[x][y]
                value_new[x][y] = self.active_func[v]
        self.new_image = cv2.merge((hsv_image[:,:,0], hsv_image[:,:,1], value_new))

    def _publish_photo(self) :
        #Convert back to RGB:
        rgb_image = cv2.cvtColor(self.new_image, cv2.COLOR_HSV2RGB)
        self.image_display.edited.cv_image = rgb_image

        #Also update the color planes:
        plane = self.image_display.edited.color_planes
        plane["red"] = rgb_image[:,:,0]
        plane["green"] = rgb_image[:,:,1]
        plane["blue"] = rgb_image[:,:,2]

        self.image_display.edited.update_photo()

if __name__ == "__main__" :
    top = Tk()
    # image = ImageDisplay(top, "lena.bmp")
    image = ImageDisplay(top, "baseball.JPG")
    slide_display = SlideDisplay(top, image)
    top.mainloop()