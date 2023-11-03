from abc import ABC, abstractmethod
import calendar
import re
import threading
from tkinter import *
from tkinter import messagebox
from prisma.models import User
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
from views.dashboard.adminDashboard import ClinicAdminDashboard
from views.dashboard.doctorDashboard import DoctorDashboard

from views.dashboard.officerDashboard import GovOfficerDashboard
from views.dashboard.patientDashboard import PatientDashboard


class Dashboard(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None, name="maindashboard"):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name=name)
        self.controller = controller
        self.prisma = self.controller.mainPrisma
        self.parent = parent
        self.name = name
        gridGenerator(self, 96, 54, "#dee8e0")
        self.createFrames()
        self.createElements()
        self.grid(
            row=0, column=0, columnspan=96, rowspan=54, sticky=NSEW
        )

    def createFrames(self):
        pass

    def createElements(self):
        """
        (imagepath, x, y, classname, root)
        """
        self.staticImgLabels = [
            (r"assets/Dashboard/DashboardBG.png", 0, 0, "dashboardbg", self),
        ]
        self.staticBtns = [
            (r"assets/Dashboard/SignOut.png", 20, 980, "signoutbtn",
             self, lambda:[self.grid_remove()]),
            (r"assets/Dashboard/Settings.png", 120, 980, "settingsbtn",
             self, lambda: print("hello")),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.controller.settingsUnpacker(self.staticBtns, "button")

    def setUser(self, user: User):
        self.user = user

    def loadRoleAssets(self, patient: bool = False, doctor: bool = False, clinicAdmin: bool = False, govofficer: bool = False):
        if patient:
            self.primarypanel = PatientDashboard(
                parent=self, controller=self.controller)
        elif doctor:
            self.primarypanel = DoctorDashboard(
                parent=self, controller=self.controller)
        elif clinicAdmin:
            self.primarypanel = ClinicAdminDashboard(
                parent=self, controller=self.controller)
        elif govofficer:
            self.primarypanel = GovOfficerDashboard(
                parent=self, controller=self.controller)
        else:
            return
        self.primarypanel.loadAssets()
        self.dashboardChip = self.controller.buttonCreator(
            ipath=r"assets/Dashboard/DashboardChip.png",
            x=20, y=300, classname="dashboardchip", root=self,
            buttonFunction=lambda: self.unloadStackedFrames(),
        )

    def unloadStackedFrames(self):
        self.primarypanel.unloadStackedFrames()
        self.primarypanel.tkraise()
