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
from views.mainGRDRequests import MainGRDRequestsInterface


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

    def unloadStackedFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath=r"assets/Dashboard/OfficerAssets/OfficerDashboardPanelBG.png",
            x=0, y=0, classname="primarypanelbg", root=self
        )

        # insert map
        self.clinicsMap = tkintermapview.TkinterMapView(
            self,  width=841, height=618)
        self.clinicsMap.place(x=13, y=101)
        self.clinicsMap.set_address("Penang, Malaysia")
        self.clinicsMap.set_tile_server(
            "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

        exampleList = []
        [exampleList.append("Clinic " + str(i))
         for i in range(30) if i % 2 == 0]
        h = len(exampleList) * 120
        if h < 600:
            h = 600
        self.exampleScrolledFrame = ScrolledFrame(
            master=self, width=750, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.exampleScrolledFrame.grid_propagate(False)
        self.exampleScrolledFrame.place(x=900, y=314, width=750, height=620)
        initialcoordinates = (20, 20)
        for thing in exampleList:
            x = initialcoordinates[0]
            y = initialcoordinates[1]
            self.controller.textElement(
                ipath=r"assets\Dashboard\cliniclistbg.png", x=x, y=y,
                classname=f"clinic{thing}", root=self.exampleScrolledFrame,
                text=thing, size=30, font=INTER,
                isPlaced=True,
            )

            initialcoordinates = (
                initialcoordinates[0], initialcoordinates[1] + 120
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
        self.browseClinic = self.controller.buttonCreator(
            ipath=d["govofficer"][0],
            x=20, y=380, classname="browseclinic_chip", root=self.parent,
            buttonFunction=lambda: [self.loadBrowseClinic()],
        )
        self.viewGRDRequests = self.controller.buttonCreator(
            ipath=d["govofficer"][1],
            x=20, y=460, classname="viewpatients_chip", root=self.parent,
            buttonFunction=lambda: [self.loadGRDRequests()],
        )

    def loadBrowseClinic(self):
        try:
            self.mainInterface.primarypanel.grid()
            self.mainInterface.primarypanel.tkraise()
        except:
            self.mainInterface = MainBrowseClinic(
                controller=self.controller, parent=self.parent)
            self.mainInterface.loadRoleAssets(govofficer=True)

    def loadGRDRequests(self):
        try:
            self.grdRequests.primarypanel.grid()
            self.grdRequests.primarypanel.tkraise()
        except:
            self.grdRequests = MainGRDRequestsInterface(
                controller=self.controller, parent=self.parent)
            self.grdRequests.loadRoleAssets(govofficer=True)
