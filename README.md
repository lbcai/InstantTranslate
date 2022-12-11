# InstantTranslate
Screengrabbing real time translator tool written in Python 3.8 with tkinter, Pillow, googletrans and pytesseract libraries.

## Usage
<p align="center" width="100%">
  <img src="icons/mainmenu.PNG?raw=true" alt="Main menu.">
</p>
Opening the executable pulls up the main menu. 

Functionality:
* Select languages to translate to or from. If no translate from language is selected, the program will attempt to guess what language to translate from based on input.
* Select sample rate of selection. If translating quickly moving text, increase the sample rate. If updates to the text are rare, lowering the sample rate will increase performance, but this is optional. Sample rate defaults to 1 image taken for translation every 1 second.
* Change the opacity of the selection window. This will allow users to see beneath the window to the original text or hide the selection window entirely (works best with text window).
* Open text window or invert the color of the selection window (black background with white text is the default). These options are disabled unless a selection window is open.
* Select Area button allows user to drag over an area on the screen to create a selection window there.
* Image Options button allows user to adjust image post-processing options to help improve translation quality. This is disabled unless a selection window is open.
* Close Windows button closes all windows except for the main menu window (selection window, text window).

## Example
<p align="center" width="100%">
  <img src="icons/step0.png?raw=true" alt="Creating a selection window.">
</p>
  Open the program and use the Select Area button to create a selection window around the section of the screen that contains the text to be translated.  

### Selection Window
<p align="center" width="100%">
  <img src="icons/step1.PNG?raw=true" alt="Image of selection window.">
</p>
The selection window defaults to white text on a black background with 50% opacity. Use the opacity slider to change the selection window, which displays the translated text. Increase the opacity to cover the original text and more easily read the translated text. 

Lower the opacity to hide the selection window. This option is best used with the text window. If the text window is opened, the selection window will no longer contain translated text. Instead, the translated text can be viewed on the text window (see below).

<p align="center" width="100%">
  <img src="icons/step5.PNG?raw=true" alt="Image of selection window with other options.">
</p>

### Options Window  
<p align="center" width="100%">
  <img src="icons/step2.PNG?raw=true" alt="Image of options window.">
</p>
Select Image Options from the main menu. A window will pop up above the main menu and allow the user to choose post-processing options for the sampled text.

* Change the Threshold Value to make the sampled text black and white and change the contrast versus the background. This may help in some cases where there are too many subtle variations in image value to get a clear translation.
* Change the Scale Multiplier of the image to increase the size of the sampled text. In many cases, this helps improve translation.
* Invert the colors of the image if necessary. This may help improve translation quality when combined with other options.
<p align="center" width="100%">
  <img src="icons/step3.PNG?raw=true" alt="Image of options window options at work.">
  <img src="icons/step4.PNG?raw=true" alt="Image of other options window options at work.">
</p>

### Text Window
<p align="center" width="100%">
  <img src="icons/step6.PNG?raw=true" alt="Image of text window.">
</p>
Here, the selection window has been hidden by setting the opacity to 0% and a text window has been opened. There are three tabs on the text window:

* Input: User can type in language of choice and translate to the target language (same as language being translated from in the selection window). There is a button to quickly copy the translated text onto the clipboard.
<p align="center" width="100%">
  <img src="icons/step8.PNG?raw=true" alt="Image of text window input tab.">
</p>

* Translation: User can view the translation of source text seen by the selection window even if the selection window is transparent. There is also a button to quickly copy the translated text onto the clipboard.
<p align="center" width="100%">
  <img src="icons/step7.PNG?raw=true" alt="Image of text window translation tab.">
</p>

* Source Text: User can view the source text seen by the selection window directly. There is also a button to quickly copy the translated text onto the clipboard. This is useful in cases where the source text is not copy and pastable, such as in cases where the text is part of an image.
<p align="center" width="100%">
  <img src="icons/step6.PNG?raw=true" alt="Image of text window source text tab.">
</p>
