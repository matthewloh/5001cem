import calendar
import datetime as dt
import re
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from resource.basewindow import ElementCreator, gridGenerator
from resource.static import *
from tkinter import *
from tkinter import messagebox

import tkintermapview
from pendulum import timezone
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from ttkbootstrap.dialogs.dialogs import DatePickerDialog
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.toast import ToastNotification

from views.mainBrowseClinic import MainBrowseClinic
from views.mainPatientRequests import MainPatientRequestsInterface
from views.mainViewAppointments import MainViewAppointmentsInterface


class DoctorDashboard(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="primarypanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.createPatientList()
        self.loadAppScrolledFrame()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/DoctorAssets/DoctorDashboard.png",
            x=0, y=0, classname="primarypanelbg", root=self
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
        self.appointmentScrolledFrame = ScrolledFrame(
            master=self, width=1500, height=h, bootstyle="bg-round", autohide=True
        )
        self.appointmentScrolledFrame.place(
            x=80, y=320, width=1500, height=620)
        initCoords = (20, 20)
        for a in appointments:
            bg = self.controller.labelCreator(
                ipath="assets/Dashboard/DoctorAssets/DoctorListButton/DoctorPatientDetailsButton.png",
                x=initCoords[0], y=initCoords[1], classname=f"UpcomingAppointment{a}", root=self.appointmentScrolledFrame,
                isPlaced=True,
            )
            initCoords = (initCoords[0], initCoords[1] + 120)


    def loadAssets(self):
        self.pfp = self.controller.buttonCreator(
            ipath="assets/Dashboard/DoctorAssets/DoctorProfilePicture.png",
            x=20, y=100, classname="profilepicture", root=self.parent,
            buttonFunction=lambda: [print('hello')]
        )
        d = {
            "doctor": [
                r"assets/Dashboard/DoctorAssets/DoctorYourClinic.png",
                r"assets/Dashboard/DoctorAssets/DoctorPatientPrescriptions.png",
                r"assets/Dashboard/DoctorAssets/DoctorPatientScheduling.png",
            ],
        }
        self.browseClinic = self.controller.buttonCreator(
            ipath=d["doctor"][0],
            x=20, y=380, classname="browseclinic_chip", root=self.parent,
            buttonFunction=lambda: [self.loadBrowseClinic()],
        )
        self.viewPatients = self.controller.buttonCreator(
            ipath=d["doctor"][1],
            x=20, y=460, classname="viewpatients_chip", root=self.parent,
            buttonFunction=lambda: [self.loadViewPatients()],
        )
        self.viewDoctorSchedule = self.controller.buttonCreator(
            ipath=d["doctor"][2],
            x=20, y=540, classname="viewdoctorschedule_chip", root=self.parent,
            buttonFunction=lambda: [self.loadViewAppointments()],
        )

    def loadBrowseClinic(self):
        try:
            self.mainInterface.primarypanel.grid()
            self.mainInterface.primarypanel.tkraise()
        except:
            self.mainInterface = MainBrowseClinic(
                controller=self.controller, parent=self.parent)
            self.mainInterface.loadRoleAssets(doctor=True)

    def loadViewPatients(self):
        try:
            self.patientRequests.primarypanel.grid()
            self.patientRequests.primarypanel.tkraise()
        except:
            self.patientRequests = MainPatientRequestsInterface(
                controller=self.controller, parent=self.parent)
            self.patientRequests.loadRoleAssets(doctor=True)

    def loadViewAppointments(self):
        try:
            self.appointments.primarypanel.grid()
            self.appointments.primarypanel.tkraise()
        except:
            self.appointments = MainViewAppointmentsInterface(
                controller=self.controller, parent=self.parent)
            self.appointments.loadRoleAssets(doctor=True)

    def createPatientList(self):
            prisma = self.prisma
            patients = prisma.patient.find_many(
                include={
                    "appointments": {
                        "include": {
                            "doctor": {
                                "include": {
                                    "user": True
                                }
                            },
                            "prescription": True
                        }

                    },
                    "user": True
                }
            )
            for patient in patients:
                singlePatientsApps = patient.appointments
                for app in singlePatientsApps:
                    prescriptions = app.prescription
                    for p in prescriptions:
                        t = p.title
                        d = p.desc

    