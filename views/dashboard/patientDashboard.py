from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.mainDashboard import Dashboard
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


class PatientDashboard(Frame):
    def __init__(self, parent: Dashboard = None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="primarypanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.prisma = self.controller.mainPrisma
        self.user = self.parent.user
        self.createFrames()
        self.createElements()

    def createFrames(self):
        pass

    def unloadStackedFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath=r"assets/Dashboard/PatientAssets/PatientDashboard/PatientDashboard.png",
            x=0, y=0, classname="primarypanelbg", root=self
        )

    def loadAssets(self):
        self.pfp = self.controller.buttonCreator(
            ipath="assets/Dashboard/PatientAssets/PatientProfilePicture.png",
            x=20, y=100, classname="profilepicture", root=self.parent,
            buttonFunction=lambda: [print('hello')]
        )
        d = {
            "patient": [
                r"assets/Dashboard/PatientAssets/PatientBrowseClinics.png",
                r"assets/Dashboard/PatientAssets/PatientPrescriptions.png",
                r"assets/Dashboard/PatientAssets/PatientAppointments.png",
            ],
        }
        self.browseClinic = self.controller.buttonCreator(
            ipath=d["patient"][0],
            x=20, y=380, classname="browseclinic_chip", root=self.parent,
            buttonFunction=lambda: [
                self.controller.threadCreator(
                    target=self.loadBrowseClinic
                )
            ],
        )
        self.viewPatients = self.controller.buttonCreator(
            ipath=d["patient"][1],
            x=20, y=540, classname="viewpatients_chip", root=self.parent,
            buttonFunction=lambda: [self.loadViewPatients()],
        )
        self.viewDoctorSchedule = self.controller.buttonCreator(
            ipath=d["patient"][2],
            x=20, y=460, classname="viewdoctorschedule_chip", root=self.parent,
            buttonFunction=lambda: [self.loadViewAppointments()],
        )
        self.loadDashboardButtons()

    def loadBrowseClinic(self):
        try:
            self.mainInterface.primarypanel.grid()
            self.mainInterface.primarypanel.tkraise()
        except:
            self.mainInterface = MainBrowseClinic(
                controller=self.controller, parent=self.parent)
            self.mainInterface.loadRoleAssets(patient=True)

    def loadViewPatients(self):
        try:
            self.patientRequests.primarypanel.grid()
            self.patientRequests.primarypanel.tkraise()
        except:
            self.patientRequests = MainPatientRequestsInterface(
                controller=self.controller, parent=self.parent)
            self.patientRequests.loadRoleAssets(patient=True)

    def loadViewAppointments(self):
        try:
            self.appointments.primarypanel.grid()
            self.appointments.primarypanel.tkraise()
        except:
            self.appointments = MainViewAppointmentsInterface(
                controller=self.controller, parent=self.parent)
            self.appointments.loadRoleAssets(patient=True)

    def loadDashboardButtons(self):
        CREATOR = self.controller.buttonCreator
        IP, X, Y, CN, R, BF = "ipath", "x", "y", "classname", "root", "buttonFunction"
        params = {
            "findbrowseclinic": {
                IP: "assets/Dashboard/PatientAssets/PatientDashboard/PatientFindBrowseClinic.png",
                X: 40,
                Y: 180,
                CN: "dash_findbrowseclinic",
                R: self,
                BF: lambda: [
                    self.controller.threadCreator(
                        target=self.loadBrowseClinic
                    )
                ]
            },
            # "searchbyspecialist": {
            #     IP: "assets/Dashboard/PatientAssets/PatientDashboard/SearchBySpeciality.png",
            #     X: 40,
            #     Y: 300,
            #     CN: "dash_searchbyspecialist",
            #     R: self,
            #     BF: lambda: [
            #         self.controller.threadCreator(
            #             target=self.loadBrowseClinic
            #         )
            #     ]
            # },
            "dash_viewappointments": {
                IP: "assets/Dashboard/PatientAssets/PatientDashboard/ViewAppointments.png",
                X: 40,
                Y: 300,
                CN: "dash_viewappointments",
                R: self,
                BF: lambda: [self.loadViewAppointments()]
            },
            "dash_manage_health_records": {
                IP: "assets/Dashboard/PatientAssets/PatientDashboard/ManageHealthRecords.png",
                X: 1180,
                Y: 140,
                CN: "dash_manage_health_records",
                R: self,
                BF: lambda: [self.loadViewPatients()]
            },
            "dash_manage_profile": {
                IP: "assets/Dashboard/PatientAssets/PatientDashboard/ManageCallADoctorProfile.png",
                X: 1180,
                Y: 240,
                CN: "dash_manage_profile",
                R: self,
                BF: lambda: [self.loadViewPatients()]
            }
        }
        for param in params:
            CREATOR(**params[param])

    def loadLatestAppointmentRequest(self):
        prisma = self.prisma
        prisma.appointmentrequest.find_many(
            take=2,
            where={
                "patientId": {
                    "equals": self.user.id
                }
            },
            include={
                "clinic": {
                    "include": {}
                }
            }
        )
        pass
