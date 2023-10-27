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


class PatientViewAppointments(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="appointmentspanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.createbutton()
        self.createFormEntries()
        self.loadAppScrolledFrame()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/PatientAssets/PatientBookAppointment.png",
            x=0, y=0, classname="appointmentspanelbg", root=self
        )

    def createFormEntries(self):
        CREATOR = self.controller.ttkEntryCreator
        FONT = ("Arial", 24)

        self.patientAppointmentClinicName = CREATOR(
            x=1174, y=664, width=360, height=46,
            root=self, classname="Patient_Appointment_Clinic_Name",
            font=FONT, isPlaced=True
        )

        self.patientAppointmentDoctorName = CREATOR(
            x=1174, y=727, width=360, height=46,
            root=self, classname="Patient_Appointment_Doctor_Name",
            font=FONT, isPlaced=True
        )

        self.patientAppointmentDate = CREATOR(
            x=1174, y=790, width=360, height=46,
            root=self, classname="Patient_Appointment_Date",
            font=FONT, isPlaced=True
        )

        self.patientAppointmentTime = CREATOR(
            x=1174, y=853, width=360, height=46,
            root=self, classname="Patient_Appointment_Time",
            font=FONT, isPlaced=True
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

        #first scroll frame
        self.appointmentViewClinicListScrolledFrame = ScrolledFrame(
            master=self, width=1500, height=h, bootstyle="light", autohide=True
        )
        self.appointmentViewClinicListScrolledFrame.place(
            x=44, y=234, width=758, height=759)
        initCoords = (10, 10)
        for a in appointments:
            #a.fullname.userId
            bg = self.controller.labelCreator(
                ipath="assets/Dashboard/PatientAssets/PatientListButton/PatientAppointmentClinicList.png",
                x=initCoords[0], y=initCoords[1], classname=f"appointmentbg{a}", root=self.appointmentViewClinicListScrolledFrame,
                isPlaced=True
            )
            initCoords = (initCoords[0], initCoords[1] + 120)

    
        self.appointmentViewDcotorListScrolledFrame = ScrolledFrame(
            master=self, width=1500, height=h, bootstyle="bg-round", autohide=True
        )
        self.appointmentViewDcotorListScrolledFrame.place(
            x=908, y=241, width=644, height=272)
        initCoords = (25, 25)
        for a in appointments:
            #a.fullname.userId
            bg = self.controller.labelCreator(
                ipath="assets/Dashboard/PatientAssets/PatientListButton/PatientAppointmentDoctorList.png",
                x=initCoords[0], y=initCoords[1], classname=f"appointmentbg1{a}", root=self.appointmentViewDcotorListScrolledFrame,
                isPlaced=True
            )
            initCoords = (initCoords[0], initCoords[1] + 120)

    def createbutton(self):
        self.submitButton = self.controller.buttonCreator(
            ipath="assets/Dashboard/PatientAssets/PatientSubmitButton.png", x=1100 , y=920,
            classname = "PatientSubmitApppointment" , root=self, buttonFunction=lambda:[print('print=Submit')]
        )
