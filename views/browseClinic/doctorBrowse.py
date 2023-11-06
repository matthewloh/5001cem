from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.dashboard.doctorDashboard import DoctorDashboard
from abc import ABC, abstractmethod
import calendar
import re
import threading
from tkinter import *
import tkinter as tk
from tkinter import messagebox
from prisma.models import Clinic
from PIL import Image, ImageOps, ImageTk
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


class DoctorBrowseClinic(Frame):
    def __init__(self, parent: DoctorDashboard=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="secondarypanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.user = self.parent.user
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.getClinicInformation()
        self.loadClinic()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/DoctorAssets/DoctorBrowse.png",
            x=0, y=0, classname="DoctorClinic", root=self
        )


    def getClinicInformation(self):
        prisma = self.prisma
        viewClinicList = prisma.clinic.find_many(
            include={
                "doctor": {
                    "include": {
                        "user": True
                    }
                }
            }
        )

        if viewClinicList:
            clinic = viewClinicList[0]  


            # clinic data
            clinic_name = clinic.name
            clinic_address = clinic.address
            clinic_Phone = clinic.phoneNum
            clinic_hrs = clinic.clinicHrs
            clinic_city = clinic.city
            clinic_state = clinic.state
            clinic_zip = clinic.zip

            # # doctor data
            # doctor_name = clinic.doctor.user.fullName
            # doctor_speciality = clinic.doctor.speciality

            ClinicName = self.controller.scrolledTextCreator(
               x=1065, y=110, width=554, height=72, classname=f"clinic_details_name",
               root=self, bg="#D1E8E2", hasBorder=TRUE,
               text=f"{clinic_name}", font=("Inter", 30), fg=BLACK,
               isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            ClinicAddress = self.controller.scrolledTextCreator(
                x=170, y=230, width=700, height=60, classname=f"clinic_details_address",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{clinic_address}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            ClinicContact = self.controller.scrolledTextCreator(
                x=170, y=325, width=240, height=60, classname=f"clinic_details_status",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{clinic_Phone}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            ClinicCity = self.controller.scrolledTextCreator(
                x=612, y=325, width=240, height=60, classname=f"clinic_details_openhrs",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{clinic_city}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            ClinicState = self.controller.scrolledTextCreator(
                x=170, y=420, width=240, height=60, classname=f"clinic_details_city",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{clinic_state}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            ClinicZi = self.controller.scrolledTextCreator(
                x=612, y=420, width=240, height=60, classname=f"clinic_details_state",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{clinic_zip}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            ClinicHours = self.controller.scrolledTextCreator(
                x=228, y=515, width=250, height=60, classname=f"clinic_details_zip",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{clinic_hrs}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            #DoctorName = self.controller.scrolledTextCreator(
            #    x=1295, y=110, width=554, height=72, classname=f"clinic_doctor_name",
            #    bg="#FEFEFE", hasBorder=False,
            #    isDisabled=True, isJustified=True, justification="center",
            #)

            #ClinicName = self.controller.scrolledTextCreator(
            #    x=1295, y=110, width=554, height=72, classname=f"clinic_doctor_name",
            #    bg="#FEFEFE", hasBorder=False,
            #    text=f"{clinic_name}", font=("Inter", 30), fg=BLACK,
            #    isDisabled=True, isJustified=True, justification="center",
            #)
    


    def loadClinic(self):
        prisma = self.prisma
        clinic = prisma.clinic.find_first(
            where={
                "doctor":{
                    "some": {
                        "userId": self.user.id
                    }
                }
            },
        )
        R = self
        self.viewedClinic = clinic
        img = self.controller.decodingBase64Data(clinic.clinicImg)
        self.viewedClinicTitle = self.controller.scrolledTextCreator(
            x=120, y=20, width=720, height=80, root=R, classname="doctor_loadedclinic_title",
            bg="#dee8e0",
            text=f"Browsing Details of { clinic.name }", font=("Inter Bold", 24), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
        )
        img = ImageOps.contain(img, (693, 793), Image.Resampling.BICUBIC)
        self.clinicImage = self.controller.labelCreator(
            x=40, y=120, classname="doctor_loadedclinic_image", root=R,
            ipath="assets/BrowseClinic/Patient/BrowseSingleClinic/ClinicImagePlaceholder.png",
            bg="#a6cbff",
            isPlaced=True
        )
        self.controller.imageDict["doctor_loadedclinic_image"] = ImageTk.PhotoImage(
            img
        )
        newImage = self.controller.imageDict["doctor_loadedclinic_image"]
        self.clinicImage.configure(image=newImage, width=693, height=793)
        self.clinicImage.place(x=965, y=120, width=700, height=700)
        formatAddress = f"{clinic.address}, {clinic.zip}, {clinic.city}, {clinic.state.replace('_', ' ').title()}"
        self.clinicAddress = self.controller.scrolledTextCreator(
            x=140, y=1000, width=660, height=100, root=self.loadedClinicFrame, classname="patient_loadedclinic_address",
            bg=WHITE, hasBorder=BLACK,
            text=formatAddress, font=("Inter Bold", 18), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )


            #DoctorName = self.controller.scrolledTextCreator(
            #    x=1295, y=110, width=554, height=72, classname=f"clinic_doctor_name",
            #    bg="#FEFEFE", hasBorder=False,
            #    isDisabled=True, isJustified=True, justification="center",
            #)

            #ClinicName = self.controller.scrolledTextCreator(
            #    x=1295, y=110, width=554, height=72, classname=f"clinic_doctor_name",
            #    bg="#FEFEFE", hasBorder=False,
            #    text=f"{clinic_name}", font=("Inter", 30), fg=BLACK,
            #    isDisabled=True, isJustified=True, justification="center",
            #)
    

        
        




