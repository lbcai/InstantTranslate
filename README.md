# InstantTranslate
Screengrabbing real time translator tool written in Python 3.8 with tkinter, Pillow, googletrans and pytesseract libraries.

This space will be updated once project is complete.

## 05/27/22 Notes
One interesting challenge of writing a desktop application that is more complex than previous applications I've written is that trying to perform multiple tasks at once with the user interface reduces usability. For example, my program would hang if I included a while loop. I turned to multithreading to find a solution for this and I've learned that there isn't a reason to close threads in general. You can't reopen them. I also noticed that after I added threads, my program would not actually close after I closed the main window, so I added a global variable to shut down threads that I could toggle when the program was closed. I read that this is best practice for closing threads and that you should avoid stopping threads in unclean ways because they might not release their resources (for example, using Daemon threads). It turns out that I can use a threading.Event() in the same way to cleanly close a thread.

Also, you should keep track of what you are doing and make sure you don't allow unlimited thread opening. I attached a thread to instances of windows that could be opened and closed, and suddenly I had five threads when I only meant to have two open at once!

Another interesting thing to note for a new programmer is that Python itself can have bugs. I ran into an issue where I was trying to determine what the user was interacting with on my interface, but the Combobox dropdown menu in tkinter has a popdown arrow that isn't accounted for in the focus_get() method. See this <a href="https://stackoverflow.com/questions/67542487/exception-keyerror-if-call-focus-get-when-down-arrow-clicked-on-widget-combo">link</a> for more information.

I also read for a tkinter program, it's good practice to separate windows into classes so things are cleaner and more scalable in the future. A goal of mine is to write much nicer code. I'll probably have to go back and refactor some of this later.
