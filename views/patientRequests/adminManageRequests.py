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


class AdminManagePatientRequests(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="requestspanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)

        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.patientImgLabels()
        self.patientRequestButtons()
        self.createPatientList()

    def createFrames(self):
        pass

    def patientImgLabels(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/PatientList.png",
            x=0, y=0, classname="patientrequests", root=self
        )

    def patientRequestButtons(self):
        d = {
            "patientRequest": [
                "assets/Dashboard/ClinicAdminAssets/PatientRequests/Accept.png",
                "assets/Dashboard/ClinicAdminAssets/PatientRequests/Reject.png",
                "assets/Dashboard/ClinicAdminAssets/PatientRequests/Refresh.png",
                "assets/Dashboard/ClinicAdminAssets/PatientRequests/Refresh.png"
            ]
        }
        self.addDoctor = self.controller.buttonCreator(
            ipath=d["patientRequest"][0],
            x=380, y=140, classname="accept", root=self,
            buttonFunction=lambda: [print('accept')],
        )
        self.rejectButton = self.controller.buttonCreator(
            ipath=d["patientRequest"][1],
            x=580,y=140, classname="reject", root=self,
            buttonFunction=lambda: [print('reject')],
        )
        self.refresh3button = self.controller.buttonCreator(
            ipath=d["patientRequest"][2],
            x=680,y=300, classname="refresh3", root=self,
            buttonFunction=lambda: [print('refresh')],
        )
        self.refresh4button = self.controller.buttonCreator(
            ipath=d["patientRequest"][3],
            x=1520, y=100, classname="refresh4", root=self,
            buttonFunction=lambda: [print('refresh')],
        )
        
    def createPatientList(self):
        prisma = self.prisma
        patients = prisma.patient.find_many(
            include={
                "user": True,
            }
        )
        h = len(patients) * 100
        if h < 770:
            h = 770

        self.patientsScrolledFrame = ScrolledFrame(
            master=self, width=800, height=h, autohide=True, bootstyle="bg-round")
        self.patientsScrolledFrame.place(
            x=840, y=190, width=800, height=770
        )
        initialCoordinates = (20, 20)
        for patient in patients:
            x = initialCoordinates[0]
            y = initialCoordinates[1]
            self.controller.textElement(
                ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/ListButton.png",
                x=x, y=y, classname=f"patientlistbg{patient.id}", root=self.patientsScrolledFrame,
                text=f"{patient.user.fullName}", size=30, font=INTER,
                isPlaced=True,
                buttonFunction=lambda:[print(patient)]
            )
            initialCoordinates = (
                initialCoordinates[0], initialCoordinates[1] + 100
            )