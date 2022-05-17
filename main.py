# for GUI
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
# for click through screen grab window
from win32gui import SetWindowLong, SetLayeredWindowAttributes
from win32con import WS_EX_LAYERED, WS_EX_TRANSPARENT, GWL_EXSTYLE, LWA_ALPHA
# for image taking
from PIL import ImageGrab
import pytesseract as pt
# for running image taking while keeping program running
from time import sleep
import threading as threading

title_string = "InstantTranslate 1.0"
# pytesseract requires tesseract exe, location provided for bundling with pyinstaller package
pt.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'


class Root(ThemedTk):
    """
    Make root window default to transparent. This root window will allow the program
    to show on the task bar despite using overrideredirect for the actual main window.
    When the main window is minimized, it will not show on the taskbar as a result of using
    that method for more control over UI appearance.
    """

    def __init__(self):
        ThemedTk.__init__(self, theme='equilux', background=True, toplevel=True)
        self.attributes('-alpha', 0.0)
        self.title(title_string)
        self.bind("<Map>", lambda event: Root.on_root_deiconify(self, event))
        self.bind("<Unmap>", lambda event: Root.on_root_iconify(self, event))
        self.app = App(self)
        self.app.mainloop()

    def on_root_deiconify(self, event):
        """
        Show main window if invisible root window is clicked from task bar.
        """
        self.app.deiconify()

    def on_root_iconify(self, event):
        """
        Minimize main window if invisible root window is minimized.
        """
        self.app.withdraw()


class App(tk.Toplevel):
    """
    Main program window.
    * User can press a button to initiate area select mode.
    * User can adjust opacity of select area.
    * User can select target language.
    * User can determine if they would like the translation to appear overlaid
      on the screen grab area or if they would like a separate window to read
      the translation in.
    * User can set time intervals for sampling grab area.
    """

    def __init__(self, master):
        # Create window as a top level. Tk windows are reserved for roots.
        tk.Toplevel.__init__(self, master)

        # Make window spawn in center of screen.
        horizontal_pop = int(self.winfo_screenwidth() / 2 - (self.winfo_reqwidth()) / 2)
        vertical_pop = int(self.winfo_screenheight() / 2 - (self.winfo_reqheight() / 2))
        self.geometry('+{}+{}'.format(horizontal_pop, vertical_pop))
        self.attributes('-topmost', 1)

        # Create custom window title bar to match theme.
        self.overrideredirect(True)
        title_bar = ttk.Frame(self, borderwidth=3)
        # close root to close program
        close_button = ttk.Button(title_bar, text='X', width=1, command=self.master.destroy)
        # minimize self through root
        mini_button = ttk.Button(title_bar, text='__', width=1, command=self.master.iconify)
        window_title = ttk.Label(title_bar, text=title_string)
        title_bar.pack(expand=1)
        close_button.pack(side=tk.RIGHT)
        mini_button.pack(side=tk.RIGHT)
        window_title.pack(side=tk.LEFT)
        # Return drag functionality to custom title bar.
        window_title.bind('<B1-Motion>', lambda event: App.move_window(self, event))
        window_title.bind('<ButtonPress-1>', lambda event: App.click_window(self, event))
        title_bar.bind('<B1-Motion>', lambda event: App.move_window(self, event))
        title_bar.bind('<ButtonPress-1>', lambda event: App.click_window(self, event))
        # Click position on title bar to be used for dragging.
        self.x_pos = 0
        self.y_pos = 0

        # Add screen grab button and bind click + drag motion to it.
        area_select_button = ttk.Button(self, text="Select Area", command=self.screen_grab)
        area_select_button.pack()

        # Screen overlay present during user draw
        self.overlay_window = None
        # Translate area that will remain on screen
        self.grab_window = None
        # Seconds between image grab
        self.time_interval = 5

    def click_window(self, event):
        """
        Helper method for move_window to allow title bar to be dragged by click location and
        not by top left corner.
        """
        self.x_pos = event.x
        self.y_pos = event.y

    def move_window(self, event):
        """
        Allow the main window to be dragged by the title bar despite using overrideredirect.
        """
        self.geometry(f'+{event.x_root - self.x_pos}+{event.y_root - self.y_pos}')

    def screen_grab(self):
        """
        When user presses button to set up translate area, create overlay that covers screen
        and allows user to draw a rectangle.
        """
        self.overlay_window = OverlayWindow(self)

    def create_grab_window(self, stored_values):
        self.overlay_window.destroy()
        self.grab_window = GrabWindow(stored_values, self)
        # Create thread for the image grabbing window loop.
        threading.Thread(target=GrabWindow.screen_grab_loop, args=self.grab_window).start()


class OverlayWindow(tk.Toplevel):
    """
    Fullscreen overlay that indicates the user is in area select mode. Is transparent and covered by
    a canvas that the user can draw a rectangle on. Window will close itself once rectangle is complete
    and a new screen grab window will spawn in the location of the rectangle selection.
    """

    def __init__(self, master):
        tk.Toplevel.__init__(self, master)

        # Clear old screen grab windows if any exist.
        if self.master.grab_window is not None:
            self.master.grab_window.destroy()
            self.master.grab_window = None

        # Map containing first click location and release location.
        self.stored_values = {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0}

        # Rectangle that user will draw
        self.rect = None

        # Create screen overlay to alert user that they are in drag mode.
        self.attributes('-fullscreen', True, '-alpha', 0.3, '-topmost', True)
        # prevent window from being closed by regular means, only guaranteed to work in Windows
        self.overrideredirect(True)

        # Create canvas, bind left click down, drag, and release.
        self.cv = tk.Canvas(self, cursor="cross", width=self.winfo_screenwidth(),
                            height=self.winfo_screenheight())
        self.cv.bind("<ButtonPress-1>", lambda event: OverlayWindow.mouse_down(self, event))
        self.cv.bind("<B1-Motion>", lambda event: OverlayWindow.mouse_down_move(self, event))
        self.cv.bind("<ButtonRelease-1>", lambda event: OverlayWindow.mouse_up(self, event))
        self.cv.pack()

    def mouse_down(self, event):
        """
        When mouse clicked on screen overlay window, save location.
        If rectangle not made yet, make rectangle so user can see where they are selecting.
        """

        self.stored_values['x1'] = event.x
        self.stored_values['y1'] = event.y
        self.rect = self.cv.create_rectangle(self.stored_values['x1'],
                                             self.stored_values['y1'], 1, 1, fill="")

    def mouse_down_move(self, event):
        """
        As mouse moves on screen overlay window while left click held down, save and update location.
        Update rectangle so user can see where they are selecting. Will not update if user clicks without
        dragging. The user will have to open another overlay window and drag a new selection window if they
        click without dragging.
        """
        self.stored_values['x2'] = event.x
        self.stored_values['y2'] = event.y
        self.cv.coords(self.rect, self.stored_values['x1'], self.stored_values['y1'],
                       self.stored_values['x2'], self.stored_values['y2'])

    def mouse_up(self, event):
        """
        Create window for screenshot location. Close overlay window.
        """
        App.create_grab_window(self.master, self.stored_values)


class GrabWindow(tk.Toplevel):
    """
    Create a transparent rectangle that displays selected area to be translated.
    Window remains on top of other windows and is not interactable.
    """

    def __init__(self, stored_values, master):
        tk.Toplevel.__init__(self, master)
        self.overrideredirect(1)

        # Determine window location (top left corner) and dimensions.
        self.x_min = min(stored_values['x1'], stored_values['x2'])
        self.y_min = min(stored_values['y1'], stored_values['y2'])
        self.x_width = abs(stored_values['x1'] - stored_values['x2'])
        self.y_height = abs(stored_values['y1'] - stored_values['y2'])
        dimensions = str(self.x_width) + "x" + str(self.y_height) + "+" + str(self.x_min) + "+" + str(self.y_min)
        self.geometry(dimensions)

        # Set window transparent and add a canvas, then use set_click_through to make canvas
        # not interactable
        self.attributes("-alpha", 0.5)
        self.attributes('-transparentcolor', 'white', '-topmost', 1)
        self.config(bg='white')
        self.cv = tk.Canvas(self, bg='white', highlightthickness=0)
        self.cv.pack()
        hwnd = self.cv.winfo_id()
        GrabWindow.set_click_through(hwnd)

        img = ImageGrab.grab(bbox=(self.x_min, self.y_min, self.x_min + self.x_width, self.y_min + self.y_height))
        text = pt.image_to_string(img)
        print(text) # TODO remove

    def screen_grab_loop(self):
        while self is not None:
            sleep(self.master.time_interval)
            # Use pillow to grab image in screen grab box
            img = ImageGrab.grab(bbox=(self.x_min, self.y_min, self.x_min + self.x_width, self.y_min + self.y_height))
            text = pt.image_to_string(img)
            print(text)  # TODO remove

    def set_click_through(hwnd):
        """
        Make screen grab window not interactable.
        """
        try:
            styles = WS_EX_LAYERED | WS_EX_TRANSPARENT
            SetWindowLong(hwnd, GWL_EXSTYLE, styles)
            SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    root = Root()

    # TODO perform screen grab on window and save image as variable every 5s
    # TODO use pytesseract to change image to text and google translate api to translate
