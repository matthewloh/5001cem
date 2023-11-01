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
        self.createPatientList()

    def createFrames(self):
        pass

    def patientImgLabels(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/PatientRequestsBg.png",
            x=0, y=0, classname="patientrequests", root=self
        )

        exampleList = []
        [exampleList.append("Thing " + str(i))
         for i in range(30) if i % 2 == 0]
        h = len(exampleList) * 120
        if h < 280:
            h = 280
        self.viewAppointmentScrolledFrame = ScrolledFrame(
            master=self, width=1500, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.viewAppointmentScrolledFrame.grid_propagate(False)
        self.viewAppointmentScrolledFrame.place(x=60, y=240, width=1500, height=280)
        initialcoordinates = (20,20)
        for request in exampleList:
            X = initialcoordinates[0]
            Y = initialcoordinates[1]
            self.controller.textElement(
                ipath=r"assets/Dashboard/ClinicAdminAssets/ScrollFrame/scrollbutton.png", x=X, y=Y,
                classname=f"request{request}", root=self.viewAppointmentScrolledFrame,
                text=request, size=30, font=INTER,
                isPlaced=True,
            )   

        d = {
            "requestButton": [
                "assets/Dashboard/ClinicAdminAssets/ScrollFrame/accept.png",
                "assets/Dashboard/ClinicAdminAssets/ScrollFrame/reject.png",
            ]
        }
        self.acceptbutton = self.controller.buttonCreator(
            ipath=d["requestButton"][0],
            x=X+1060, y=Y+30, classname=f"acceptbutton{request}", root=self.viewAppointmentScrolledFrame,
                buttonFunction=lambda: [print('accept')],
                isPlaced=True
        )
        self.rejectbutton = self.controller.buttonCreator(
            ipath=d["requestButton"][1],
            x=X+1260, y=Y+30, classname=f"rejectbutton{request}", root=self.viewAppointmentScrolledFrame,
                buttonFunction=lambda: [print('reject')],
                isPlaced=True
        )

        initialcoordinates = (
                initialcoordinates[0], initialcoordinates[1] + 120
            )
        
    def createPatientList(self):
        prisma = self.prisma
        patientLists = prisma.patient.find_many(
            include={
                "user": True,
            }
        )
        h = len(patientLists) * 120
        if h < 290:
            h = 290
        self.patientScrolledFrame = ScrolledFrame(
            master=self, width=1540, height=h, autohide=True, bootstyle="minty-bg"
        )
        self.patientScrolledFrame.grid_propagate(False)
        self.patientScrolledFrame.place(x=60, y=710, width=1540, height=290)
        initialcoordinates = (20,20)
        for patient in patientLists:
            x = initialcoordinates[0]
            y = initialcoordinates[1]
            self.controller.textElement(
                ipath="assets/Dashboard/ClinicAdminAssets/ScrollFrame/scrollbutton.png", x=x, y=y,
                classname=f"patientlistbg{patient.id}", root=self.patientScrolledFrame,
                text=f"{patient.user.fullName}", size=30, font=INTER,
                isPlaced=True,
                buttonFunction=lambda: [print(patient)]
            )

            initialcoordinates = (
                initialcoordinates[0], initialcoordinates[1] + 120
            )
            