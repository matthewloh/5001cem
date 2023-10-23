from abc import ABC, abstractmethod
import calendar
import re
import threading
from tkinter import *
from tkinter import messagebox
from prisma.models import Appointment
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from ttkbootstrap.dialogs.dialogs import DatePickerDialog
from resource.basewindow import gridGenerator
from resource.static import *
from resource.basewindow import ElementCreator
from datetime import datetime, timedelta
import datetime as dt
from pendulum import timezone
import tkintermapview


class PatientBrowseClinic(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="browseclinicpanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)

        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/BrowseClinic/Patient/BG.png",
            x=0, y=0, classname="secondarypanelbg", root=self
        )
        self.createButtons()
        self.createEntry()

    def createButtons(self):
        CREATOR = self.controller.buttonCreator
        IP, X, Y, CN, R, BF = "ipath", "x", "y", "classname", "root", "buttonFunction"
        name = "browseclinic"
        params = {
            "searchbutton": {
                IP: "assets/BrowseClinic/Patient/Search.png",
                X: 780,
                Y: 80,
                CN: f"{name}_searchbtn",
                R: self,
                BF: lambda: [print('test')]
            },
        }
        for param in params:
            CREATOR(**params[param])

    def createEntry(self):
        CREATOR = self.controller.ttkEntryCreator
        self.searchEntry = CREATOR(
            x=0, y=80,
            width=780, height=80,
            classname="searchentry", root=self,
            placeholder="Search for clinics"
        )
