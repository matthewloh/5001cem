from abc import ABC, abstractmethod
import calendar
import re
import threading
from tkinter import *
import tkinter as tk
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


class DoctorBrowseClinic(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="secondarypanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.getClinicInformation()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/DoctorAssets/DoctorClinic.png",
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


            #clinic data
            #clinic_name = clinic.name
            #clinic_address = clinic.address
            #clinic_Phone = clinic.phoneNum
            #clinic_hrs = clinic.clinicHrs
            #clinic_city = clinic.city
            #clinic_state = clinic.state
            #clinic_zip = clinic.zip

            #doctor data
            #doctor_name = clinic.doctor.user.fullName
            #doctor_speciality = clinic.doctor.speciality

            #ClinicName = self.controller.scrolledTextCreator(
            #    x=1295, y=110, width=554, height=72, classname=f"clinic_details_name",
            #    bg="#FEFEFE", hasBorder=TRUE,
            #    text=f"{clinic_name}", font=("Inter", 30), fg=BLACK,
            #    isDisabled=True, isJustified=True, justification="center",
            #)

            ClinicAddress = self.controller.scrolledTextCreator(
                x=480, y=220, width=622, height=60, classname=f"clinic_details_address",
                bg="#FFFFD0", hasBorder=False,
                text=f"{clinic_address}", font=("Inter", 30), fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
            )

            ClinicState = self.controller.scrolledTextCreator(
                x=418, y=320, width=240, height=60, classname=f"clinic_details_status",
                bg="#FEFEFE", hasBorder=False,
                text=f"{clinic_Phone}", font=("Inter", 30), fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
            )

            CliniOpenHrs = self.controller.scrolledTextCreator(
                x=862, y=320, width=240, height=60, classname=f"clinic_details_openhrs",
                bg="#FEFEFE", hasBorder=False,
                text=f"{clinic_hrs}", font=("Inter", 30), fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
            )

            ClinicCity = self.controller.scrolledTextCreator(
                x=418, y=420, width=240, height=60, classname=f"clinic_details_city",
                bg="#FEFEFE", hasBorder=False,
                text=f"{clinic_city}", font=("Inter", 30), fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
            )

            ClinicState = self.controller.scrolledTextCreator(
                x=862, y=420, width=240, height=60, classname=f"clinic_details_state",
                bg="#FEFEFE", hasBorder=False,
                text=f"{clinic_state}", font=("Inter", 30), fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
            )

            ClinicZip = self.controller.scrolledTextCreator(
                x=418, y=520, width=240, height=60, classname=f"clinic_details_zip",
                bg="#FEFEFE", hasBorder=False,
                text=f"{clinic_zip}", font=("Inter", 30), fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
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
    

        
        




