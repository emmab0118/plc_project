import os
import tkinter
from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
from syntax import SyntaxHighlighter

class Notepad:
    __root = Tk()

    # default window width and height
    __thisWidth = 300
    __thisHeight = 300
    __thisTextArea = Text(__root)
    __thisMenuBar = Menu(__root)
    __thisFileMenu = Menu(__thisMenuBar, tearoff=0)
    __thisEditMenu = Menu(__thisMenuBar, tearoff=0)
    __thisScrollBar = Scrollbar(__thisTextArea)
    __file = None

    def __init__(self, **kwargs):
        # set window size 
        try:
            self.__thisWidth = kwargs['width']
        except KeyError:
            pass

        try:
            self.__thisHeight = kwargs['height']
        except KeyError:
            pass

        # set the window text
        self.__root.title("Untitled - Notepad")

        # center window
        screenWidth = self.__root.winfo_screenwidth()
        screenHeight = self.__root.winfo_screenheight()

        left = (screenWidth / 2) - (self.__thisWidth / 2)
        top = (screenHeight / 2) - (self.__thisHeight / 2)

        self.__root.geometry('%dx%d+%d+%d' % (self.__thisWidth, self.__thisHeight, left, top))

        # make the textarea auto resizable
        self.__root.grid_rowconfigure(0, weight=1)
        self.__root.grid_columnconfigure(0, weight=1)

        # add controls (widget)
        self.__thisTextArea.grid(sticky=N+E+S+W)
        
        # Initialize syntax highlighter
        self.highlighter = SyntaxHighlighter(self.__thisTextArea)
        
        # Bind events for syntax highlighting
        self.__thisTextArea.bind('<KeyRelease>', self.highlighter.highlight_syntax)

        self.__thisFileMenu.add_command(label="New", command=self.__newFile)
        self.__thisFileMenu.add_command(label="Open", command=self.__openFile)
        self.__thisFileMenu.add_command(label="Save", command=self.__saveFile)
        self.__thisFileMenu.add_separator()
        self.__thisFileMenu.add_command(label="Exit", command=self.__quitApplication)
        self.__thisMenuBar.add_cascade(label="File", menu=self.__thisFileMenu)

        self.__thisEditMenu.add_command(label="Cut", command=self.__cut)
        self.__thisEditMenu.add_command(label="Copy", command=self.__copy)
        self.__thisEditMenu.add_command(label="Paste", command=self.__paste)
        self.__thisMenuBar.add_cascade(label="Edit", menu=self.__thisEditMenu)
        
        self.__root.config(menu=self.__thisMenuBar)

        self.__thisScrollBar.pack(side=RIGHT, fill=Y)
        self.__thisScrollBar.config(command=self.__thisTextArea.yview)
        self.__thisTextArea.config(yscrollcommand=self.__thisScrollBar.set)

    def __quitApplication(self):
        self.__root.destroy()

    def __openFile(self):
        self.__file = askopenfilename(defaultextension=".txt",
                                    filetypes=[("All Files", "*.*"), 
                                                ("Text Documents", "*.txt"),
                                                ("Python Files", "*.py")])

        if self.__file == "":
            # no file to open
            self.__file = None
        else:
            # try to open the file and set the window title
            self.__root.title(os.path.basename(self.__file) + " - Notepad")
            self.__thisTextArea.delete(1.0, END)

            with open(self.__file, "r") as file:
                self.__thisTextArea.insert(1.0, file.read())
            
            # Apply syntax highlighting after loading
            self.highlighter.highlight_syntax()

    def __newFile(self):
        self.__root.title("Untitled - Notepad")
        self.__file = None
        self.__thisTextArea.delete(1.0, END)

    def __saveFile(self):
        # creating new file if no file is currently open
        if self.__file is None:
            # save as new file
            self.__file = asksaveasfilename(initialfile='Untitled.txt',
                                            defaultextension=".txt",
                                            filetypes=[("All Files", "*.*"),
                                                    ("Text Documents", "*.txt"),
                                                    ("Python Files", "*.py")])

            if self.__file == "":
                self.__file = None
            else:
                # try to save the file
                with open(self.__file, "w") as file:
                    file.write(self.__thisTextArea.get(1.0, END))
                # change the window title
                self.__root.title(os.path.basename(self.__file) + " - Notepad")
                
        # save existing file
        else:
            with open(self.__file, "w") as file:
                file.write(self.__thisTextArea.get(1.0, END))

    def __cut(self):
        self.__thisTextArea.event_generate("<<Cut>>")

    def __copy(self):
        self.__thisTextArea.event_generate("<<Copy>>")

    def __paste(self):
        self.__thisTextArea.event_generate("<<Paste>>")

    def run(self):
        self.__root.mainloop()


# run the notepad
notepad = Notepad(width=600, height=400)
notepad.run()
