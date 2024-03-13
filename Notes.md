## Notes
* Learned about multithreading with Threading library
    * When I began this project, I was so new to programming that I did not
     realize this UI-heavy application would require multithreading to
      maintain responsiveness. This seems like an obvious requirement in
       hindsight.
    * There appear to be best practices and ways to organize code
     that I now understand better. The next time I use multithreading in a
      project, I will plan accordingly.
* Learned about tkinter Python library
    * Got experience working with basic UI elements.
    * Got experience implementing custom window bars (minimization, dragging, closing) and trying a "hacky" solution with invisible root windows to
     give the application a taskbar presence.
    * Got experience with .ico display resolutions and compiling with
     pyinstaller. Compiling into a standalone single .exe was made
      complicated by the inclusion of Tesseract-OCR.
* Worked with other interesting libraries
    * pytesseract - using Tesseract-OCR. Optical image recognition and NN
     training is an interesting and useful field
    * googletrans - Google Translate service
    * pillow - image processing and manipulation library
* Learned more about code organization and object-oriented programming in
 Python
    * The structure of this project was planned on the fly. It would have
     turned out a lot nicer and more separable if I was able to
      conceptualize code structure before beginning. I have begun to
       develop that ability now.
        * Example: I would avoid passing in a class's parent object just so
         I could call the parent methods from the child. I would also prefer
          if code for specific tasks was all in the same area.
 
 This project is now considered complete and unsupported. There are still a
  number of improvements that are possible, especially in performance and
   code quality. If I revisit this
   project in the future, I will likely begin from scratch in the latest
    version of Python.