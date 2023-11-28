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
        self.LoadClinicDoctor()


    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/DoctorAssets/DoctorBrowse.png",
            x=0, y=0, classname="DoctorClinic", root=self
        )


    def getClinicInformation(self):
        prisma = self.prisma
        viewClinicList = prisma.clinic.find_many(    #need to change to find_first?
            where={
                "doctor":{
                    "some": {
                        "userId": self.user.id
                    }
                }
            },
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
               x=1065, y=105, width=554, height=72, classname=f"clinic_details_name",
               root=self, bg="#D1E8E2", hasBorder=TRUE,
               text=f"{clinic_name}", font=("Inter", 30), fg=BLACK,
               isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            ClinicAddress = self.controller.scrolledTextCreator(
                x=150, y=225, width=740, height=60, classname=f"clinic_details_address",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{clinic_address}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            ClinicContact = self.controller.scrolledTextCreator(
                x=150, y=320, width=318, height=60, classname=f"clinic_details_status",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{clinic_Phone}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            ClinicCity = self.controller.scrolledTextCreator(
                x=572, y=320, width=318, height=60, classname=f"clinic_details_openhrs",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{clinic_city}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            ClinicState = self.controller.scrolledTextCreator(
                x=150, y=415, width=318, height=60, classname=f"clinic_details_city",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{clinic_state}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            ClinicZip = self.controller.scrolledTextCreator(
                x=572, y=415, width=318, height=60, classname=f"clinic_details_state",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{clinic_zip}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            ClinicHours = self.controller.scrolledTextCreator(
                x=198, y=505, width=318, height=60, classname=f"clinic_details_zip",
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
            x=935, y=930, width=720, height=80, root=R, classname="doctor_loadedclinic_title",
            bg="#ebd9dd", hasBorder=True, 
            text=f"The Details of { clinic.name }", font=("Inter Bold", 24), fg=BLACK,
            isDisabled=True, isJustified=True, justification="center", isPlaced=True,
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
        self.clinicImage.place(x=955, y=220, width=695, height=650)
        


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
    

    def LoadClinicDoctor(self):   
        prisma = self.prisma
        clinicOfDoctor = prisma.clinic.find_first(
            where={
                "doctor": {
                    "some":{
                        "userId": self.user.id
                    }
                }
            },
            include={
                "doctor": {
                    "include": {
                         "user": True,
                    }
                }
            }
        )

        h = len(clinicOfDoctor.doctor) * 120
        if h < 760:
            h = 760
        self.appointmentListFrame = ScrolledFrame(
            master=self, width=1500, height=h, autohide=True, bootstyle="DoctorDashboard.bg"
        )
        self.appointmentListFrame.grid_propagate(False)
        self.appointmentListFrame.place(x=23, y=782, width=877, height=225)
        COORDS = (5, 5)
        for clinicDoctor in clinicOfDoctor.doctor:

            DoctorName = clinicDoctor.user.fullName
            DoctorSpeciality = clinicDoctor.speciality
            DoctorContact = clinicDoctor.user.contactNo
            DoctorEmail = clinicDoctor.user.email

            X = COORDS[0]
            Y = COORDS[1]
            R = self.appointmentListFrame
            self.controller.labelCreator(
                x=X, y=Y, classname=f"{clinicDoctor.id}_bg", root=R,
                ipath="assets/Dashboard/DoctorAssets/DoctorListButton/ViewDcotorDetails.png",
                isPlaced=True,
            )
            doctoerName = self.controller.scrolledTextCreator(
                x=X+25, y=Y+16, width=145, height=55, root=R, classname=f"{clinicDoctor.id}_name",
                bg="#3D405B", hasBorder=False,
                text=f"{DoctorName}", font=("Inter", 20), fg=WHITE,
                isDisabled=True, isJustified=True, justification="center",
                isPlaced=True,
            )
            doctorspeciality = self.controller.scrolledTextCreator(
                x=X+245, y=Y+32, width=145, height=55, root=R, classname=f"{clinicDoctor.id}_phone_num",
                bg="#3D405B", hasBorder=False,
                text=f"{DoctorSpeciality}", font=("Inter", 18), fg=WHITE,
                isDisabled=True, isJustified=True, justification="center",
                isPlaced=True,
            )
            doctorContactNumber = self.controller.scrolledTextCreator(
                x=X+470, y=Y+32, width=145, height=55, root=R, classname=f"{clinicDoctor.id}_App_time",
                bg="#3D405B", hasBorder=False,
                text=f"{DoctorContact}", font=("Inter", 18), fg=WHITE,
                isDisabled=True, isJustified=True, justification="center",
                isPlaced=True,
            )
            UpAppTime = self.controller.scrolledTextCreator(
                x=X+695, y=Y+32, width=145, height=55, root=R, classname=f"{clinicDoctor.id}_App_time",
                bg="#3D405B", hasBorder=False,
                text=f"{DoctorEmail}", font=("Inter", 18), fg=WHITE,
                isDisabled=True, isJustified=True, justification="center",
                isPlaced=True,
            )
            COORDS = (COORDS[0], COORDS[1] + 120)

        




