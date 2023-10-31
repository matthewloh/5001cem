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
from views.mainGRDRequests import MainGRDRequestsInterface
from views.mainPatientRequests import MainPatientRequestsInterface
from views.mainViewAppointments import MainViewAppointmentsInterface


class ClinicAdminDashboard(Frame):
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
        self.dashboardButtons()
        self.createList()
        self.loadDoctorsAndFilterBySpeciality()

    def loadAssets(self):
        self.pfp = self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/AdminProfilePicture.png",
            x=20, y=100, classname="profilepicture", root=self.parent,
            buttonFunction=lambda: [print('hello')]
        )
        d = {
            "clinicAdmin": [
                "assets/Dashboard/ClinicAdminAssets/AdminManageClinic.png",
                "assets/Dashboard/ClinicAdminAssets/AdminViewPatientRequests.png",
                "assets/Dashboard/ClinicAdminAssets/AdminViewDoctorSchedule.png",
                "assets/Dashboard/ClinicAdminAssets/AdminGRDRequests.png"
            ],
        }
        self.browseClinic = self.controller.buttonCreator(
            ipath=d["clinicAdmin"][0],
            x=20, y=380, classname="browseclinic_chip", root=self.parent,
            buttonFunction=lambda: [self.loadBrowseClinic()],
        )
        self.viewPatients = self.controller.buttonCreator(
            ipath=d["clinicAdmin"][1],
            x=20, y=460, classname="viewpatients_chip", root=self.parent,
            buttonFunction=lambda: [self.loadViewPatients()],
        )
        self.viewDoctorSchedule = self.controller.buttonCreator(
            ipath=d["clinicAdmin"][2],
            x=20, y=540, classname="viewdoctorschedule_chip", root=self.parent,
            buttonFunction=lambda: [self.loadViewAppointments()],
        )
        self.viewGRDRequests = self.controller.buttonCreator(
            ipath=d["clinicAdmin"][3],
            x=20, y=620, classname="grdrequests_chip", root=self.parent,
            buttonFunction=lambda: [self.loadGRDRequests()],
        )

    def loadBrowseClinic(self):
        try:
            self.mainInterface.primarypanel.grid()
            self.mainInterface.primarypanel.tkraise()
        except:
            self.mainInterface = MainBrowseClinic(
                controller=self.controller, parent=self.parent)
            self.mainInterface.loadRoleAssets(clinicAdmin=True)

    def loadViewPatients(self):
        try:
            self.patientRequests.primarypanel.grid()
            self.patientRequests.primarypanel.tkraise()
        except:
            self.patientRequests = MainPatientRequestsInterface(
                controller=self.controller, parent=self.parent)
            self.patientRequests.loadRoleAssets(clinicAdmin=True)

    def loadViewAppointments(self):
        try:
            self.appointments.primarypanel.grid()
            self.appointments.primarypanel.tkraise()
        except:
            self.appointments = MainViewAppointmentsInterface(
                controller=self.controller, parent=self.parent)
            self.appointments.loadRoleAssets(clinicAdmin=True)

    def loadGRDRequests(self):
        try:
            self.grdRequests.primarypanel.grid()
            self.grdRequests.primarypanel.tkraise()
        except:
            self.grdRequests = MainGRDRequestsInterface(
                controller=self.controller, parent=self.parent)
            self.grdRequests.loadRoleAssets(clinicAdmin=True)

    def createFrames(self):
        self.ListFrame = self.controller.frameCreator(
            x=0, y=0, classname="listframe", root=self, framewidth=1680, frameheight=1080
        )
        self.unloadStackedFrames()

    def unloadStackedFrames(self):
        self.ListFrame.grid_remove()
       
    def createElements(self):
        self.bg = self.controller.labelCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/AdminDashboard/Homepage.png",
            x=0, y=0, classname="homepage", root=self
        )
        self.imgLabels = [
            ("assets/Dashboard/ClinicAdminAssets/Add&DeleteList/Add&DeleteBg.png",
             0, 0, "listimage", self.ListFrame)
        ]
        self.controller.settingsUnpacker(self.imgLabels, "label")

    def loadDoctorsAndFilterBySpeciality(self):
        prisma = self.prisma
        self.doctors = prisma.doctor.find_many(
            include={
                "user": True,
            }
        )
        self.specialitiesAndDoctors = {}
        for doctor in self.doctors:
            if doctor.speciality not in self.specialitiesAndDoctors.keys():
                self.specialitiesAndDoctors[doctor.speciality] = []
            self.specialitiesAndDoctors[doctor.speciality].append(doctor)
        self.specialitySelected = StringVar()
        keyOptionsForMenuButton = list(self.specialitiesAndDoctors.keys())
        self.specialityMenuButton = self.controller.menubuttonCreator(
            x=140, y=240, classname="specialitymenubutton", root=self,
            width=400, height=80, listofvalues=keyOptionsForMenuButton,
            variable=self.specialitySelected,
            command=lambda: [
                self.loadDoctorsBySpeciality(self.specialitySelected.get())],
            text="Select Speciality"
        )
    
    def loadDoctorsAndFilterByAppointment(self):
        prisma = self.prisma
        self.doctors = prisma.doctor.find_many(
            include={
                "user": True,
            }
        )
        self.appointmentsAndDoctors = {}
        for doctor in self.doctors:
            if doctor.doctorApptSchedule not in self.appointmentsAndDoctors.keys():
                self.appointmentsAndDoctors[doctor.doctorApptSchedule] = []
            self.appointmentsAndDoctors[doctor.doctorApptSchedule].append(doctor)
        self.doctorApptScheduleSelected = StringVar()
        keyOptionsForMenuButton = list(self.appointmentsAndDoctors.keys())
        self.doctorApptScheduleMenuButton = self.controller.menubuttonCreator(
            x=140, y=640, classname="doctorApptSchedulemenubutton", root=self,
            width=400, height=80, listofvalues=keyOptionsForMenuButton,
            variable=self.specialitySelected,
            command=lambda: [
                self.loadDoctorsAndFilterByAppointment(self.doctorApptScheduleSelected.get())],
            text="Select doctorApptSchedule"
        )


    def loadDoctorsBySpeciality(self, option):
        doctors = self.specialitiesAndDoctors[option]
        h = len(doctors) * 100
        if h < 375:
            h = 375
        self.doctorsScrolledFrame = ScrolledFrame(
            master=self, width=920, height=h, autohide=True, bootstyle="minty-bg")
        self.doctorsScrolledFrame.place(
            x=680, y=145, width=920, height=370
        )
        initialCoordinates = (20, 20)
        for doctor in doctors:
            x = initialCoordinates[0]
            y = initialCoordinates[1]
            self.controller.textElement(
                ipath="assets/Dashboard/ClinicAdminAssets/AdminDashboard/ListButton.png",
                x=x, y=y, classname=f"doctorlistbg{doctor.id}", root=self.doctorsScrolledFrame,
                text=f"{doctor.user.fullName}", size=30, font=INTER,
                isPlaced=True,
                buttonFunction=lambda d=doctor: [print(d)]
            )
            initialCoordinates = (
                initialCoordinates[0], initialCoordinates[1] + 100
            )

    def dashboardButtons(self):
        d = {
            "adminDashboard": [
                "assets/Dashboard/ClinicAdminAssets/Add&DeleteList/Add&DeleteDoctor.png",
                "assets/Appointments/ReturnButton.png",
                "assets/Dashboard/ClinicAdminAssets/ScrollFrame/scrollrefreshbutton.png"
            ]
        }
        self.Listbutton = self.controller.buttonCreator(
            ipath=d["adminDashboard"][0],
            x=140, y=440, classname="listbutton", root=self,
            buttonFunction=lambda: [
                self.ListFrame.grid(), self.ListFrame.tkraise()],
        )
        self.Returnbutton = self.controller.buttonCreator(
            ipath=d["adminDashboard"][1],
            x=60, y=40, classname="returnbutton", root=self.ListFrame,
            buttonFunction=lambda: [self.ListFrame.grid_remove()],
        )
        self.Refreshbutton = self.controller.buttonCreator(
            ipath=d["adminDashboard"][2],
            x=1400, y=140, classname="refreshbutton", root=self.ListFrame,
            buttonFunction=lambda: [print('refresh')],
        )

    def createList(self):
        prisma = self.prisma
        doctors = prisma.doctor.find_many(
            include={
                "user": True,
            }
        )
        h = len(doctors) * 100
        if h < 375:
            h = 375

        self.doctorsScrolledFrame = ScrolledFrame(
            master=self, width=920, height=h, autohide=True, bootstyle="minty-bg")
        self.doctorsScrolledFrame.place(
            x=680, y=145, width=920, height=375
        )
        initialCoordinates = (20, 20)
        for doctor in doctors:
            x = initialCoordinates[0]
            y = initialCoordinates[1]
            self.controller.textElement(
                ipath="assets/Dashboard/ClinicAdminAssets/ScrollFrame/scrolldashboardbutton.png",
                x=x, y=y, classname=f"doctorlistbg{doctor.id}", root=self.doctorsScrolledFrame,
                text=f"{doctor.user.fullName}", size=30, font=INTER,
                isPlaced=True,
                buttonFunction=lambda: [print(doctor)]
            )
            initialCoordinates = (
                initialCoordinates[0], initialCoordinates[1] + 100
            )

        exampleList = []
        [exampleList.append("Thing " + str(i))
         for i in range(30) if i % 2 == 0]
        h = len(exampleList) * 120
        if h < 650:
            h = 650
        self.ListScrolledFrame = ScrolledFrame(
            master=self.ListFrame, width=1500, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.ListScrolledFrame.grid_propagate(False)
        self.ListScrolledFrame.place(x=80, y=280, width=1500, height=650)
        initialcoordinates = (20,20)
        for list in exampleList:
            x = initialcoordinates[0]
            y = initialcoordinates[1]
            self.controller.textElement(
                ipath=r"assets/Dashboard/ClinicAdminAssets/ScrollFrame/scrollbutton.png", x=x, y=y,
                classname=f"list{list}", root=self.ListScrolledFrame,
                text=list, size=30, font=INTER,
                isPlaced=True,
            )
            initialcoordinates = (
                initialcoordinates[0], initialcoordinates[1] + 120
            )

    