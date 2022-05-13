# for GUI
from tkinter import *


class App(Frame):

    def __init__(self, frame):
        Frame.__init__(self, frame=None)
        horizontal_pop = int(frame.winfo_screenwidth() / 2 - (frame.winfo_reqwidth()) / 2)
        vertical_pop = int(frame.winfo_screenheight() / 2 - (frame.winfo_reqheight() / 2))
        frame.geometry('+{}+{}'.format(horizontal_pop, vertical_pop))

        # Add screen grab button and bind click + drag motion to it.
        area_select_button = Button(frame, text="Select Area", command=self.screen_grab)
        area_select_button.pack()
        self.rect = None
        self.grab_window = None

    def screen_grab(self):
        """
           When user presses button to set up translate area, this method is called
           and collects mouse down and release coordinates. Uses the coordinates to
           spawn a transparent tkinter window that will highlight the area to be
           monitored for translation. The user can reset the window by pressing the
           button and dragging again.
           """
        stored_values = {'x1': 0, "y1": 0, "x2": 0, "y2": 0}
        if self.grab_window is not None:
            self.grab_window.destroy()
            self.grab_window = None

        def mouse_down(event):
            stored_values['x1'] = event.x
            stored_values['y1'] = event.y
            self.rect = cv.create_rectangle(stored_values['x1'], stored_values['y1'], 1, 1, fill="")

        def mouse_down_move(event):
            stored_values['x2'] = event.x
            stored_values['y2'] = event.y
            cv.coords(self.rect, stored_values['x1'], stored_values['y1'], stored_values['x2'], stored_values['y2'])

        def mouse_up(event):
            overlay_window.destroy()

            # Create window for screenshot location.
            self.grab_window = Tk()
            self.grab_window.overrideredirect(True)

            x_val = min(stored_values['x1'], stored_values['x2'])
            y_val = min(stored_values['y1'], stored_values['y2'])
            dimensions = str(abs(stored_values['x1'] - stored_values['x2'])) + "x" + str(abs(
                stored_values['y1'] - stored_values['y2'])) + "+" + str(x_val) + "+" + str(y_val)
            self.grab_window.geometry(dimensions)

            self.grab_window.attributes('-alpha', 0.05)
            self.grab_window.mainloop()

        # Create screen overlay to alert user that they are in drag mode.
        overlay_window = Tk()
        overlay_window.attributes('-fullscreen', True, '-alpha', 0.3)
        overlay_window.overrideredirect(True)

        # Create canvas, bind left click down, drag, and release.
        cv = Canvas(overlay_window, cursor="cross", width=overlay_window.winfo_screenwidth(),
                    height=overlay_window.winfo_screenheight())
        cv.bind("<ButtonPress-1>", mouse_down)
        cv.bind("<B1-Motion>", mouse_down_move)
        cv.bind("<ButtonRelease-1>", mouse_up)
        cv.pack()

        overlay_window.mainloop()


if __name__ == '__main__':
    main_window = Tk()
    app = App(main_window)

    main_window.mainloop()
    # TODO quit/close will close all windows and exit program completely
    # TODO drawing a screengrab window over the main window will keep main window on top
    # TODO perform screengrab on window and save image as variable every 5s
    # TODO use pytesseract to change image to text and google translate api to translate

