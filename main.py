import threading
from tkinter import *
from ctypes import windll
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.dialogs import MessageDialog
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from dotenv import load_dotenv
from prisma import Prisma
from pendulum import timezone
from nonstandardimports import *
from views.mainDashboard import Dashboard
from views.registration import RegistrationPage

"""
Views
"""
from resource.basewindow import ElementCreator, gridGenerator

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
        self.initMainPrisma()
        self.loadSignIn()
        self.bind("<F11>", lambda e: self.togglethewindowbar())
        # self.pingBackend()

    def loadSignIn(self):
        self.loginEmailEntry = self.ttkEntryCreator(
            root=self.parentFrame,
            x=1140, y=440,
            width=600, height=80,
            classname="emailentry"
        )
        self.loginPasswordEntry = self.ttkEntryCreator(
            root=self.parentFrame,
            x=1140, y=600,
            width=600, height=80,
            classname="passwordentry"
        )
        self.loginButton = self.buttonCreator(
            root=self.parentFrame,
            ipath=r"assets\HomePage\SignInButton.png",
            x=1180, y=760,
            classname="loginbutton",
            buttonFunction=self.signIn,
        )
        self.signUpRedirectButton = self.buttonCreator(
            root=self.parentFrame,
            ipath=r"assets\HomePage\RedirectSignUpButton.png",
            x=1180, y=940,
            classname="signupredirectbutton",
            useHover=True,
            buttonFunction=self.loadReg,
        )

    def signIn(self):
        choices = ["Patient:success", "Doctor:secondary",
                   "Clinic Admin:info", "GovOfficer:warning", "Cancel:danger"]
        askOption = MessageDialog(
            parent=self.loginButton,
            title="Signing in (Dev)",
            message="What would you like to sign in as?",
            buttons=choices,
        )
        askOption.show()
        self.dashboard = Dashboard(parent=self.parentFrame, controller=self)
        self.frames[Dashboard] = self.dashboard
        self.dashboard.grid(
            row=0, column=0, columnspan=96, rowspan=54, sticky=NSEW
        )
        self.dashboard.tkraise()
        if askOption.result == "Patient":
            self.dashboard.loadRoleAssets(patient=True)
        elif askOption.result == "Doctor":
            self.dashboard.loadRoleAssets(doctor=True)
        elif askOption.result == "Clinic Admin":
            self.dashboard.loadRoleAssets(clinicAdmin=True)
        elif askOption.result == "GovOfficer":
            self.dashboard.loadRoleAssets(govofficer=True)
        elif askOption.result == "Cancel":
            self.dashboard.grid_remove()
            return
        return
        try:
            toast = ToastNotification(
                title="Signing in",
                message=f"Signing in...",
                bootstyle=INFO,
            )
            toast.show_toast()
            self.prisma = self.mainPrisma
            emailtext = self.loginEmailEntry.get()
            entrytext = self.loginPasswordEntry.get()
            if emailtext == "" or entrytext == "":
                toast.hide_toast()
                toast = ToastNotification(
                    title="Error",
                    message=f"Please fill in all fields",
                    duration=3000,
                )
                toast.show_toast()
                return
        except Exception as e:
            print(e)

    def loadReg(self):
        self.registrationPage = RegistrationPage(
            parent=self.parentFrame, controller=self)
        self.frames[RegistrationPage] = self.registrationPage
        self.registrationPage.grid(
            row=0, column=0, columnspan=96, rowspan=54, sticky=NSEW)
        self.registrationPage.tkraise()

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
        self.title("Call a Doctor Desktop App")
        self.resizable(False, False)
        self.bind("<Escape>", lambda e: self.destroy())
        self.parentFrame = Frame(
            self, bg="#ecf2ff", width=1920, height=1080, name="parentframe", autostyle=False
        )
        gridGenerator(self.parentFrame, 96, 54, "#ecf2ff")
        self.bg = self.labelCreator(
            root=self.parentFrame,
            x=0, y=0,
            ipath=r"assets\HomePage\SignIn.png",
            classname="homepagebg",
        )
        self.parentFrame.grid(row=0, column=0, rowspan=96,
                              columnspan=54, sticky=NSEW)


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
