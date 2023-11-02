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
from ttkbootstrap.tooltip import ToolTip
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




class OfficerBrowseClinic(Frame):
    def __init__(self, parent: GovOfficerDashboard, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="browseclinicpanel")
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
            ipath=r"assets/Dashboard/OfficerAssets/OfficerManageClinicsBG.png",
            x=0, y=0, classname="browseclinicbg", root=self
        )

        self.initializeManageClinicsSystem()
        self.loadManageClinicsFrame()

    def loadManageClinicsFrame(self):
        h = len(self.manageClinics.programmeRegistration) * 120
        if h < 600:
            h = 600
        self.manageClinicsFrame = ScrolledFrame(
            master=self, width=1500, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.manageClinicsFrame.grid_propagate(False)
        self.manageClinicsFrame.place(x=80, y=280, width=1500, height=620)
        COORDS = (20, 20)

        for clinicEnrolment in self.manageClinics.programmeRegistration:
            clinic = clinicEnrolment.clinic
            X = COORDS[0]
            Y = COORDS[1]
            R = self.manageClinicsFrame
            self.controller.labelCreator(
                x=X, y=Y, classname=f"{clinic.id}_bg", root=R,
                ipath="assets\Dashboard\clinicdetailsbg.png",
                isPlaced=True,
            )

            clinicName = self.controller.scrolledTextCreator(
                x=60, y=Y+20, width=200, height=60, root=R, classname=f"{clinic.id}_name",
                bg="#f1feff", hasBorder=False, text=clinic.name,
                font=("Inter", 14), fg=BLACK, 
                isDisabled=True, isJustified=True,
            )

            clinicId = self.controller.scrolledTextCreator(
                x=290, y=Y+20, width=200, height=60, root=R, classname=f"{clinic.id}_id",
                bg="#f1feff", hasBorder=False, text=clinic.id,
                font=("Inter", 14), fg=BLACK, 
                isDisabled=True, isJustified=True,
            )

            clinicPhone = self.controller.scrolledTextCreator(
                x=540, y=Y+20, width=200, height=60, root=R, classname=f"{clinic.id}_phone",
                bg="#f1feff", hasBorder=False, text=clinic.phoneNum,
                font=("Inter", 14), fg=BLACK, 
                isDisabled=True, isJustified=True,
            )

            clinicHrs = self.controller.scrolledTextCreator(
                x=780, y=Y+20, width=220, height=60, root=R, classname=f"{clinic.id}_hrs",
                bg="#f1feff", hasBorder=False, text=clinic.clinicHrs,
                font=("Inter", 14), fg=BLACK, 
                isDisabled=True, isJustified=True,
            )

            clinicAddress = self.controller.scrolledTextCreator(
                x=1020, y=Y+20, width=260, height=60, root=R, classname=f"{clinic.id}_address",
                bg="#f1feff", hasBorder=False, text=clinic.address,
                font=("Inter", 14), fg=BLACK, 
                isDisabled=True, isJustified=True,
            )

            hidebtn = self.controller.buttonCreator(
                ipath="assets/Dashboard/OfficerAssets/hideindicator.png",
                classname=f"hideindicator{clinic.id}", root=R,
                x=1300, y=Y+20, buttonFunction=lambda t = clinic.id: [print(f"hide {t}")],
                isPlaced=True,
            )
            ToolTip(hidebtn, f"Hide {clinic.name}")

            deletebtn = self.controller.buttonCreator(
                ipath="assets/Dashboard/OfficerAssets/dustbin.png",
                classname=f"dustbin{clinic.id}", root=R,
                x=1380, y=Y+20, buttonFunction=lambda t = clinic.id: [print(f"delete {t}")],
                isPlaced=True
            )
            ToolTip(deletebtn, f"Delete {clinic.name}")
            
            COORDS = (
                COORDS[0], COORDS[1] + 120
            )

    def initializeManageClinicsSystem(self):
        prisma = self.prisma
        self.manageClinics = prisma.govregsystem.find_first(
            where={
                "supervisingOfficer": {"some": {"userId": self.user.id}},
            },
            include={
                "programmeRegistration":{
                                            "where": {
                                                "status": "APPROVED"
                                            },
                                            "include": {
                                                "clinic": True
                                            }
                                        }
            }
            
        )
         
    

    # def loadClinicsRequests(self):
    #     pass

    # def loadViewDoctorSchedule(self):
    #     pass
