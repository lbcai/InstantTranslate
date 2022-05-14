# for GUI
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
# for click through screen grab window
from win32gui import SetWindowLong, GetWindowLong, SetLayeredWindowAttributes
from win32con import WS_EX_LAYERED, WS_EX_TRANSPARENT, GWL_EXSTYLE, LWA_ALPHA

global title_string


class Root(ThemedTk):
    """
    Make root window default to transparent. This root window will allow the program
    to show on the task bar despite using overrideredirect for the actual main window.
    When the main window is minimized, it will not show on the taskbar as a result.
    """
    def __init__(self):
        ThemedTk.__init__(self, theme='equilux', background=True, toplevel=True)
        self.attributes('-alpha', 0.0)


class App(tk.Toplevel):

    def __init__(self, master):
        tk.Toplevel.__init__(self, master)

        horizontal_pop = int(self.winfo_screenwidth() / 2 - (self.winfo_reqwidth()) / 2)
        vertical_pop = int(self.winfo_screenheight() / 2 - (self.winfo_reqheight() / 2))
        self.geometry('+{}+{}'.format(horizontal_pop, vertical_pop))
        self.attributes('-topmost', 1)

        def move_window(event):
            # TODO make draggable
            self.geometry('+{0}+{1}'.format(event.x_root, event.y_root))

        # Create custom window title bar to match theme.
        self.overrideredirect(True)
        title_bar = ttk.Frame(self, borderwidth=3)
        close_button = ttk.Button(title_bar, text='X', width=1, command=self.master.destroy)  # close invisible root
        mini_button = ttk.Button(title_bar, text='__', width=1, command=self.master.iconify)  # minimize self
        window_title = ttk.Label(title_bar, text=title_string)
        title_bar.pack(expand=1)
        close_button.pack(side=tk.RIGHT)
        mini_button.pack(side=tk.RIGHT)
        window_title.pack(side=tk.LEFT)
        title_bar.bind('<B1-Motion>', move_window)

        # Add screen grab button and bind click + drag motion to it.
        area_select_button = ttk.Button(self, text="Select Area", command=self.screen_grab)
        area_select_button.pack()
        # Rectangle that user will draw
        self.rect = None
        # Screen overlay present during user draw
        self.overlay_window = None
        # Translate area that will remain on screen
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

        # Handle cases where user makes many grab windows or clicks button multiple times.
        if self.grab_window is not None:
            self.grab_window.destroy()
            self.grab_window = None

        if self.overlay_window is not None:
            self.overlay_window.destroy()
            self.overlay_window = None

        def mouse_down(event):
            stored_values['x1'] = event.x
            stored_values['y1'] = event.y
            self.rect = cv.create_rectangle(stored_values['x1'], stored_values['y1'], 1, 1, fill="")

        def mouse_down_move(event):
            stored_values['x2'] = event.x
            stored_values['y2'] = event.y
            cv.coords(self.rect, stored_values['x1'], stored_values['y1'], stored_values['x2'], stored_values['y2'])

        def mouse_up(event):

            def set_click_through(hwnd):
                try:
                    styles = GetWindowLong(hwnd, GWL_EXSTYLE)
                    styles = WS_EX_LAYERED | WS_EX_TRANSPARENT
                    SetWindowLong(hwnd, GWL_EXSTYLE, styles)
                    SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA)
                except Exception as e:
                    print(e)

            self.overlay_window.destroy()
            self.overlay_window = None

            # Create window for screenshot location.
            self.grab_window = tk.Toplevel(self)
            self.grab_window.overrideredirect(True)

            x_val = min(stored_values['x1'], stored_values['x2'])
            y_val = min(stored_values['y1'], stored_values['y2'])
            dimensions = str(abs(stored_values['x1'] - stored_values['x2'])) + "x" + str(abs(
                stored_values['y1'] - stored_values['y2'])) + "+" + str(x_val) + "+" + str(y_val)
            self.grab_window.geometry(dimensions)

            self.grab_window.attributes('-alpha', 0.1, '-topmost', True)
            set_click_through(self.grab_window.winfo_id())
            self.grab_window.mainloop()

        # Create screen overlay to alert user that they are in drag mode.
        self.overlay_window = tk.Toplevel(self)
        self.overlay_window.attributes('-fullscreen', True, '-alpha', 0.3, '-topmost', True)
        self.overlay_window.overrideredirect(
            True)  # prevent window from being closed by regular means, only guaranteed to work in Windows

        # Create canvas, bind left click down, drag, and release.
        cv = tk.Canvas(self.overlay_window, cursor="cross", width=self.overlay_window.winfo_screenwidth(),
                       height=self.overlay_window.winfo_screenheight())
        cv.bind("<ButtonPress-1>", mouse_down)
        cv.bind("<B1-Motion>", mouse_down_move)
        cv.bind("<ButtonRelease-1>", mouse_up)
        cv.pack()

        self.overlay_window.mainloop()


if __name__ == '__main__':
    title_string = 'InstantTranslate 1.0'
    root = Root()
    root.title(title_string)
    app = App(root)

    def on_root_deiconify(event):
        app.deiconify()

    def on_root_iconify(event):
        app.withdraw()

    root.bind("<Map>", on_root_deiconify)
    root.bind("<Unmap>", on_root_iconify)

    app.mainloop()

    # TODO allow screengrab window to be clicked through
    # TODO perform screengrab on window and save image as variable every 5s
    # TODO use pytesseract to change image to text and google translate api to translate
    # TODO refactor into classes
    # TODO fix main window layout
