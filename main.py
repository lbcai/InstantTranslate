# for GUI
import _tkinter
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
# for click through screen grab window
from win32gui import SetWindowLong, SetLayeredWindowAttributes
from win32con import WS_EX_LAYERED, WS_EX_TRANSPARENT, GWL_EXSTYLE, LWA_ALPHA
# for image taking and text conversion
from PIL import ImageGrab, ImageTk, ImageChops
import pytesseract as pt
# for running image taking while keeping program running
from time import sleep
from threading import Thread
# for translation
from googletrans import Translator, LANGUAGES

title_string = "InstantTranslate 1.0"
# Flag for screen grab thread to stop after program closes.
stop_threads = False
# pytesseract requires tesseract exe, location provided for bundling with pyinstaller package
pt.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'

# List of languages (capitalized)
language_list = list(LANGUAGES.values())
for i in range(len(language_list)):
    language_list[i] = language_list[i].capitalize()
    if " " in language_list[i]:
        broken_string = language_list[i].split()
        if "(" in broken_string[1]:
            broken_string[1] = broken_string[1][1::].capitalize()
            broken_string[1] = "(" + broken_string[1]
        else:
            broken_string[1] = broken_string[1].capitalize()
        fixed_string = broken_string[0] + " " + broken_string[1]
        language_list[i] = fixed_string


def update_lang_dict():
    j = 0
    for key in LANGUAGES:
        LANGUAGES[key] = language_list[j]
        j += 1


def stop_threads_true():
    """
    Exit all threads on program exit.
    """
    global stop_threads
    stop_threads = True


def center_window(self, boolean=True):
    """
    Spawn new window in center of screen. Default to True for main window, False for other windows
    will cause them to center on the main window and not the screen.
    """
    if boolean is True:
        self.tk.eval(f'tk::PlaceWindow {self._w} center')
    else:
        self.tk.eval(f'tk::PlaceWindow {self._w} widget {self.master}')
    self.attributes('-topmost', True)


def set_click_through(hwnd):
    """
    Make screen grab window not interactable.
    """
    try:
        styles = WS_EX_LAYERED | WS_EX_TRANSPARENT
        SetWindowLong(hwnd, GWL_EXSTYLE, styles)
        SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA)
    except Exception:
        pass


def make_title_bar(self):
    """
    Use to make custom title bar that matches visual theme of the program.
    """
    # Create custom window title bar to match theme.
    self.overrideredirect(True)
    title_bar = ttk.Frame(self, borderwidth=3)
    # close root to close program if on main window, else close window for toplevel windows
    if isinstance(self, App):
        close_button = ttk.Button(title_bar, text='X', width=1,
                                  command=lambda: [self.close_other_windows(), self.master.destroy(),
                                                   stop_threads_true()])
    else:
        close_button = ttk.Button(title_bar, text='X', width=1,
                                  command=self.reset_master_box)

    window_title = ttk.Label(title_bar, text=title_string)
    title_bar.pack(expand=False, fill=tk.X, side=tk.TOP)
    close_button.pack(side=tk.RIGHT)

    # minimize self through root
    if isinstance(self, App):
        mini_button = ttk.Button(title_bar, text='__', width=1, command=self.master.iconify)
        mini_button.pack(side=tk.RIGHT)
    else:
        mini_button = ttk.Button(title_bar, text='__', width=1, command=self.hidden_window.iconify)
        mini_button.pack(side=tk.RIGHT)

    window_title.pack(side=tk.LEFT)
    # Return drag functionality to custom title bar.
    window_title.bind('<B1-Motion>', lambda event: App.move_window(self, event))
    window_title.bind('<ButtonPress-1>', lambda event: App.click_window(self, event))
    title_bar.bind('<B1-Motion>', lambda event: App.move_window(self, event))
    title_bar.bind('<ButtonPress-1>', lambda event: App.click_window(self, event))

    # Divide the title bar space off from the main window space.
    separator = tk.Frame(self, height=1, borderwidth=0, bg='#373737')
    separator.pack(fill=tk.X, padx=5)
    separator_underline = tk.Frame(self, height=1, borderwidth=0, bg='#414141')
    separator_underline.pack(fill=tk.X, padx=5)


def toggle_slider(boolean, slide):
    """
    Use to disable or enable horizontal sliders depending on user specification through checkboxes.
    """
    if boolean is True:
        slide.config(state='enabled')
    else:
        slide.config(state='disabled')


def update_display(label, boolean, tag="", int_flag=True):
    """
    Updates number displayed alongside horizontal slide bars.
    Use int_flag to specify int or float conversions (floats will display with 1 decimal point).
    """
    if int_flag is True:
        label.config(text=f"{tag}{int(boolean)}")
    else:
        label.config(text=f"{tag}{round(float(boolean), 1)}")


class IntegerEntry(ttk.Entry):
    """
    Entry box that checks for integer input and overwrites invalid input.
    Used to determine sample time of grab window.
    """

    def __init__(self, master, string):
        self.var = tk.StringVar(value=string)
        ttk.Entry.__init__(self, master, textvariable=self.var)
        self.reset_value = string
        self.var.trace_add('write', self.check)  # Add observer. On write, check input.
        # Thread for listening while input box is empty.
        self.t = Thread(target=self.check_thread_helper)

    def check(self, *args):
        """
        Used on input to entry box to check input. Only starts thread for listening.
        """
        if not self.t.is_alive():
            self.t.start()

    def check_input(self):
        """
        Actual check input logic for thread to run.
        """
        if self.get().isdigit():
            # Input is numbers, change value to reset to to be current input.
            self.reset_value = self.get()
        else:
            # Input not numbers, replace value with last good input.
            self.delete(0, tk.END)
            self.insert(0, self.reset_value)

    def check_thread_helper(self):
        """
        For thread to run to keep program responsive.
        """
        # If empty, wait until box not in focus to refill so user has time to delete all text and re-enter.
        try:
            while stop_threads is False:
                while self.master.master.focus_get() is self:
                    if self.get() == '':
                        pass
                    else:
                        self.check_input()
                self.check_input()
        except KeyError:  # Python bug, tkinter doesn't understand popdown arrow on Combobox
            pass


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
    * User can open options adjustment window to help pytesseract read text from image.
    * User can close all windows except main window.
    """

    def __init__(self, master):
        # Create window as a top level. Tk windows are reserved for roots.
        tk.Toplevel.__init__(self, master)

        # Make window spawn in center of screen.
        center_window(self)

        # Screen overlay present during user draw
        self.overlay_window = None
        # Translate area that will remain on screen
        self.grab_window = None
        self.grab_opacity = '0.5'
        # Options window for user to adjust image settings for text reading
        self.options_window = None
        # Thread for image grab window
        self.t = None
        # Separate window for translation text
        self.text_window = None
        # Boolean for use thresholding & other options on image
        self.thresholding_boolean = False
        self.threshold = '100'
        self.inversion_boolean = False
        self.resize_boolean = False
        self.resize = '1'
        self.text_window_boolean = tk.BooleanVar()
        self.text_window_boolean.set(False)

        # Click position on title bar to be used for dragging.
        self.x_pos = 0
        self.y_pos = 0
        make_title_bar(self)

        # Add language choice dropdown.
        # Color combobox dropdowns on this window to match Equilux theme.
        self.option_add('*TCombobox*Listbox.background', self['background'])
        self.option_add('*TCombobox*Listbox.foreground', '#a6a6a6')
        # User-determined language to translate into
        self.target_lang = tk.StringVar(self)
        self.target_lang.set('English')  # default value for dropdown is English
        language_frame = ttk.Frame(self)
        language_label = ttk.Label(language_frame, text="Translate to:")
        language_dropdown = ttk.Combobox(language_frame, state='readonly', textvariable=self.target_lang,
                                         values=language_list)
        language_label.pack()
        language_dropdown.pack()
        language_frame.pack(padx=5, pady=5)

        # Add time interval selection for grab window.
        time_selection_frame = ttk.Frame(self)
        time_selection_label = ttk.Label(time_selection_frame, text="Image Sample Interval (sec):")
        self.time_selection_entry = IntegerEntry(time_selection_frame, '1')  # Default sample time is once a second.
        time_selection_label.pack()
        self.time_selection_entry.pack()
        time_selection_frame.pack()

        # Text box option instead of grab window option for text
        self.window_checkbox = ttk.Checkbutton(self, text="Text Window",
                                               variable=self.text_window_boolean, onvalue=True, offvalue=False,
                                               command=self.text_window_generate, state='disabled')
        self.window_checkbox.pack()

        # Change opacity of grab window option
        self.grab_opacity_slide = ttk.Scale(self, from_=0, to=1, orient='horizontal')
        self.grab_opacity_slide.set(self.grab_opacity)
        self.grab_opacity_label = ttk.Label(self, text=f"Selection Opacity: {float(self.grab_opacity_slide.get())}")
        self.grab_opacity_slide.config(command=lambda x: [update_display(self.grab_opacity_label,
                                                                         self.grab_opacity_slide.get(),
                                                                         tag="Selection Opacity: ", int_flag=False),
                                                          self.update_grab_window_opacity()], state='disabled')
        self.grab_opacity_label.pack()
        self.grab_opacity_slide.pack()

        # Add screen grab button and bind click + drag motion to it.
        button_frame = ttk.Frame(self)
        area_select_button = ttk.Button(button_frame, text="Select Area", command=self.screen_grab)
        area_select_button.pack()

        # Add button to open settings adjustment window.
        self.options_button = ttk.Button(button_frame, text="Image Options", command=self.options_window_open,
                                         state='disabled')
        self.options_button.pack()

        # Close other windows button
        close_windows_button = ttk.Button(button_frame, text="Close Windows", command=self.close_other_windows)
        close_windows_button.pack()

        button_frame.pack(padx=5, pady=5)

    def update_grab_window_opacity(self):
        """
        Change grab window opacity in real time with slider.
        """
        self.grab_opacity = self.grab_opacity_slide.get()
        self.grab_window.attributes("-alpha", float(self.grab_opacity))

    def text_window_generate(self):
        """
        Open or close separate window to display translated text.
        """
        if self.text_window_boolean.get() is False:
            self.text_window.destroy()
        else:
            self.text_window = TextWindow(self)

    def close_other_windows(self):
        """
        From main app window, close other extra windows and close threads.
        """
        if self.overlay_window is not None and self.overlay_window.winfo_exists():
            self.overlay_window.destroy()
        if self.grab_window is not None and self.grab_window.winfo_exists():
            self.grab_window.destroy()
            self.options_button_disable(True)
        if self.options_window is not None and self.options_window.winfo_exists():
            self.options_window.destroy()
        if self.text_window is not None and self.text_window.winfo_exists():
            self.text_window.destroy()

    def options_button_disable(self, boolean):
        """
        Disable options menu, text window checkbox, opacity slider unless grab window exists.
        """
        if boolean is False:
            self.options_button.config(state='normal')
            self.window_checkbox.config(state='normal')
            self.grab_opacity_slide.config(state='normal')
        else:
            self.options_button.config(state='disabled')
            self.window_checkbox.config(state='disabled')
            self.grab_opacity_slide.config(state='disabled')

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

    def options_window_open(self):
        """
        Open window to allow user to adjust image options. Options affect whether pytesseract can process
        text from screen grab.
        """
        self.options_window = OptionsWindow(self)
        # Stop user from interacting with main window until options are closed.
        self.options_window.grab_set()
        self.options_window.wait_window()

    def screen_grab(self):
        """
        When user presses button to set up translate area, create overlay that covers screen
        and allows user to draw a rectangle.
        """
        self.overlay_window = OverlayWindow(self)

    def create_grab_window(self, stored_values):
        """
        Create screen grab window after overlay window used to draw rectangle.
        """
        self.overlay_window.destroy()
        self.grab_window = GrabWindow(stored_values, self)
        # Create thread for the image grabbing window loop.
        self.t = Thread(target=GrabWindow.screen_grab_loop, args=(self.grab_window,))
        if not self.t.is_alive():
            self.t.start()

# TODO any windows in the program over the translation spot should be hidden during screenshot
# TODO test with text of different sizes


class TextWindowHidden(tk.Toplevel):
    """
    Hidden window to make text window minimizable and show up on task bar.
    """
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.attributes('-alpha', 0.0)
        self.bind("<Unmap>", lambda event: self.on_iconify(event))
        self.bind("<Destroy>", lambda event: self.on_destroy(event))
        self.bind("<FocusIn>", lambda event: self.on_deiconify(event))

    def on_destroy(self, event):
        """
        When hidden window is destroyed from taskbar, also destroy text window and reset master check box.
        """
        self.master.reset_master_box()

    def on_deiconify(self, event):
        """
        Show main window if invisible root window is clicked from task bar.
        """
        self.master.deiconify()

    def on_iconify(self, event):
        """
        Minimize main window if invisible root window is minimized.
        """
        self.master.withdraw()


class TextWindow(tk.Toplevel):
    """
    Window to display translated text if user selects option to use.
    """

    def __init__(self, master):
        tk.Toplevel.__init__(self, master)

        self.hidden_window = TextWindowHidden(self)

        self.size()

        # Click position on title bar to be used for dragging.
        self.x_pos = 0
        self.y_pos = 0
        make_title_bar(self)

        self.translation = self.master.grab_window.get_translation()
        self.text = self.master.grab_window.get_text()
        self.target_lang = ''
        self.src_lang = ''

        main_frame = ttk.Frame(self)

        text_frame = ttk.Frame(main_frame)
        self.lang_label = ttk.Label(text_frame, text=self.src_lang)
        self.lang_label.pack(side=tk.TOP)
        self.text_label = ttk.Label(text_frame, text=self.text)
        self.text_label.pack(side=tk.BOTTOM, pady=5)
        text_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Separator for looks
        separator = tk.Frame(main_frame, width=1, borderwidth=0, bg='#373737')
        separator.pack(fill=tk.Y, pady=5, side=tk.LEFT)
        separator_underline = tk.Frame(main_frame, width=1, borderwidth=0, bg='#414141')
        separator_underline.pack(fill=tk.Y, pady=5, side=tk.LEFT)

        trans_frame = ttk.Frame(main_frame)
        self.target_label = ttk.Label(trans_frame, text=self.target_lang)
        self.target_label.pack(side=tk.TOP)
        self.translation_label = ttk.Label(trans_frame, text=self.translation)
        self.translation_label.pack(side=tk.BOTTOM, pady=5)
        trans_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True, side=tk.RIGHT)

        main_frame.pack(fill=tk.BOTH, expand=True)

    def size(self):
        """
        Set window dimensions.
        """
        dimensions = self.master.grab_window.return_size().replace('x', '+')
        dimensions_array = dimensions.split('+')
        # Add headspace for title bar in window size
        self.geometry(
            f'{int(dimensions_array[0]) * 2}x{int(dimensions_array[1]) + 36}+'
            f'{dimensions_array[2]}+{int(dimensions_array[3]) - 36}')

    def reset_master_box(self):
        """
        On close, reset master's checkbox to match state of window (closed).
        """
        self.master.text_window_boolean.set(False)
        self.destroy()

    def update_translation(self):
        self.text = self.master.grab_window.get_text()
        self.text_label.config(text=self.text)
        self.translation = self.master.grab_window.get_translation()
        self.translation_label.config(text=self.translation)
        self.target_lang = self.master.grab_window.get_target_lang()
        self.target_label.config(text=self.target_lang)
        self.src_lang = self.master.grab_window.get_src_lang()
        self.lang_label.config(text=self.src_lang)


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
        Create window for screenshot location. Close overlay window. Resize text window if option is up.
        """
        App.create_grab_window(self.master, self.stored_values)
        if self.master.text_window is not None:
            if self.master.text_window.winfo_exists():
                self.master.text_window.size()


class GrabWindow(tk.Toplevel):
    """
    Create a transparent rectangle that displays selected area to be translated.
    Window remains on top of other windows and is not interactable.
    """

    def __init__(self, stored_values, master):
        tk.Toplevel.__init__(self, master)
        self.overrideredirect(True)

        # Enable options button in main app window
        App.options_button_disable(self.master, False)

        # Determine window location (top left corner) and dimensions.
        self.x_min = min(stored_values['x1'], stored_values['x2'])
        self.y_min = min(stored_values['y1'], stored_values['y2'])
        self.x_width = abs(stored_values['x1'] - stored_values['x2'])
        self.y_height = abs(stored_values['y1'] - stored_values['y2'])
        dimensions = str(self.x_width) + "x" + str(self.y_height) + "+" + str(self.x_min) + "+" + str(self.y_min)
        self.geometry(dimensions)

        # Set window transparent and add a canvas, then use set_click_through to make canvas
        # not interactable
        self.attributes("-alpha", float(self.master.grab_opacity))
        self.attributes('-transparentcolor', 'white', '-topmost', True)
        self.config(bg='white')
        self.cv = tk.Canvas(self, bg='white', highlightthickness=0, width=self.x_width, height=self.y_height)
        self.cv_text = self.cv.create_text(self.x_width // 2, self.y_height // 2, text=" ", fill="black")
        self.cv.pack()
        hwnd = self.cv.winfo_id()
        set_click_through(hwnd)

        # Spawn a translator
        self.trans = Translator()
        self.translation = ''
        self.src_lang = ''

        # Make a raw image for viewing and an img for running translator on to prevent logic shenanigans with
        # options checkboxes.
        self.img_raw = ImageGrab.grab(bbox=(self.x_min, self.y_min, self.x_min + self.x_width, self.y_min +
                                            self.y_height))
        self.img = self.img_raw.copy()
        self.text = pt.image_to_string(self.img)
        GrabWindow.translate(self)

    def get_translation(self):
        return self.translation

    def get_text(self):
        return self.text

    def get_target_lang(self):
        return self.master.target_lang.get()

    def get_src_lang(self):
        return LANGUAGES[self.src_lang]

    def translate(self):
        """
        Apply translation to grab window unless the user selected a separate window to hold the translation.
        Then it will be applied there.
        """
        if self.text is not None:
            translation_obj = self.trans.translate(self.text, dest=self.master.target_lang.get(), src='auto')
            self.translation = translation_obj.text
            self.src_lang = translation_obj.src
            if self.master.text_window_boolean.get() is False:
                self.cv.itemconfig(self.cv_text, text=self.translation)
            else:
                self.cv.itemconfig(self.cv_text, text='')

    def return_size(self):
        """
        Use for making translation text box if user has that option selected in main program.
        """
        return str(self.x_width) + "x" + str(self.y_height) + "+" + str(self.x_min) + "+" + str(self.y_min)

    def screen_grab_loop(self):
        while stop_threads is False:
            try:
                if not self.master.time_selection_entry.get().isdigit():
                    sleep_time = int('5')
                else:
                    sleep_time = int(self.master.time_selection_entry.get())
                sleep(sleep_time)
                # Use pillow to grab image in screen grab box

                self.cv.pack_forget()  # Temporarily unpack canvas to take a nice image of the text.
                self.img_raw = \
                    ImageGrab.grab(bbox=(self.x_min, self.y_min,
                                         self.x_min + self.x_width, self.y_min + self.y_height))
                self.img = self.img_raw.copy()
                self.cv.pack()  # Repack canvas so user can see the window again.

                if self.master.resize_boolean is True:
                    width = self.img.width * int(self.master.resize)
                    height = self.img.height * int(self.master.resize)
                    self.img = self.img.resize((width, height))

                if self.master.thresholding_boolean is True:
                    self.img = self.img.convert("L")  # Grayscale
                    # PIL thresholding: white if above threshold, black otherwise
                    self.img = self.img.point(lambda p: 255 if p > int(self.master.threshold) else 0)
                    self.img = self.img.convert("1")  # Monochromatic

                if self.master.inversion_boolean is True:
                    self.img = ImageChops.invert(self.img)

                if self.master.text_window_boolean.get() is True:
                    self.master.text_window.update_translation()  # ugly but wanted to avoid more threads...

                self.text = pt.image_to_string(self.img)
                GrabWindow.translate(self)
            except RuntimeError:
                break
            except _tkinter.TclError:
                break


class OptionsWindow(tk.Toplevel):
    """
    Window that shows user what image pytesseract is seeing for text extraction and allows
    user to adjust settings to make text extraction easier.
    """

    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.overrideredirect(True)

        # Define variables that will be used below to pass options back up to main program.
        self.thresholding_boolean_var = tk.BooleanVar()
        self.thresholding_boolean_var.set(self.master.thresholding_boolean)
        self.inversion_boolean_var = tk.BooleanVar()
        self.inversion_boolean_var.set(self.master.inversion_boolean)
        self.resize_boolean_var = tk.BooleanVar()
        self.resize_boolean_var.set(self.master.resize_boolean)

        # Current screen grab image and scroll bars
        self.img = self.master.grab_window.img

        limited_img_height = self.img.size[0]  # width
        limited_img_width = self.img.size[1]  # height
        if limited_img_height > 400:
            limited_img_height = 400
        if limited_img_width > 400:
            limited_img_width = 400
        self.image_frame = ttk.Frame(self, height=limited_img_height, width=limited_img_width)  # Limit canvas size
        # TODO FIX SLIDE BAR SPAWN
        # Scroll bar configs
        self.xbar = ttk.Scrollbar(self.image_frame, orient=tk.HORIZONTAL)
        self.ybar = ttk.Scrollbar(self.image_frame)
        self.image_panel = tk.Canvas(self.image_frame, highlightthickness=0, height=self.img.size[1],
                                     width=self.img.size[0], xscrollcommand=self.xbar.set, yscrollcommand=self.ybar.set)
        self.xbar.config(command=self.image_panel.xview)
        self.ybar.config(command=self.image_panel.yview)
        self.xbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.ybar.pack(side=tk.RIGHT, fill=tk.Y)

        # Pack image-containing canvas
        self.image_panel.config(scrollregion=self.image_panel.bbox(tk.ALL))
        self.image_panel.pack()
        self.image_frame.pack_propagate(False)  # Don't grow if canvas is large
        self.image_frame.pack(expand=True, fill=tk.BOTH)

        # Image adjustment settings - create checkboxes and fields
        # Thresholding
        self.adjustment_frame = ttk.Frame(self)
        thresholding_checkbox = ttk.Checkbutton(self.adjustment_frame, text="Thresholding",
                                                variable=self.thresholding_boolean_var, onvalue=True, offvalue=False,
                                                command=lambda: [self.refresh_image(),
                                                                 toggle_slider(self.thresholding_boolean_var.get(),
                                                                               self.thresholding_input_slide)])
        thresholding_checkbox.pack()
        self.thresholding_input_slide = ttk.Scale(self.adjustment_frame, from_=0, to=100, orient='horizontal')
        self.thresholding_input_slide.set(self.master.threshold)
        self.thresholding_label = ttk.Label(self.adjustment_frame,
                                            text=f"Threshold Value: {int(self.thresholding_input_slide.get())}")
        self.thresholding_input_slide.config(command=lambda x: [update_display(self.thresholding_label,
                                                                               self.thresholding_input_slide.get(),
                                                                               tag="Threshold Value: "),
                                                                self.refresh_image()])
        self.thresholding_label.pack()
        self.thresholding_input_slide.pack()
        toggle_slider(self.thresholding_boolean_var.get(), self.thresholding_input_slide)

        # Resize
        resize_checkbox = ttk.Checkbutton(self.adjustment_frame, text="Scale",
                                          variable=self.resize_boolean_var, onvalue=True, offvalue=False,
                                          command=lambda: [self.refresh_image(),
                                                           toggle_slider(self.resize_boolean_var.get(),
                                                                         self.resize_input_slide)])
        resize_checkbox.pack()
        self.resize_input_slide = ttk.Scale(self.adjustment_frame, from_=1, to=8, orient='horizontal')
        self.resize_input_slide.set(self.master.resize)
        self.resize_label = ttk.Label(self.adjustment_frame,
                                      text=f"Scale Multiplier: {int(self.resize_input_slide.get())}")
        self.resize_input_slide.config(command=lambda x: [update_display(self.resize_label,
                                                                         self.resize_input_slide.get(),
                                                          tag="Scale Multiplier: "),
                                                          self.refresh_image()])
        self.resize_label.pack()
        self.resize_input_slide.pack()
        toggle_slider(self.resize_boolean_var.get(), self.resize_input_slide)

        # Invert
        self.inversion_checkbox = ttk.Checkbutton(self.adjustment_frame, text="Invert",
                                                  variable=self.inversion_boolean_var, onvalue=True, offvalue=False,
                                                  command=self.refresh_image)
        self.inversion_checkbox.pack()
        self.adjustment_frame.pack()

        buttons_frame = ttk.Frame(self)
        buttons_frame.pack()
        # Button to update settings
        save_button = ttk.Button(buttons_frame, text="Save", command=lambda: [self.push_options(), self.destroy()])
        save_button.pack(side=tk.LEFT)
        # Button to close window
        close_button = ttk.Button(buttons_frame, text="Exit", command=self.destroy)
        close_button.pack(side=tk.RIGHT)

        center_window(self, False)

        # Actual first image spawn
        self.refresh_image()

    def push_options(self):
        """
        Use when saving options. Push options to main program window.
        """
        # Make sure we are getting a number, else don't save input.
        self.master.threshold = self.thresholding_input_slide.get()
        self.master.thresholding_boolean = self.thresholding_boolean_var.get()

        self.master.resize = self.resize_input_slide.get()
        self.master.resize_boolean = self.resize_boolean_var.get()

        self.master.inversion_boolean = self.inversion_boolean_var.get()

    def refresh_image(self):
        """
        Use when options are adjusted or window spawned. Unpack and repack image canvas with new image.
        """
        # self.img = ImageTk.PhotoImage(self.master.grab_window.img)
        self.img = self.master.grab_window.img_raw

        if self.resize_boolean_var.get() is True:
            width = self.img.size[0] * int(self.resize_input_slide.get())
            height = self.img.size[1] * int(self.resize_input_slide.get())
            self.img = self.img.resize((width, height))
            self.image_panel.config(height=self.img.size[1], width=self.img.size[0])

        if self.thresholding_boolean_var.get() is True:
            self.img = self.img.convert("L")  # Grayscale
            # PIL thresholding: white if above threshold, black otherwise
            self.img = self.img.point(lambda p: 255 if p > int(self.thresholding_input_slide.get()) else 0)
            self.img = self.img.convert("1")  # Monochromatic

        if self.inversion_boolean_var.get() is True:
            self.img = ImageChops.invert(self.img)

        self.img = ImageTk.PhotoImage(self.img)

        self.image_panel.create_image(self.img.width() // 2, self.img.height() // 2, image=self.img)
        self.image_panel.image = self.img  # Prevent garbage collection of image


# TODO rotation, specify box for border removal, noise removal
# TODO title bar icon
# TODO non letter languages seem to have poor support (eg japanese, chinese) for image recognition. solution?

if __name__ == '__main__':
    update_lang_dict()
    root = Root()
