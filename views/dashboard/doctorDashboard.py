from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.mainDashboard import Dashboard
import calendar
from prisma.models import Appointment
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
from datetime import datetime


class DoctorDashboard(Frame):
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
        self.ScrolledFrame()
        self.createPatientList()
        self.createNavigateButton()
        self.getClinicData()

    def createFrames(self):
        pass

    def unloadStackedFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/DoctorAssets/DoctorDashboard.png",
            x=0, y=0, classname="primarypanelbg", root=self
        )

    def ScrolledFrame(self):
        prisma = self.prisma
        doctor = prisma.doctor.find_first(
            where={
                "userId": self.user.id
            }
        )
        viewAppointment = prisma.appointment.find_many(
            where={
                "doctorId": doctor.id
            },
            include={
                "appRequest": {
                    "include": {
                        "patient": {
                            "include": {
                                "user": True
                            }
                        }
                    }
                },
                 "prescription": True
            }
        )

        h = len(viewAppointment) * 120
        if h < 760:
            h = 760
        self.appointmentListFrame = ScrolledFrame(
            master=self, width=1500, height=h, autohide=True, bootstyle="DoctorDashboard.bg"
        )
        self.appointmentListFrame.grid_propagate(False)
        self.appointmentListFrame.place(x=48, y=279, width=1040, height=722)
        COORDS = (5, 5)
        for appointments in viewAppointment:

            patientName = appointments.appRequest.patient.user.fullName
            patientContact = appointments.appRequest.patient.user.contactNo

            X = COORDS[0]
            Y = COORDS[1]
            R = self.appointmentListFrame
            self.controller.labelCreator(
                x=X, y=Y, classname=f"{appointments.id}_bg", root=R,
                ipath="assets/Dashboard/DoctorAssets/DoctorListButton/DashboardAppointmentbutton.png",
                isPlaced=True,
            )
            UpAppPatientName = self.controller.scrolledTextCreator(
                x=X+15, y=Y+32, width=145, height=60, root=R, classname=f"{appointments.id}_name",
                bg="#3D405B", hasBorder=False,
                text=f"{patientName}", font=("Inter", 20), fg=WHITE,
                isDisabled=True, isJustified=True, justification="center",
            )
            UpAppPatientContact = self.controller.scrolledTextCreator(
                x=X+180, y=Y+32, width=145, height=60, root=R, classname=f"{appointments.id}_phone_num",
                bg="#3D405B", hasBorder=False,
                text=f"{patientContact}", font=("Inter", 18), fg=WHITE,
                isDisabled=True, isJustified=True, justification="center",
            )
            patientAppDate = appointments.startTime

            date_part = patientAppDate.date()
            time_part = patientAppDate.time()

            date_string = date_part.strftime('%Y-%m-%d')
            time_string = time_part.strftime('%H:%M:%S')
            UpAppDate = self.controller.scrolledTextCreator(
                x=X+350, y=Y+32, width=145, height=60, root=R, classname=f"{appointments.id}_App_date",
                bg="#3D405B", hasBorder=False,
                text=f"{date_string}", font=("Inter", 18), fg=WHITE,
                isDisabled=True, isJustified=True, justification="center",
            )
            UpAppTime = self.controller.scrolledTextCreator(
                x=X+515, y=Y+32, width=145, height=60, root=R, classname=f"{appointments.id}_App_time",
                bg="#3D405B", hasBorder=False,
                text=f"{time_string}", font=("Inter", 18), fg=WHITE,
                isDisabled=True, isJustified=True, justification="center",
            )
            self.controller.buttonCreator(
                ipath="assets/Dashboard/DoctorAssets/DoctorListButton/HealthRecord.png",
                classname=f"HealthReocrd{appointments.id}", root=R,
                x=X+670, y=Y+25, buttonFunction=lambda t = appointments.id: [print(f"record {t}")],
                isPlaced=True
            )
            self.controller.buttonCreator(
                ipath="assets/Dashboard/DoctorAssets/DoctorListButton/AddPrescription.png",
                classname=f"AcceptPrescripton{appointments.id}", root=R,
                x=844, y=Y+25, buttonFunction=lambda a=appointments: [
                self.loadIntoAppointmentView(a)],
                isPlaced=True,
            )
            COORDS = (COORDS[0], COORDS[1] + 120)

    # def createImageClinic(self):
        # prisma = self.prisma
        # viewClinicImg = prisma.clinic.find_many(
        # )
    # "assets/Dashboard/DoctorAssets/DoctorClinic.png",
    # "assets/Dashboard/DoctorAssets/DoctorPrescriptionRequest.png",

    

    def getClinicData(self):
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

            ClinicName = self.controller.scrolledTextCreator(
               x=1377, y=150, width=244, height=34, classname=f"clinic_name_dashboard",
               root=self, bg="#ECECEC", hasBorder=TRUE,
               text=f"{clinic_name}", font=("Inter", 18), fg=BLACK,
               isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            ClinicAddress = self.controller.scrolledTextCreator(
                x=1394, y=238, width=227, height=97, classname=f"clinic_address_dashboard",
                root=self, bg="#ECECEC", hasBorder=True,
                text=f"{clinic_address}", font=("Inter", 18), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

    def createNavigateButton(self):
        self.navigateToClinicPage = self.controller.buttonCreator(
            ipath="assets/Dashboard/DoctorAssets/DoctorListButton/YourClinicMoreDetails.png", x=1355, y=455,
            classname="ButtonToYourClinic", root=self, buttonFunction=lambda: [print("print=ToClinic")],
            isPlaced=True,
        )

    def loadAssets(self):
        self.pfp = self.controller.buttonCreator(
            ipath="assets/Dashboard/DoctorAssets/DoctorProfilePicture.png",
            x=20, y=100, classname="profilepicture", root=self.parent,
            buttonFunction=lambda: [print('hello')]
        )
        d = {
            "doctor": [
                "assets/Dashboard/DoctorAssets/DoctorYourClinic.png",
                "assets/Dashboard/DoctorAssets/DoctorPatientPrescriptions.png",
                "assets/Dashboard/DoctorAssets/DoctorPatientScheduling.png",
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
                "madeAppRequests": {
                    "include": {
                        "appointments": {
                            "include": {
                                "doctor": {
                                    "include": {
                                        "user": True
                                    }
                                },
                                "prescription": True
                            }
                        }
                    }
                },
                "user": True
            }
        )
        #for patient in patients:
           # print(patient)

    def loadIntoAppointmentView(self, appointment: Appointment):
        try:
            self.patientRequests.primarypanel.grid()
            self.patientRequests.primarypanel.tkraise()
        except:
            self.patientRequests = MainPatientRequestsInterface(
                controller=self.controller, parent=self.parent)
            self.patientRequests.loadRoleAssets(doctor=True)
        self.patientRequests.primarypanel.loadAppointment(
            appointment=appointment)


