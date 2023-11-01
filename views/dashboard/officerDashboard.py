from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.mainDashboard import Dashboard
import calendar
import datetime as dt
import re
import os
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from resource.basewindow import ElementCreator, gridGenerator
from resource.static import *
from tkinter import *
from tkinter import messagebox

import tkintermapview
from geopy.geocoders import GoogleV3
from pendulum import timezone
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from ttkbootstrap.dialogs.dialogs import DatePickerDialog
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.toast import ToastNotification

from views.mainBrowseClinic import MainBrowseClinic
from views.mainGRDRequests import MainGRDRequestsInterface


class GovOfficerDashboard(Frame):
    def __init__(self, parent: Dashboard = None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="primarypanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.prisma = self.controller.mainPrisma
        self.user = self.parent.user
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

        self.initializeGovRegSystem()
        self.loadSupervisedClinicsOnMap()
        self.loadClinicsIntoSideFrame()
        self.loadClinicsIntoBottomFrame()

    def loadClinicsIntoSideFrame(self):
        h = len(self.systemManaged.programmeRegistration) * 120
        if h < 760:
            h = 760
        self.clinicsListFrame = ScrolledFrame(
            master=self, width=780, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.clinicsListFrame.grid_propagate(False)
        self.clinicsListFrame.place(x=880, y=260, width=780, height=760)
        COORDS = (20, 20)
        for clinicEnrolment in self.systemManaged.programmeRegistration:
            clinic = clinicEnrolment.clinic
            X = COORDS[0]
            Y = COORDS[1]
            R = self.clinicsListFrame
            self.controller.labelCreator(
                x=X, y=Y, classname=f"{clinic.id}_bg", root=R,
                ipath="assets/Dashboard/OfficerAssets/clinicsstatusbg.png",
                isPlaced=True,
            )
            clinicname = self.controller.scrolledTextCreator(
                x=X+20, y=Y, width=180, height=100, root=R, classname=f"{clinic.id}_name",
                bg="#f1feff", hasBorder=False,
                text=clinic.name, font=("Inter", 14), fg=BLACK,
                isDisabled=True, isJustified=True,
            )
            clinicPhone = self.controller.scrolledTextCreator(
                x=X+220, y=Y, width=180, height=100, root=R, classname=f"{clinic.id}_phone_num",
                bg="#f1feff", hasBorder=False,
                text=clinic.phoneNum, font=("Inter", 14), fg=BLACK,
                isDisabled=True, isJustified=True
            )
            clinicAddress = self.controller.scrolledTextCreator(
                x=X+420, y=Y, width=220, height=100, root=R, classname=f"{clinic.id}_address",
                bg="#f1feff", hasBorder=False,
                text=clinic.address, font=("Inter", 12), fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
            )
            clinicStatus = self.controller.buttonCreator(
                x=X+660, y=Y+20, classname=f"{clinic.id}_status", root=R,
                ipath="assets/Dashboard/OfficerAssets/Approved.png" if clinicEnrolment.status == "APPROVED" else "assets/Dashboard/OfficerAssets/Pending.png",
                buttonFunction=lambda c=clinic: [self.updateClinicStatus(c)],
                isPlaced=True
            )
            COORDS = (
                COORDS[0], COORDS[1] + 120
            )

    def loadClinicsIntoBottomFrame(self):
        # h = len(self.systemManaged.programmeRegistration) * 120
        # if h < 760:
        #     h = 760
        # self.clinicsListFrame = ScrolledFrame(
        #     master=self, width=780, height=h, autohide=True, bootstyle="officer-bg"
        # )
        # self.clinicsListFrame.grid_propagate(False)
        # self.clinicsListFrame.place(x=880, y=1040, width=780, height=760)
        # COORDS = (20, 20)
        # for clinicEnrolment in self.systemManaged.programmeRegistration:
        #     clinic = clinicEnrolment.clinic
        #     X = COORDS[0]
        #     Y = COORDS[1]
        #     R = self.clinicsListFrame
        #     self.controller.labelCreator(
        #         x=X, y=Y, classname=f"{clinic.id}_bg", root=R,
        #         ipath="assets/Dashboard/OfficerAssets/clinicsstatusbg.png",
        #         isPlaced=True,
        #     )
        pass

    def loadSupervisedClinicsOnMap(self):
        self.loc = GoogleV3(api_key=os.getenv(
            "MAPS_API_KEY"), user_agent="myGeocoder")
        # insert map

        self.clinicsMap = tkintermapview.TkinterMapView(
            self,  width=840, height=620, corner_radius=12)
        self.clinicsMap.place(x=20, y=100)
        self.clinicsMap.set_address(
            f"{self.systemManaged.state.replace('_', ' ').title()}, Malaysia")
        self.clinicsMap.set_zoom(13)
        self.clinicsMap.set_tile_server(
            "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

        for clinicEnrolment in self.systemManaged.programmeRegistration:
            clinic = clinicEnrolment.clinic
            structuredAddress = f"{clinic.address}, {clinic.zip}, {clinic.city}, {clinic.state.replace('_', ' ').title()}"
            clinicCoordinates = self.loc.geocode(structuredAddress)
            self.clinicsMap.set_marker(
                clinicCoordinates.latitude, clinicCoordinates.longitude, text=clinic.name
            )

    def initializeGovRegSystem(self):
        self.systemManaged = self.prisma.govregsystem.find_first(
            where={
                "supervisingOfficer": {"some": {"userId": self.user.id}}
            },
            include={
                "programmeRegistration": {"include": {"clinic": True}}
            }
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
