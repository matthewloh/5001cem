from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.dashboard.officerDashboard import GovOfficerDashboard
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


class OfficerGRDRequests(Frame):
    def __init__(self, parent: GovOfficerDashboard, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="clinicgrdrequests")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        
        self.user = self.parent.user
        self.prisma = self.controller.mainPrisma

        self.createFrames()
        self.createElements()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath=r"assets/Dashboard/OfficerAssets/OfficerClinicsRequestsBG.png",
            x=0, y=0, classname="grdrequestsbg", root=self
        )

        self.initializeOfficerGRDRequests()
        self.loadClinicsRequestsFrame()

    def loadClinicsRequestsFrame(self):
        h = len(self.clinicsRequests.programmeRegistration) * 120
        if h < 600:
            h = 600
        self.clinicRequestsFrame = ScrolledFrame(
            master=self, width=1500, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.clinicRequestsFrame.grid_propagate(False)
        self.clinicRequestsFrame.place(x=80, y=280, width=1500, height=620)
        COORDS = (20, 20)
        for clinicEnrolment in self.clinicsRequests.programmeRegistration:
            clinic = clinicEnrolment.clinic
            X = COORDS[0]
            Y = COORDS[1]
            R = self.clinicRequestsFrame
            self.controller.labelCreator(
                x=X, y=Y, classname=f"{clinic.id}_req", root=R,
                ipath="assets\Dashboard\clinicdetailsbg.png",
                isPlaced=True,
            )

            clinicName = self.controller.scrolledTextCreator(
                x=75, y=Y+25, width=200, height=60, root=R, classname=f"{clinic.id}_name",
                bg="#f1feff", hasBorder=False, text=clinic.name,
                font=("Inter", 14), fg=BLACK, 
                isDisabled=True, isJustified=True,
            )

            clinicId = self.controller.scrolledTextCreator(
                x=320, y=Y+25, width=200, height=60, root=R, classname=f"{clinic.id}_id",
                bg="#f1feff", hasBorder=False, text=clinic.id,
                font=("Inter", 14), fg=BLACK, 
                isDisabled=True, isJustified=True,
            )

            clinicPhone = self.controller.scrolledTextCreator(
                x=540, y=Y+25, width=200, height=60, root=R, classname=f"{clinic.id}_phone_num",
                bg="#f1feff", hasBorder=False, text=clinic.phoneNum,
                font=("Inter", 14), fg=BLACK, 
                isDisabled=True, isJustified=True,
            )

            clinicHrs = self.controller.scrolledTextCreator(
                x=790, y=Y+25, width=200, height=60, root=R, classname=f"{clinic.id}_hrs",
                bg="#f1feff", hasBorder=False, text=clinic.clinicHrs,
                font=("Inter", 14), fg=BLACK, 
                isDisabled=True, isJustified=True,
            )

            self.controller.buttonCreator(
                ipath="assets/Dashboard/OfficerAssets/OfficerAcceptClinic.png",
                classname=f"acceptclinic{clinic.id}", root=R,
                x=1055, y=Y+20, buttonFunction=lambda t = clinic.id: [print(f"acceptclinic {clinic.name}")],
                isPlaced=True,
            )
            self.controller.buttonCreator(
                ipath="assets/Dashboard/OfficerAssets/OfficerRejectClinic.png",
                classname=f"rejectclinic{clinic.id}", root=R,
                x=1055+216, y=Y+20, buttonFunction=lambda t = clinic.id: [print(f"rejectclinic {clinic.name}")],
                isPlaced=True
            )

            COORDS = (
                COORDS[0], COORDS[1] + 120
            )


    def initializeOfficerGRDRequests(self):
        prisma = self.prisma
        self.clinicsRequests = prisma.govregsystem.find_first(
            where={
                "supervisingOfficer": {"some": {"userId": self.user.id}},
            },
            include={
                "programmeRegistration":{
                                            "where": {
                                                "status": "PENDING"
                                            },
                                            "include": {
                                                "clinic": True
                                            }
                                        }
            }
            
        )

