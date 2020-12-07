from tkinter import * 
from tkinter import ttk
import numpy as np
from scipy import interpolate
import cv2
from ImageDisplay import ImageDisplay

CANVAS_WIDTH = 450
CANVAS_HEIGHT = 250
GRID_SCALE_FACTOR = 0.85
NUM_GRID_LINES = 3
NODE_RADIUS = 6
NUM_POINTS = 5
LINE_DEFINITION = 15
POINT_MARGIN = 20

STATE_NORMAL = "default state"
STATE_DRAGGING = "dragging state"

"""Points without Collision Boxes"""
class Point(object) :
    def __init__(self, x, y) :
        self.x = x
        self.y = y

"""Points with Collision Boxes"""
class ControlPoint(Point):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.left = x - NODE_RADIUS
        self.right = x + NODE_RADIUS
        self.top = y - NODE_RADIUS
        self.bottom = y + NODE_RADIUS

    #Detects event collision when event occurs inside node bounding box 
    def collide_point(self, event) :
        return (self.left < event.x < self.right and 
                self.top < event.y < self.bottom)

"""Performs Grid Render and Collision."""
class ControlGrid(object):
    def __init__(self):

        #Boring Grid Positioning
        self.width_center = int(CANVAS_WIDTH / 2)
        self.height_center = int(CANVAS_HEIGHT / 2)

        self.grid_width = int(CANVAS_WIDTH * GRID_SCALE_FACTOR)
        self.grid_height = int(CANVAS_HEIGHT * GRID_SCALE_FACTOR)

        half_width = int(self.grid_width / 2)
        half_height = int(self.grid_height / 2)

        self.left_wall = self.width_center - half_width
        self.right_wall = self.width_center + half_width
        self.top_wall = self.height_center - half_height
        self.bottom_wall = self.height_center + half_height

        self.LT_corner = Point(self.left_wall, self.top_wall)
        self.LB_corner = Point(self.left_wall, self.bottom_wall)
        self.RT_corner = Point(self.right_wall, self.top_wall)
        self.RB_corner = Point(self.right_wall, self.bottom_wall)
        self.grid_points = [self.LT_corner, self.LB_corner, self.RT_corner, self.RB_corner]

class SplineDisplay() :
    def __init__(self, root, image_display, grid_setting=(1,1)) :
        #Initialize Display Frame
        self.frame = ttk.Frame(root)
        self.frame.grid(row=grid_setting[0], column=grid_setting[1], 
                        rowspan=2, sticky=(N,E))
        self.frame['padding'] = (0,0,20,40)

        #Define Canvas inside Frame
        self.canvas = Canvas(self.frame)
        self.canvas.config(width=CANVAS_WIDTH, height=CANVAS_HEIGHT, 
                            background="gray75")               
        self.canvas.grid(row=0)

        #Draw Control Grid
        self.control_grid = ControlGrid()
        endpts = []
        endpts.append(self.control_grid.grid_points[0].x)
        endpts.append(self.control_grid.grid_points[0].y)
        endpts.append(self.control_grid.grid_points[-1].x)
        endpts.append(self.control_grid.grid_points[-1].y)
        self.canvas.create_rectangle(endpts, width=2, fill="gray")

        #Draw Grid Lines:
        xdelta = self.control_grid.grid_width // NUM_GRID_LINES
        ydelta = self.control_grid.grid_height // NUM_GRID_LINES
        originx = self.control_grid.grid_points[0].x
        originy = self.control_grid.grid_points[0].y

        for x in range(1, NUM_GRID_LINES) :
            xcurr = originx + (xdelta * x)
            starty = self.control_grid.bottom_wall
            endy = self.control_grid.top_wall
            self.canvas.create_line([xcurr, starty, xcurr, endy])

        for y in range(1, NUM_GRID_LINES) :
            ycurr = originy + (ydelta * y)
            startx = self.control_grid.left_wall
            endx = self.control_grid.right_wall
            self.canvas.create_line([startx, ycurr, endx, ycurr])

        #Split Color Planes and Create Splines
        self.image_display = image_display
        self.red_spline = Spline(self.canvas, image_display, "red", self.control_grid,
                         preset=[ControlPoint(90, 145), ControlPoint(250, 65)]) 
        self.green_spline = Spline(self.canvas, image_display, "green", self.control_grid,
                            preset=[ControlPoint(125, 135), ControlPoint(350, 50)])
        self.blue_spline = Spline(self.canvas, image_display, "blue", self.control_grid,
                            preset=[ControlPoint(150, 140), ControlPoint(330, 70)])
        
        self.splines = dict([("red", self.red_spline), 
                            ("green", self.green_spline), 
                            ("blue", self.blue_spline)])
        
        #Define Event Bindings:
        self.canvas.bind("<Button-1>", self.on_button_one)
        self.canvas.bind("<Motion>", self.on_mouse_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_one_release)

        #Control:
        self.active_curve = "red"

        #Label 
        self.label = ttk.Label(self.frame, text="RGB Curves",
                                font=('TkMenuFont', 11))
        self.label.grid(row=1)

        self.description = ttk.Label(self.frame, 
                                text="Maps colors on x-axis to y-axis. Linear Curve is Identity.", 
                                font=('TkMenuFont', 11))
        self.description.grid(row=2)


    #Runs each curve's collision function, if collision detected, sets active curve
    def on_button_one(self, event):
        if (self.image_display.active_widget != "RGB") :
            self.image_display.active_widget = "RGB"

        for spline in self.splines.values() :
            spline.on_button_one(event)
            if (spline.state == STATE_DRAGGING) :
                self.active_curve = spline.color
                break
    
    #Run active curve's dragging function
    def on_mouse_motion(self, event):
        self.splines.get(self.active_curve).on_mouse_motion(event)
    
    #Run active curve's release funciton
    def on_button_one_release(self, event):
        self.splines[self.active_curve].on_button_one_release(event)

class Spline() :
    def __init__(self, root, image_display, color, control_grid,
                 preset=[ControlPoint(200, 300), ControlPoint(400, 150)]) :
        
        #Important References
        self.canvas = root
        self.image_display = image_display
        self.color = color
        self.control_grid = control_grid

        #Color string determines which plane to edit.
        #Grab the reference to original color plane, make a copy for edits
        self.ref_color_plane = self.image_display.edited.color_planes[color]
        self.new_color_plane = self.ref_color_plane.copy()

        #Define State
        self.state = STATE_NORMAL
        self.dragging_point = None

        #Define Point Array, set to presets
        left = self.control_grid.grid_points[1]
        right = self.control_grid.grid_points[2]
        left_anchor = ControlPoint(left.x, left.y)
        right_anchor = ControlPoint(right.x, right.y)
        self.point_array = [left_anchor] + preset + [right_anchor]

        #Define Render Elements, to store/update references to drawn line and nodes
        self.line = None
        self.render_array = [None] * NUM_POINTS

        #Transform Curve, initialized as straight line
        self.xtransform = np.linspace(self.control_grid.left_wall, self.control_grid.right_wall, 256)
        self.ytransform = None

        #Finally, draw the spline
        self.interpolate()
        self.draw_line()

    """*****Event Handling Functions******
    Control Flow transitions between Event Handling State Machine 
        and Computation/Drawing Functions below. """
    #Command callback corresponding to Left Click
    def on_button_one(self, event):
        #Detects collision, transitions state, and records corresponding point
        #Only detects collision within center points.  
        for i in range(0, NUM_POINTS - 1):
            if self.point_array[i].collide_point(event): 
                self.state = STATE_DRAGGING
                self.dragging_point = i
                break

    #Command callback corresponding to Motion
    def on_mouse_motion(self, event):
        
        #Update Position of Control Points/Line and re-render. 
        if (self.state == STATE_DRAGGING) :

            #Midpoint:
            if (0 < self.dragging_point < len(self.point_array) - 1):
                
                #Safe to define left/right points:
                index = self.dragging_point                
                left_point = self.point_array[index - 1]
                right_point = self.point_array[index + 1]

                #Restrict points to inside frame and enforcing function. 
                #Y-axis is flipped by Tkinter's orientation. 
                if (self.control_grid.top_wall <= event.y <= self.control_grid.bottom_wall and
                    left_point.x + POINT_MARGIN <= event.x <= right_point.x - POINT_MARGIN) :
                    
                    #Record new point location and update
                    new_point = ControlPoint(event.x, event.y)
                    self.point_array[index] = new_point
                    self.__update()
            else:
                #Left Endpoint: 
                if (self.dragging_point == 0) :
                    #Dragging Restrictions:
                    if (self.control_grid.top_wall <= event.y <= self.control_grid.bottom_wall) :
                        
                        #Record new point location and update
                        new_point = ControlPoint(self.control_grid.left_wall, event.y)
                        self.point_array[0] = new_point
                        self.__update()
                
                #Right Endpoint:
                else: 
                    #Dragging Restrictions:
                    if (self.control_grid.top_wall <= event.y <= self.control_grid.bottom_wall) :
                        
                        #Record new point location and update
                        new_point = ControlPoint(self.control_grid.right_wall, event.y)
                        self.point_array[-1] = new_point
                        self.__update()   

        #Inside Dragging State        

    #Helper Method to on_mouse_motion.
    #Updates Line and Image!
    def __update(self) :
        self.interpolate()
        self.draw_line()
        self.transform_image()

    #Command callback corresponding to Left Click Release
    def on_button_one_release(self, event):
        #Reset state and collision index.
        #Corresponding point is dropped and no longer updated.
        if self.state == STATE_DRAGGING:
            self.state = STATE_NORMAL
            self.dragging_point = None

    """*****Computational Functions******"""
    #Interpolates Rendered Curve wrt to Control Points.
    # Outputs curve at the specified x vector points:
    def interpolate(self) :

        #Calculate coeffcients with ref point arrays
        x = np.array([point.x for point in self.point_array])
        y = np.array([point.y for point in self.point_array])
        
        tck = interpolate.splrep(x, CANVAS_HEIGHT - y) #flip orientation

        #Calculate interpolated points, threshold at the control grid.
        result = CANVAS_HEIGHT - interpolate.splev(self.xtransform, tck, der=0) #flip orientation
        u_threshold = self.control_grid.top_wall
        l_threshold = self.control_grid.bottom_wall
        filter_result = [l_threshold if value > l_threshold 
           else u_threshold if value < u_threshold  
           else value for value in result]
        self.ytransform = np.array(filter_result)

    #Calculates Image Transform
    def transform_image(self) :
        #Converting rendered curve into function and applying to image:
        # 1) Flip:
        flipped = CANVAS_HEIGHT - self.ytransform

        # 2) Translate to Top:
        top = flipped - self.control_grid.top_wall

        # 3) Translate to Top Corner:
        #       Indicies are already [0, 255]!

        # 4) Normalize Function, map y-range to 255:
        control_grid_height = self.control_grid.bottom_wall - self.control_grid.top_wall
        func = (top / control_grid_height) * 255

        # 5) Apply function. Publish edited color plane:
        xrange, yrange = self.ref_color_plane.shape
        for x in range(xrange) :
            for y in range(yrange) :
                value = self.ref_color_plane[x][y]
                self.new_color_plane[x][y] = func[value]
        self.image_display.edited.color_planes[self.color] = self.new_color_plane

        # 6) Merge color planes :
        plane = self.image_display.edited.color_planes
        self.image_display.edited.cv_image = cv2.merge((plane["red"], plane["green"], plane["blue"]))

        # 7) Publish and Display New Image :
        self.image_display.edited.update_photo()

    """*****Drawing Functions******"""        
    #Renders Line and Control Point Endpoints
    def draw_line(self):

        #Clear Preexisting Line
        self.canvas.delete(self.line)
        
        #Draw Line, Sample by Line Definition for Simplified Rendering
        point_list = []
        step_ratio = 256 // LINE_DEFINITION
        x4render = self.xtransform[::step_ratio]
        y4render = self.ytransform[::step_ratio]
        for i in range(len(x4render)):
            point_list.append(x4render[i])
            point_list.append(y4render[i])

        #Add last point:
        point_list.append(self.point_array[-1].x)
        point_list.append(self.point_array[-1].y)

        self.line = self.canvas.create_line(point_list, smooth=True, width=2, fill="{}".format(self.color))

        #Draw nodes, drawn after line so nodes are rendered above line
        if self.state == STATE_NORMAL :
            for i, p in enumerate(self.point_array):
                self.render_array[i] = self.draw_point(p)
        elif self.state == STATE_DRAGGING :
            for i in range(0, NUM_POINTS - 1):
                self.canvas.delete(self.render_array[i])
                self.render_array[i] = self.draw_point(self.point_array[i])

    #Renders Control Points called inside Draw Line
    def draw_point(self, point):        

        bounding_box = (point.left, point.top, point.right, point.bottom)
        return self.canvas.create_oval(bounding_box, fill="{}".format("white"))

if __name__ == "__main__" :    
    top = Tk()
    #image = ImageDisplay(top, "lena.bmp")
    image = ImageDisplay(top, "baseball.JPG")
    #image = ImageDisplay(top, "flowers.tif")
    splines = SplineDisplay(top, image)
    top.mainloop()