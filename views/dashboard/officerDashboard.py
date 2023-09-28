import calendar
import datetime as dt
import re
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from resource.basewindow import ElementCreator, gridGenerator
from resource.static import *
from tkinter import *
from tkinter import messagebox

import tkintermapview
from pendulum import timezone
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from ttkbootstrap.dialogs.dialogs import DatePickerDialog
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.toast import ToastNotification

from views.mainBrowseClinic import MainBrowseClinic


class GovOfficerDashboard(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="primarypanel")
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
            ipath=r"assets/Dashboard/OfficerAssets/OfficerDashboardPanelBG.png",
            x=0, y=0, classname="primarypanelbg", root=self
        )


    def loadAssets(self):
        self.pfp = self.controller.buttonCreator(
            ipath="assets/Dashboard/OfficerAssets/OfficerProfilePicture.png",
            x=20, y=100, classname="profilepicture", root=self.parent,
            buttonFunction=lambda: [print('hello')]
        )
        d = {
            "govofficer": [
                r"assets/Dashboard/OfficerAssets/OfficerManageClinics.png",
                r"assets/Dashboard/OfficerAssets/OfficerClinicRequests.png",
            ],
        }
        self.officerDashboard = self.controller.buttonCreator(
            ipath=d["govofficer"][0],
            x=20, y=380, classname="officerdashboard_chip", root=self.parent,
            buttonFunction=lambda: [self.loadBrowseClinic()],
        )
        self.clinicsRequests = self.controller.buttonCreator(
            ipath=d["govofficer"][1],
            x=20, y=460, classname="clincsrequests_chip", root=self.parent,
            buttonFunction=lambda: [self.loadClinicsRequests()],
        )
        # self.viewDoctorSchedule = self.controller.buttonCreator(
        #     ipath=d["govofficer"][2],
        #     x=20, y=540, classname="viewdoctorschedule_chip", root=self.parent,
        #     buttonFunction=lambda: [self.loadViewDoctorSchedule()],
        # )

    def loadBrowseClinic(self):
        try:
            self.mainInterface.primarypanel.grid()
            self.mainInterface.primarypanel.tkraise()
        except:
            self.mainInterface = MainBrowseClinic(
                controller=self.controller, parent=self.parent)
            self.mainInterface.loadRoleAssets(govofficer=True)

    def loadClinicsRequests(self):
        pass

    def loadViewDoctorSchedule(self):
        pass
