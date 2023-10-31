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

    def createPatientList(self):
        prisma = self.prisma
        patientLists = prisma.patient.find_many(
            include={
                "user": True,
            }
        )
        patientLists = []
        [patientLists.append("Thing " + str(i))
         for i in range(30) if i % 2 == 0]
        h = len(patientLists) * 120
        if h < 380:
            h = 380
        self.patientScrolledFrame = ScrolledFrame(
            master=self, width=1540, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.patientScrolledFrame.grid_propagate(False)
        self.patientScrolledFrame.place(x=60, y=280, width=1540, height=380)
        initialcoordinates = (20,20)
        for patient in patientLists:
            x = initialcoordinates[0]
            y = initialcoordinates[1]
            self.controller.textElement(
                ipath=r"assets/Dashboard/ClinicAdminAssets/ScrollFrame/srollbutton.png", x=x, y=y,
                classname=f"patientlistbg{patient.id}", root=self.patientScrolledFrame,
                text=f"{patient.user.fullName}", size=30, font=INTER,
                isPlaced=True,
                buttonFunction=lambda: [print(patient)]
            )

            initialcoordinates = (
                initialcoordinates[0], initialcoordinates[1] + 120
            )
            