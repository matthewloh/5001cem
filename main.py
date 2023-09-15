from tkinter import *
from ctypes import windll
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from dotenv import load_dotenv
from prisma import Prisma
from pendulum import timezone
from nonstandardimports import *

"""
Views
"""
from basewindow import ElementCreator, gridGenerator

load_dotenv()

user32 = windll.user32


class Window(ElementCreator):
    def __init__(self, *args, **kwargs):
        ttk.Window.__init__(self, themename="minty", *args, **kwargs)
        self.widgetsDict = {}
        self.imageDict = {}
        self.imagePathDict = {}
        self.frames = {}
        self.subframes = {}
        self.initializeWindow()
        # self.initMainPrisma()
        for F in (HomePage,):
            frame = F(parent=self.parentFrame, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, columnspan=96, rowspan=54, sticky=NSEW)
            self.maincanvas = self.canvasCreator(
                xpos=80,
                ypos=80,
                width=1920,
                height=920,
                root=self,
                classname="maincanvas",
                bgcolor=WHITE,
                isTransparent=True,
                transparentcolor=LIGHTYELLOW,
            )
            frame.grid_remove()

        # self.postSelectFrame.tkraise()
        # self.show_frame(HomePage)
        self.loadSignIn()
        self.bind("<F11>", lambda e: self.togglethewindowbar())

    def loadSignIn(self):
        self.labelCreator(
            imagepath=r"assets\HomePage\SignIn.png",
            xpos=0,
            ypos=0,
            classname="homepagebg",
            root=self,
        )

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
        frames = ()
        for widgetname, widget in self.children.items():
            if isinstance(widget, widgettypes) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        for widgetname, widget in self.parentFrame.children.items():
            if isinstance(widget, widgettypes) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        for widgetname, widget in root.children.items():
            if isinstance(widget, widgettypes) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        try:
            for widgetname, widget in self.get_page(HomePage).children.items():
                if isinstance(widget, widgettypes) and not widgetname.startswith("!la"):
                    self.widgetsDict[widgetname] = widget
        except:
            pass
        try:
            for widgetname, widget in self.widgetsDict["maincanvas"].children.items():
                if isinstance(widget, widgettypes) and not widgetname.startswith("!la"):
                    self.widgetsDict[widgetname] = widget
        except:
            pass

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

    def initializeWindow(self):
        windll.shcore.SetProcessDpiAwareness(1)
        quarterofscreenwidth = int(int(user32.GetSystemMetrics(0) / 2) / 4)
        quarterofscreenheight = int(int(user32.GetSystemMetrics(1) / 2) / 4)
        gridGenerator(self, 1, 1, NICEPURPLE)
        if self.winfo_screenwidth() <= 1920 and self.winfo_screenheight() <= 1080:
            self.geometry(f"1920x1080+0+0")
        elif self.winfo_screenwidth() > 1920 and self.winfo_screenheight() > 1080:
            self.geometry(
                f"1920x1080+{quarterofscreenwidth}+{quarterofscreenheight}")
        self.title("INTI Learning Platform")
        self.resizable(False, False)
        self.bind("<Escape>", lambda e: self.destroy())
        self.parentFrame = Frame(
            self, bg=ORANGE, width=1, height=1, name="parentframe", autostyle=False
        )
        self.parentFrame.grid(row=0, column=0, rowspan=96,
                              columnspan=54, sticky=NSEW)
        gridGenerator(self.parentFrame, 96, 54, OTHERPINK)


class HomePage(Frame):
    def __init__(self, parent, controller: Window):
        Frame.__init__(self, parent, width=1, height=1,
                       bg=OTHERPINK, name="dashboard", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 54, LIGHTYELLOW)
        self.load()

    def load(self):
        self.CT = self.controller
        # self.controller.maincanvas = self.controller.canvasCreator(
        #     xpos=80, ypos=80, width=1920, height=920, root=self,
        #     classname="maincanvas", bgcolor=WHITE, isTransparent=True, transparentcolor=LIGHTYELLOW
        # )


def runGui():
    window = Window()
    window.mainloop()


def runGuiThreaded():
    t = Thread(ThreadStart(runGui))
    t.ApartmentState = ApartmentState.STA
    t.Start()
    t.Daemon = True
    t.Join()


if __name__ == "__main__":
    runGui()
    # runGuiThreaded()
