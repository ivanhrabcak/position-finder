import tkinter
from enum import Enum
from tkinter.constants import BOTH, YES
from threading import Timer
from typing import Union

def delayed_execution(fun, args, timeout):
    Timer(timeout, fun, args).start()


class Shape(Enum):
    Rectangle = 0
    Line = 1
    Triangle = 2
    Circle = 3
    Delete = 4

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return f"Point({str(self.x)}, {str(self.y)})"

class Rectangle:
    def __init__(self, start_point: Point, end_point: Point, item: str):
        self.start_point = start_point
        self.end_point = end_point
        self.item = item
    
    def __str__(self):
        return f"Rectangle: Point({str(self.start_point.x)}, {str(self.start_point.y)}), Point({str(self.end_point.x)}, {str(self.end_point.y)})"

class Line:
    def __init__(self, start_point: Point, end_point: Point, item: str):
        self.start_point = start_point
        self.end_point = end_point
        self.item = item
    
    def __str__(self):
        return f"Line: Point({str(self.start_point.x)}, {str(self.start_point.y)}), Point({str(self.end_point.x)}, {str(self.end_point.y)})"

class Triangle:
    def __init__(self, x: Point, y: Point, z: Point, item: str):
        self.x = x
        self.y = y
        self.z = z
        self.item = item
    
    def __str__(self):
        return f"Triangle: {str(self.x)}, {str(self.y)}, {str(self.z)}"

class Circle:
    def __init__(self, x: Point, y: Point, item: str):
        self.x = x 
        self.y = y
        self.item = item

    def __str__(self):
        return f"Circle: Point({str(self.x.x)}, {self.x.y}), Point({self.y.x}, {self.y.y})"

class DrawingCanvas(tkinter.Canvas):
    def __init__(self, parent, **kwargs):
        tkinter.Canvas.__init__(self, parent, **kwargs)
        
        # register all calback we'll need
        self.bind("<Configure>", self.on_resize) # resize callback
        self.bind_all("<KeyPress>", self.on_keydown)
        self.bind_all("<Button-1>", self.on_mouse1_down)
        self.bind_all("<Button-3>", self.on_mouse2_down)
        self.bind_all("<ButtonRelease-1>", self.on_mouse1_up)

        # fetch the current window width and height
        self.height = self.winfo_reqheight() 
        self.width = self.winfo_reqwidth()
        
        self.shape = Shape.Rectangle # set the default shape

        self.drawn_shapes = []

        # triangle drawing
        self.is_choosing_triangle_points = False 
        self.current_triangle_points = []
        
        # rectangle drawing
        self.is_drawing_rectangle = False 
        self.rectangle_starting_point = None

        # line drawing
        self.is_drawing_line = False
        self.line_starting_point = None    

        # circle drawing
        self.is_drawing_circle = False
        self.circle_starting_point = None
    
    def on_mouse1_up(self, event):
        mx = event.x
        my = event.y

        if self.is_drawing_rectangle:
            rect_width = (self.rectangle_starting_point.x - mx) * -1
            rect_height = (self.rectangle_starting_point.y - my) * -1
            x, y = self.rectangle_starting_point.x, self.rectangle_starting_point.y

            item = self.create_rectangle(x, y, x + rect_width, y + rect_height)
            self.drawn_shapes.append(Rectangle(Point(x, y), Point(x + rect_width, y + rect_height), item))

            self.is_drawing_rectangle = False
        elif self.is_drawing_line:
            item = self.create_line(self.line_starting_point.x, self.line_starting_point.y, mx, my)
            self.drawn_shapes.append(Line(self.line_starting_point, Point(mx, my), item))

            self.is_drawing_line = False
        elif self.is_drawing_circle:
            item = self.create_oval(self.circle_starting_point.x, self.circle_starting_point.y, mx, my)
            self.drawn_shapes.append(Circle(self.circle_starting_point, Point(mx, my), item))
            self.is_drawing_circle = False

    def on_mouse2_down(self, event):
        mx = event.x
        my = event.y

        item = self.find_closest(mx, my)
        drawn_shape = self.get_drawn_shape_by_item(*item)

        if drawn_shape == None:
            return

        print(str(drawn_shape))

    
    def on_mouse1_down(self, event):
        mx = event.x
        my = event.y

        if self.shape == Shape.Triangle:
            if len(self.current_triangle_points) == 2:
                self.delete("point")
                self.current_triangle_points.append(Point(mx, my))
                
                p = self.current_triangle_points

                points = [p[0].x, p[0].y, p[1].x, p[1].y, p[2].x, p[2].y]
                item = self.create_polygon(points)

                self.drawn_shapes.append(Triangle(p[0], p[1], p[2], item))

                self.is_choosing_triangle_points = False
                self.current_triangle_points.clear()
                return

            self.is_choosing_triangle_points = True

            item = self.create_oval(mx -1, my -1, mx + 1, my + 1, tags=["point"])
            self.current_triangle_points.append(Point(mx, my))
        elif self.shape == Shape.Rectangle:
            self.rectangle_starting_point = Point(mx, my)
            self.is_drawing_rectangle = True
        elif self.shape == Shape.Line:
            self.is_drawing_line = True
            self.line_starting_point = Point(mx, my)
        elif self.shape == Shape.Circle:
            self.is_drawing_circle = True
            self.circle_starting_point = Point(mx, my)

    def find_horizontal_center(self, item):
        coords = self.bbox(item)
        return (self.width / 2) - ((coords[2] - coords[0]) / 2) 
    
    def delete(self, *tagsOrCanvasIds: Union[str, int]) -> None:
        super().delete(*tagsOrCanvasIds)

        if tagsOrCanvasIds == None:
            return

        for shape in self.drawn_shapes:
            if shape.item == tagsOrCanvasIds[0]:
                self.drawn_shapes.remove(shape)
                return

    def get_drawn_shape_by_item(self, item):
        for shape in self.drawn_shapes:
            if shape.item == item:
                return shape

    
    def flash_text(self, text):
        text_id = self.create_text(0, 50, text=text, font=("Arial", 35), tags=["flash_text"])
        x_offset = self.find_horizontal_center(text_id)
        self.move(text_id, x_offset, 0)
        delayed_execution(self.delete, ("flash_text",), 2)

    def shape_to_string(self, shape):
        if shape == Shape.Rectangle:
            return "Rectangle"
        elif shape == Shape.Circle:
            return "Circle"
        elif shape == Shape.Line:
            return "Line"
        elif shape == Shape.Triangle:
            return "Triangle"
        else:
            return "Unknown Shape"
    
    def on_keydown(self, event):
        key = event.keysym

        if self.is_choosing_triangle_points:
            return

        shape_before = self.shape

        if key == "r":
            self.shape = Shape.Rectangle
        elif key == "c":
            self.shape = Shape.Circle
        elif key == "l":
            self.shape = Shape.Line
        elif key == "t":
            self.shape = Shape.Triangle
        elif key == "BackSpace":
            self.addtag_all("all")
            self.delete("all")
        
        if shape_before != self.shape:
            self.delete("flash_text")
            self.flash_text(self.shape_to_string(self.shape))

    def on_resize(self, event):
        print("Window resized: ", end="")
        print(event.height, event.width)
        
        # determine the scaling ratio
        width_scale = float(event.width) / self.width
        height_scale = float(event.height) / self.height

        self.width = event.width
        self.height = event.height

        # change size of the window
        self.config(width=self.width, height=self.height)

        # all the canvas widget have to be tagged with the tag 'all'
        self.addtag_all("all")
        self.scale("all", 0, 0, width_scale, height_scale)


class Application:
    def __init__(self, window):
        self.window = window

        self.canvas = DrawingCanvas(self.window)

    def run(self):
        self.canvas.pack(fill=BOTH, expand=YES)
        self.window.mainloop()



def main():
    window = tkinter.Tk()

    application = Application(window)
    application.run()

if __name__ == "__main__":
    main()
