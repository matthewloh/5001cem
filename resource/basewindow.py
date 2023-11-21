from datetime import datetime, timedelta
import io
import sys
import threading
from tkinter import FLAT, NSEW, Frame, Label
from typing import Dict
from prisma import Base64, Prisma
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.validation import add_regex_validation, validator, add_validation
from nonstandardimports import *
from tkinter import *
from resource.static import *
from PIL import Image, ImageTk, ImageDraw, ImageFont
# https://stackoverflow.com/a/68621773
# This bit of code allows us to remove the window bar present in tkinter
# More information on the ctypes library can be found here:
# https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowlongptrw
# https://learn.microsoft.com/en-us/windows/win32/winmsg/window-styles
# Check if operating system is windows

if sys.platform == "win32":
    # If it is, import the ctypes library
    from ctypes import windll
    # GetWindowLongPtrW is a function that gets the window's parent
    GetWindowLongPtrW = windll.user32.GetWindowLongPtrW
    # SetWindowLongPtrW is a function that sets the window's
    SetWindowLongPtrW = windll.user32.SetWindowLongPtrW


def get_handle(root) -> int:
    root.update_idletasks()
    # This gets the window's parent same as `ctypes.windll.user32.GetParent`
    return GetWindowLongPtrW(root.winfo_id(), GWLP_HWNDPARENT)


# user32 = windll.user32
# eventId = None


def gridGenerator(root: Frame, width=None, height=None, color="#dee8e0", overriderelief: bool = False, relief: str = FLAT, name=None):
    for x in range(width):
        root.columnconfigure(x, weight=1, uniform="row")
        if height > width:
            Label(root, width=1, bg=color, relief=relief if overriderelief else FLAT, name=name, autostyle=False).grid(
                row=0, column=x, sticky=NSEW)
    for y in range(height):
        root.rowconfigure(y, weight=1, uniform="row")
        if width >= height:
            Label(root, width=1, bg=color, relief=relief if overriderelief else FLAT, name=name, autostyle=False).grid(
                row=y, column=0, sticky=NSEW)
    return root


class ElementCreator(ttk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgetsDict : Dict[str, Widget|Entry]= {}
        self.imageDict = {}
        self.imagePathDict = {}

    def startPrisma(self):
        try:
            self.mainPrisma = Prisma()
            self.mainPrisma.connect()
            print("Successfully connected to Prisma client.")
        except Exception as e:
            print(e)

    def initMainPrisma(self):
        self.t = threading.Thread(target=self.startPrisma)
        self.t.daemon = True
        self.t.start()

    def pingBackend(self):
        def foo():
            if self.mainPrisma.is_connected:
                self.mainPrisma.execute_raw(
                    """ 
                    SELECT 1;
                    """
                )
            else:
                self.mainPrisma.connect()
        self.t = threading.Thread(target=foo)
        self.t.daemon = True
        self.t.start()
        self.after(1000, self.pingBackend)

    def updateWidgetsDict(self, root: Frame):
        widgettypes = (
            Label,
            Button,
            Frame,
            Canvas,
            Entry,
            Text,
            ScrolledFrame,
            ScrolledText,
        )
        for widgetname, widget in self.children.items():
            if isinstance(widget, widgettypes) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        for widgetname, widget in root.children.items():
            if isinstance(widget, widgettypes) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget

    def createImageReference(self, ipath: str, classname: str):
        # stores a key value pair of "classname" : "ipath"
        self.imagePathDict[classname] = ipath
        # creates a Tkinter image object
        image = ImageTk.PhotoImage(Image.open(ipath))
        # stores a key value pair of "classname" : "image" to prevent garbage collection
        self.imageDict[classname] = image
        return image

    def settingsUnpacker(self, listoftuples, typeoftuple):
        """
        format for labels: (ipath, x, y, classname, root)\n
        format for buttons: (ipath, x, y, classname, root, buttonFunction)\n
        tupletodict creates a dict mapping to the creator functions.
        TODO: enable styling within here
        """
        for i in listoftuples:
            if typeoftuple == "button":
                self.buttonCreator(**self.tupleToDict(i))
            elif typeoftuple == "label":
                self.labelCreator(**self.tupleToDict(i))

    def tupleToDict(self, tup):  # TODO: make this multipurpose
        if len(tup) == 5:
            return dict(zip(("ipath", "x", "y", "classname", "root"), tup))
        if len(tup) == 6:
            return dict(zip(("ipath", "x", "y", "classname", "root", "buttonFunction"), tup))

    def buttonCreator(self, ipath=None, x=None, y=None, classname=None, buttonFunction=None, root=None, relief=FLAT, overrideRelief=FLAT, bg=WHITE, isPlaced=False, useHover=False) -> Button:
        """
        Args:
            ipath (str): path to the image
            x (int): x position of the button
            y (int): y position of the button
            classname (str): name of the button.
            buttonFunction (function): function to be called when the button is clicked.
            root (Frame): the root frame to place the button in.
            isPlaced (bool): whether or not the button is placed.

        Returns:
             Button: the Tkinter button object placed in the root container

        Usage:
            self.controller.buttonCreator(
                ipath=r"\ipath.png", x=0, y=0, 
                classname="classname", root=validtkinterparent (Frame, Canvas, ttk.ScrolledFrame),
                buttonFunction=lambda: function()
            )
        """
        def hoverOnEnter(button, event):
            button.config(relief="raised")

        def unhoverOnLeave(button, event):
            button.config(relief=relief)

        classname = classname.replace(" ", "").lower()
        self.createImageReference(ipath, classname)
        image = self.imageDict[classname]
        widthspan = int(image.width()/20)
        # just the vertical length of the image divided by 20 to get rowspan
        heightspan = int(image.height()/20)
        # the W value of the image divided by 20 to get the column position
        columnarg = int(x/20)
        rowarg = int(y/20)
        if isPlaced:
            placedwidth = int(image.width())
            placedheight = int(image.height())
        button = Button(
            root, image=image, command=lambda: buttonFunction(
            ) if buttonFunction else print(f"This is the {classname} button"),
            relief=relief if not overrideRelief else overrideRelief, bg=bg, width=1, height=1,
            cursor="hand2", state=NORMAL,
            name=classname, autostyle=False
        )
        if isPlaced:
            button.place(x=x, y=y, width=placedwidth,
                         height=placedheight)
        else:
            button.grid(row=rowarg, column=columnarg,
                        rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        if useHover:
            button.bind("<Enter>", lambda e: hoverOnEnter(button, e))
            button.bind("<Leave>", lambda e: unhoverOnLeave(button, e))
        self.updateWidgetsDict(root=root)
        self.widgetsDict[classname].grid_propagate(False)
        return button

    def labelCreator(self, ipath, x, y, classname=None, root=None, overrideRelief=FLAT, isPlaced=False, bg=WHITE) -> Label:
        """
        Args:
            ipath (str): path to the image
            x (int): x position of the label
            y (int): y position of the label
            classname (str): name of the label.
            root (Frame): the root frame to place the label in.
            isPlaced (bool): whether or not the label is placed.

        Returns:
             Label: the label object placed in the root container

        Usage:
            self.controller.labelCreator(
                ipath=r"\ipath.png", x=0, y=0, 
                classname="classname", root=validtkinterparent (Frame, Canvas, ttk.ScrolledFrame),
            )
        """
        classname = classname.replace(" ", "").lower()
        self.createImageReference(ipath, classname)
        image = self.imageDict[classname]
        widthspan = int(image.width()/20)
        # just the vertical length of the image divided by 20 to get rowspan
        heightspan = int(image.height()/20)
        # the W value of the image divided by 20 to get the column position
        columnarg = int(x/20)
        rowarg = int(y/20)
        placedwidth = int(image.width())
        placedheight = int(image.height())
        label = Label(
            root, image=image, relief=FLAT, width=1, height=1,
            state=NORMAL, name=classname,
            autostyle=False, bg=bg
        )
        if isPlaced:
            label.place(x=x, y=y, width=placedwidth, height=placedheight)
        else:
            label.grid(row=rowarg, column=columnarg,
                       rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        self.updateWidgetsDict(root=root)
        return label

    def frameCreator(self, x, y, framewidth, frameheight, root=None, classname=None, bg="#dee8e0", relief=FLAT, imgSettings=None, isPlaced=False) -> Frame:
        classname = classname.replace(" ", "").lower()
        widthspan = int(framewidth / 20)
        heightspan = int(frameheight / 20)
        columnarg = int(x / 20)
        rowarg = int(y / 20)

        frame = Frame(root, width=1, height=1, bg=bg,
                      relief=relief, name=classname, autostyle=False,)
        if isPlaced:
            frame.place(x=x, y=y, width=framewidth, height=frameheight)
        else:
            frame.grid(row=rowarg, column=columnarg, rowspan=heightspan,
                       columnspan=widthspan, sticky=NSEW)
        self.updateWidgetsDict(root=root)
        if imgSettings:
            listofimages = list(enumerate(imgSettings))
        # imgBg is a list of tuples containing (ipath, x, y, name)
        # example = [("Assets\Dashboard\Top Bar.png", 0, 0, "stringwhatever"),] -> 0 ('Assets\\Dashboard\\Top Bar.png', 0, 0, 'stringwhatever')
        for widgetname, widget in root.children.items():
            if widgetname == classname:
                gridGenerator(widget, widthspan, heightspan, bg)
                widget.grid_propagate(False)
                if imgSettings:
                    for i, j in listofimages:
                        # print(j[1] / 20, j[2] / 20)
                        self.buttonCreator(
                            j[0],
                            j[1] - x,
                            j[2] - y,
                            classname=j[3],
                            root=widget,
                            buttonFunction=j[4])
        return frame

    def entryCreator(self, x, y, width, height, root=None, classname=None, bg=WHITE, relief=FLAT, fg=BLACK, textvariable=None, pady=None, font=("Avenir Next Medium", 16), isPlaced=False) -> Entry:
        classname = classname.lower().replace(" ", "")
        columnarg = int(x / 20)
        rowarg = int(y / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        self.updateWidgetsDict(root=root)
        entry = Entry(root, bg=bg, relief=SOLID, font=font, fg=fg, width=1,
                      name=classname, autostyle=False, textvariable=textvariable)
        entry.grid(
            row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW, pady=pady) if not isPlaced else entry.place(
            x=x, y=y, width=width, height=height
        )
        self.updateWidgetsDict(root=root)
        for widgetname, widget in root.children.items():
            if widgetname == classname.lower().replace(" ", ""):
                widget.grid_propagate(False)
        return entry

    def canvasCreator(self, x, y, width, height, root, classname=None, bgcolor=WHITE, imgSettings=None, relief=FLAT, isTransparent=False, transparentcolor=TRANSPARENTGREEN) -> Canvas:
        classname = classname.lower().replace(" ", "")
        columnarg = int(x / 20)
        rowarg = int(y / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        if imgSettings:
            listofimages = list(enumerate(imgSettings))
        canvas = Canvas(root, bg=bgcolor, highlightcolor=bgcolor, relief=FLAT,
                        width=1, height=1, name=classname, highlightthickness=0, autostyle=False)
        canvas.grid(row=rowarg, column=columnarg, rowspan=heightspan,
                    columnspan=widthspan, sticky=NSEW)
        for widgetname, widget in root.children.items():
            if widgetname == classname.lower().replace(" ", ""):
                gridGenerator(widget, widthspan, heightspan, bgcolor)
                widget.grid_propagate(False)
                if isTransparent:
                    hwnd = widget.winfo_id()  # TRANSPARENTGREEN IS the default colorkey
                    transparentcolor = self.hex_to_rgb(transparentcolor)
                    wnd_exstyle = win32gui.GetWindowLong(
                        hwnd, win32con.GWL_EXSTYLE)
                    new_exstyle = wnd_exstyle | win32con.WS_EX_LAYERED
                    win32gui.SetWindowLong(
                        hwnd, win32con.GWL_EXSTYLE, new_exstyle)
                    win32gui.SetLayeredWindowAttributes(
                        hwnd, transparentcolor, 255, win32con.LWA_COLORKEY)
                if imgSettings:
                    for i, j in listofimages:
                        self.buttonCreator(
                            j[0],
                            j[1],
                            j[2],
                            classname=j[3],
                            root=widget,
                            buttonFunction=j[4]
                        )
        self.updateWidgetsDict(root=root)
        return canvas

    def menubuttonCreator(self, x=None, y=None, width=None, height=None, root=None, classname=None, bgcolor=WHITE, relief=FLAT, font=("Helvetica", 16), text=None, variable=None, listofvalues=None, command=None, isPlaced=False) -> ttk.Menubutton:
        """
        Takes in arguments x, y, width, height, from Figma, creates a frame,\n
        and places a menubutton inside of it. The menubutton is then returned into the global dict of widgets.\n
        Requires a var like StringVar() to be initialized and passed in.\n
        Feed in a list of values and command functions to be used in the menubutton.\n
        Styling handled by passing in a formatted classname and font to config a style.
        """
        columnarg = int(x / 20)
        rowarg = int(y / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        classname = classname.lower().replace(" ", "")
        themename = f"{str(root).split('.')[-1]}.TMenubutton"
        # print(themename, classname)
        menustyle = ttk.Style()
        menustyle.configure(
            style=themename, font=("Helvetica", 16),
            background="#FFFFFF", foreground=BLACK,
            bordercolor="#78c2ad",
            relief="raised",
        )
        if themename == "registrationformframe.TMenubutton":
            menustyle.configure(style=themename, background=WHITE,
                                foreground=BLACK, bordercolor="#78c2ad",
                                font=("Helvetica", 12))
            menustyle.map(themename, foreground=[('active', BLACK), ("disabled", BLACK)],
                          background=[('active', WHITE), ("disabled", WHITE)])

        if themename == "apptcreateframe.TMenubutton":
            menustyle.configure(style=themename, background=LIGHTPURPLE,
                                foreground=BLACK, bordercolor=LIGHTPURPLE,
                                font=("Urbanist Medium", 20))
            menustyle.map(themename, foreground=[('active', BLACK), ("disabled", BLACK)],
                          background=[('active', "#ffe3bd"), ("disabled", "#ffe3bd")])
        self.frameCreator(x, y, width, height, root,
                          classname=f"{classname}hostfr", bg=bgcolor, relief=FLAT,
                          isPlaced=isPlaced)
        frameref = self.widgetsDict[f"{classname}hostfr"]
        menubutton = ttk.Menubutton(
            frameref, text=text.title(),
            style=themename,
            name=classname,
            # bootstyle=(DANGER)
        )
        menubutton.grid(row=0, column=0, rowspan=heightspan,
                        columnspan=widthspan, sticky=NSEW)
        menubtnmenu = Menu(
            menubutton, tearoff=0, name=f"{classname}menu",
            bg=LIGHTPURPLE, relief=FLAT, font=("Helvetica", 12),
        )
        for x in listofvalues:
            menubtnmenu.add_radiobutton(label=x, variable=variable, value=x,
                                        command=lambda: [command(), menubutton.config(text=variable.get())])
        menubutton["menu"] = menubtnmenu
        self.widgetsDict[menubutton["menu"]] = menubtnmenu
        self.widgetsDict[classname] = menubutton
        self.updateWidgetsDict(root=root)

        return menubutton

    def timeMenuButtonCreator(self, x=None, y=None, width=None, height=None, root=None, classname=None, bgcolor=WHITE, relief=FLAT, font=("Helvetica", 16), text=None, variable=None,
                              command=None, isPlaced=False,
                              startTime: str = "12:00AM", endTime: str = "12:00PM",
                              interval: int = 30,
                              isTimeSlotFmt: bool = False) -> ttk.Menubutton:
        """ 
        Takes in arguments x, y, width, height, from Figma, creates a menubutton using the menubuttonCreator function,\n
        Similar to the menubuttonCreator function, but takes in a startTime, endTime, and interval to generate a list of timeslots.\n
        """
        start_time = datetime.strptime(startTime, HUMANTIME)
        end_time = datetime.strptime(endTime, HUMANTIME)
        interval = interval
        total_minutes = int((end_time - start_time).total_seconds() / 60)
        time_slots = [(start_time + timedelta(minutes=i*interval)).strftime(HUMANTIME) + ' - ' +
                      (start_time + timedelta(minutes=(i+1)
                       * interval)).strftime(HUMANTIME)
                      for i in range(total_minutes // interval)]

        if not isTimeSlotFmt:
            time_slots = [time.split(' - ')[0] for time in time_slots]

        return self.menubuttonCreator(
            x=x, y=y, width=width, height=height, root=root, classname=classname,
            bgcolor=bgcolor, relief=relief, font=font, text=text, variable=variable,
            command=command, isPlaced=isPlaced, listofvalues=time_slots,
        )

    def ttkEntryCreator(self, x=None, y=None, width=None, height=None, root=None, classname=None, bgcolor=WHITE, relief=FLAT, font=("Helvetica", 16), fg=BLACK, validation=False, passwordchar="*", captchavar=None, isPlaced=False, placeholder=None) -> ttk.Entry:
        """
        Takes in arguments x, y, width, height, from Figma, creates a frame,\n
        and places a ttk.Entry inside of it. The ttk.Entry is then returned into the global dict of widgets.\n
        Requires a var like StringVar() to be initialized and passed in.\n
        Styling handled by passing in a formatted classname and font to config a style.
        """
        classname = classname.lower().replace(" ", "")
        columnarg = int(x / 20)
        rowarg = int(y / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        # entrystyle = ttk.Style()
        # entrystyle.configure(f"{classname}.TEntry", font=font, background=bgcolor, foreground=WHITE)
        frame = self.frameCreator(x, y, width, height, root,
                                  classname=f"{classname}hostfr", bg=bgcolor, relief=FLAT, isPlaced=isPlaced)

        @validator
        def validatePassword(event):
            """
            Validates the password and confirms password entries.
            """
            parentname = str(root).split(".")[-1]
            if self.widgetsDict["regpassent"].get() == "":
                return False
            elif self.widgetsDict["regpassent"].get() == self.widgetsDict[f"regconfpassent"].get():
                return True
            else:
                return False

        @validator
        def validateNRICorPassport(event):
            """
            Validates the NRIC or Passport number.
            """
            if self.widgetsDict["regnricent"].get() == "":
                return False
            elif self.widgetsDict["regnricent"].get().isalnum():
                return True
            else:
                return False

        # themename = f"{str(root).split('.')[-1]}.TEntry"
        # ttk.Style().configure(
        #     style=themename, font=font, background=NICEBLUE, foreground=BLACK,
        # )
        entry = ttk.Entry(frame, bootstyle=PRIMARY, foreground=fg,
                          name=classname, font=font, background=bgcolor)
        entry.grid(row=0, column=0, rowspan=heightspan,
                   columnspan=widthspan, sticky=NSEW)

        if validation == "isPassword":
            entry.config(show=passwordchar)
            add_regex_validation(
                widget=entry, pattern="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,}$")
        elif validation == "isConfPass":
            entry.config(show=passwordchar)
            add_validation(widget=entry, func=validatePassword)
        elif validation == "isEmail":
            add_regex_validation(
                widget=entry, pattern="^[a-zA-Z0-9._%+-]+@(?:student\.newinti\.edu\.my|newinti\.edu\.my)$")
        elif validation == "isContactNo":
            add_regex_validation(
                widget=entry, pattern="^(\+?6?01)[02-46-9]-*[0-9]{7}$|^(\+?6?01)[1]-*[0-9]{8}$")
        elif validation == "isCaptcha":
            add_validation(widget=entry, func=validateCaptcha)
        else:
            # just not blank
            add_regex_validation(widget=entry, pattern="^.*\S.*$")
            pass

        def entryEnter(event):
            entry.config(foreground=BLACK)
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(foreground="#bfbfbf")
            entry.bind("<FocusIn>", lambda e: [[entry.delete(0, END) if entry.get(
            ) == placeholder else None], entry.config(foreground=BLACK)])
            entry.bind("<FocusOut>", lambda e: [entry.insert(0, placeholder), entry.config(
                foreground="#bfbfbf")] if entry.get() == "" else None)

        self.widgetsDict[classname] = entry
        self.updateWidgetsDict(root=root)
        return entry

    def textElement(self, ipath, x, y, classname=None, buttonFunction=None, root=None, relief=FLAT, fg=BLACK, bg=WHITE, font=SFPRO, text=None, size=40, isPlaced=False, yIndex=0, xoffset=0) -> Label | Button:
        classname = classname.replace(" ", "").lower()
        # ~~~ ADD TEXT TO IMAGE FUNCTIONS ~~~
        h = fg.lstrip("#")
        textcolor = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        im = Image.open(ipath)
        font = ImageFont.truetype(font, size)
        draw = ImageDraw.Draw(im)
        # print(im.size) # Returns (width, height) tuple
        xcoord, ycoord = im.size
        # push the text to the right by xoffset pixels
        xcoord = im.size[0]/20 + xoffset*20
        y_offset = size * yIndex  # Vertical offset based on font size and index
        ycoord = ycoord/2 - (font.getbbox(text)[3]/2) + y_offset
        draw.text((xcoord, ycoord), text, font=font, fill=textcolor)
        self.imageDict[f"{classname}"] = ImageTk.PhotoImage(im)
        image = self.imageDict[f"{classname}"]
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        widthspan = int(image.width()/20)
        heightspan = int(image.height()/20)
        columnarg = int(x/20)
        rowarg = int(y/20)
        placedwidth = int(image.width())
        placedheight = int(image.height())

        if buttonFunction:
            if isPlaced:
                element = Button(root, image=image, cursor="hand2", command=lambda: buttonFunction() if buttonFunction else print("No function assigned to button"),
                                 relief=relief, bg=bg, width=1, height=1, name=classname, autostyle=False)
                element.place(x=x, y=y, width=placedwidth,
                              height=placedheight)
            else:
                element = Button(root, image=image, cursor="hand2", command=lambda: buttonFunction() if buttonFunction else print("No function assigned to button"),
                                 relief=relief, bg=bg, width=1, height=1, name=classname, autostyle=False)
                element.grid(row=rowarg, column=columnarg,
                             rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        else:
            if isPlaced:
                element = Label(root, image=image, relief=relief, bg=bg,
                                width=1, height=1, name=classname, autostyle=False)
                element.place(x=x, y=y, width=placedwidth,
                              height=placedheight)
            else:
                element = Label(root, image=image, relief=relief, bg=bg,
                                width=1, height=1, name=classname, autostyle=False)
                element.grid(row=rowarg, column=columnarg,
                             rowspan=heightspan, columnspan=widthspan, sticky=NSEW)

        self.updateWidgetsDict(root=root)
        element.grid_propagate(False)
        return element

    def scrolledTextCreator(self, x=None, y=None, width=None, height=None, root=None, classname=None,
                            bg="#f1feff", hasBorder=False, borderColor=BLACK, padding=0,
                            text=None, font=("Inter", 12), fg=BLACK, isPlaced=True, isDisabled=False, isJustified=False, justification="center",
                            hasVbar=True, hasHbar=False):
        """ 
        Creates a scrolled text widget and returns it.\n
        Uses the place geometry manager by default. Key styling options include enabling padding (disabled by defaut) between the host frame and the text widget, and whether or not the text is justified.\n
        Customization of the border color is also enabled with the hasBorder and borderColor arguments.\n
        Justification options include "left", "center", and "right", and is only enabled when isJustified is set to True by passing in justification.\n
        Background is customized by setting bg which by default also sets the border color of the text to bg.\n

        Args:
            x (int): x position of the text
            y (int): y position of the text
            width (int): width of the text
            height (int): height of the text
            root (Frame): the root frame to place the text in.
            classname (str): name of the text.
            bg (str): background color of the text.
            hasBorder (bool): whether or not the text has a border.
            borderColor (str): color of the border.
            padding (int): padding between the host frame and the text. Default is 0.
            text (str): text to be displayed.
            font (tuple): font and font size of the text widget.
            fg (str): foreground color of the text.
            isPlaced (bool): whether or not the text is placed.
            isDisabled (bool): whether or not the text is disabled.
            isJustified (bool): whether or not the text is justified.
            justification (str): the justification of the text. Defaults to "center".

        Returns:
            ScrolledText: the scrolled text object placed in the root container, note the inner text must be accessed via the .text attribute.

        Usage: 
            self.controller.scrolledTextCreator(
                x=0, y=0, width=100, height=100, root=validtkinterparent (Frame, Canvas), classname = "classname",
                bg=WHITE, hasBorder=False, # borderColor=BLACK, 
                text="This is the text to be displayed", font=("Inter", 12), fg=BLACK, 
                isPlaced=True, isDisabled=False, isJustified=False, # justification="center"
            ) 
            clinicname = self.controller.scrolledTextCreator(
                x=X+20, y=Y, width=180, height=100, root=R, classname=f"{clinic.id}_name",
                bg="#f1feff", hasBorder=False,
                text=clinic.name, font=("Inter", 14), fg=BLACK,
                isDisabled=True, isJustified=True,
            )
        """
        classname = classname.lower().replace(" ", "")
        columnarg = int(x / 20)
        rowarg = int(y / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        scrolledText = ScrolledText(
            master=root, width=width, height=height,
            autohide=True, bootstyle="bg-round",
            padding=padding, vbar=hasVbar, hbar=hasHbar,
        )
        scrolledText.text.config(
            bg=bg, font=font, wrap=WORD, fg=fg
        )
        scrolledText.text.insert(1.0, text)
        if hasBorder:
            scrolledText.text.config(highlightbackground=borderColor)
        else:
            scrolledText.text.config(
                highlightbackground=bg, highlightthickness=0, border=0, borderwidth=0)
        if isJustified:
            scrolledText.text.tag_configure("center", justify=justification)
            scrolledText.text.tag_add("center", 1.0, "end")
        if isPlaced:
            scrolledText.place(
                x=x, y=y, width=width, height=height
            )
        else:
            scrolledText.grid(
                row=rowarg, column=columnarg, rowspan=heightspan,
                columnspan=widthspan, sticky=NSEW
            )
        if isDisabled:
            scrolledText.text.config(state=DISABLED)
        else:
            scrolledText.text.config(state=NORMAL)
        self.updateWidgetsDict(root=root)
        self.widgetsDict[classname] = scrolledText
        return scrolledText

    def threadCreator(self, target, daemon=True, *args, **kwargs):
        t = threading.Thread(target=target, args=args, kwargs=kwargs)
        t.daemon = daemon
        t.start()

    def decodingBase64Data(self, b64):
        decoded = Base64.decode(b64)
        dataBytesIO = io.BytesIO(decoded)
        im = Image.open(dataBytesIO)
        return im

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.grid()
        frame.tkraise()

    def show_canvas(self, cont):
        canvas = self.canvasInDashboard[cont]
        canvas.grid()
        canvas.tk.call("raise", canvas._w)
        canvas.focus_force()

    def get_page(self, classname):
        return self.frames[classname]

    # def hex_to_rgb(self, hexstring) -> tuple:
    #     # Convert hexstring to integer
    #     hexint = int(hexstring[1:], 16)
    #     # Extract Red, Green, and Blue values from integer using bit shifting
    #     red = hexint >> 16
    #     green = (hexint >> 8) & 0xFF
    #     blue = hexint & 0xFF
    #     colorkey = win32api.RGB(red, green, blue)
    #     return colorkey

    def togglethewindowbar(self) -> None:
        self.deletethewindowbar() if self.state() == "normal" else self.showthewindowbar()

    def deletethewindowbar(self) -> None:
        hwnd: int = get_handle(self)
        style: int = GetWindowLongPtrW(hwnd, GWL_STYLE)
        style &= ~(WS_CAPTION | WS_THICKFRAME)
        SetWindowLongPtrW(hwnd, GWL_STYLE, style)
        self.state("zoomed")

    def showthewindowbar(self) -> None:
        hwnd: int = get_handle(self)
        style: int = GetWindowLongPtrW(hwnd, GWL_STYLE)
        style |= WS_CAPTION | WS_THICKFRAME
        SetWindowLongPtrW(hwnd, GWL_STYLE, style)
        self.state("normal")
