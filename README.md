# InstantTranslate
Screengrabbing real time translator tool written in Python 3.8 with tkinter, Pillow, googletrans and pytesseract libraries.

## Usage
<p align="center" width="100%">
  <img src="icons/mainmenu.png?raw=true" alt="Main menu.">
</p>
Opening the executable pulls up the main menu. 

Main Menu Functionality:
* Select languages to translate to or from. If no translate from language is selected, the program will attempt to guess what language to translate from based on input.

* Select sample rate of selection. If translating quickly moving text, increase the sample rate. If updates to the text are rare, lower the sample rate. Sample rate defaults to 1 image taken for translation every 1 second.
* Change the opacity of the selection window. This will allow users to see beneath the window to the original text or hide the selection window entirely (works best with text window).
* Open text window or invert the color of the selection window (black background with white text is the default).
* Select Area button allows user to drag over an area on the screen to create a selection window there.
* Image Options button allows user to adjust image post-processing options to help improve translation quality.
* Close Windows button closes all windows except for the main menu window (selection window, text window).
