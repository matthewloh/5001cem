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


class PatientCreateRequests(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="requestspanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)

        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.createbutton()
        self.loadAppScrolledFrame()
        self.createFormEntries()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/PatientAssets/PatientRequestPrescription.png",
            x=0, y=0, classname="requestspanelbg", root=self
        )

    def loadAppScrolledFrame(self):
        prisma = self.prisma
        # appointments = prisma.appointment.find_many(
        #     where={
        #         "doctor": {
        #             "is": {
        #                 "userId": self.getUserID()
        #             }
        #         }
        #     },
        #     include={
        #         "patient": {
        #             "include": {
        #                 "user": True
        #             }
        #         }
        #     }
        # )
        appointments = [1, 2, 3, 4, 5, 6, 7]
        h = len(appointments) * 120
        if h < 620:
            h = 620
        self.prescriptionStatus = ScrolledFrame(
            master=self, width=1500, height=h, bootstyle="bg-round", autohide=True
        )
        self.prescriptionStatus.place(
            x=932, y=341, width=647, height=594)
        initCoords = (40, 40)
        for a in appointments:
            #a.fullname.userId
            bg = self.controller.labelCreator(
                ipath="assets/Dashboard/PatientAssets/PatientListButton/PatientRequestPrescriptionButton.png",
                x=initCoords[0], y=initCoords[1], classname=f"prescriptionStatus{a}", root=self.prescriptionStatus,
                isPlaced=True
            )
            initCoords = (initCoords[0], initCoords[1] + 90)


    def createFormEntries(self):
        CREATOR = self.controller.ttkEntryCreator
        FONT = ("Arial", 24)

        self.patientBrowserSelectAddress = CREATOR(
            x=124, y=383, width=611, height=56,
            root=self, classname="Patient_Request_Prescription_Name",
            font=FONT, isPlaced=True
        )

        self.patientBrowserSelectAddress = CREATOR(
            x=124, y=383, width=611, height=56,
            root=self, classname="Patient_Request_Prescription_Name",
            font=FONT, isPlaced=True
        )

        self.patientBrowserSearchClinic = CREATOR(
            x=124, y=487, width=611, height=56,
            root=self, classname="Patient_Request_Prescription_Contact",
            font=FONT, isPlaced=True
        )

        self.patientBrowserSearchClinic = CREATOR(
            x=124, y=592, width=611, height=56,
            root=self, classname="Patient_Request_Prescription_Email",
            font=FONT, isPlaced=True
        )

        self.patientBrowserSearchClinic = CREATOR(
            x=124, y=773, width=611, height=56,
            root=self, classname="Patient_Request_Prescription_DoctorName",
            font=FONT, isPlaced=True
        )

    def createbutton(self):
        self.submitButton = self.controller.buttonCreator(
            ipath="assets/Dashboard/PatientAssets/PatientSubmitButton.png", x=290 , y=853,
            classname = "PatientRequestPrescription" , root=self, buttonFunction=lambda:[print('print=Submit')]
        )

        
