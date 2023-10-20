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
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="primarypanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)

        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.dashboardButtons()
        self.createFrames()
        self.createDoctorList()

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
        self.addListsFrame = self.controller.frameCreator(
            x=0, y=0, classname="addlist", root=self,framewidth=1680, frameheight=1080 
        )
        self.addListsFrame.grid_remove()
        pass
        self.deleteListsFrame = self.controller.frameCreator(
            x=0, y=0, classname="deletelist", root=self,framewidth=1680, frameheight=1080 
        )
        self.deleteListsFrame.grid_remove()
        pass
  
    def createElements(self):
        self.bg = self.controller.labelCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/AdminDashboard/Homepage.png",
            x=0, y=0, classname="homepage", root=self
        )
        self.imgLabels = [
            ("assets/Dashboard/ClinicAdminAssets/AddList/AddList1.png", 0, 0, "addlistimage", self.addListsFrame),
            ("assets/Dashboard/ClinicAdminAssets/DeleteList/Background.png", 0, 0, "deletelistimage", self.deleteListsFrame)
        ]
        self.controller.settingsUnpacker(self.imgLabels, "label")
        
    def dashboardButtons(self):
        d = {
            "adminDashboard": [
                "assets/Dashboard/ClinicAdminAssets/AdminDashboard/AddDoctor.png",
                "assets/Dashboard/ClinicAdminAssets/AdminDashboard/DeleteDoctor.png",
                "assets/Dashboard/ClinicAdminAssets/AdminDashboard/Refresh.png",
                "assets/Dashboard/ClinicAdminAssets/AdminDashboard/Refresh.png"
            ]
        }
        self.addDoctor = self.controller.buttonCreator(
            ipath=d["adminDashboard"][0],
            x=140, y=440, classname="adddoctor", root=self,
            buttonFunction=lambda: [self.addListsFrame.grid() , self.addListsFrame.tkraise() ],
        )
        self.deleteDoctor = self.controller.buttonCreator(
            ipath=d["adminDashboard"][1],
            x=380, y=440, classname="deletedoctor", root=self,
            buttonFunction=lambda: [self.deleteListsFrame.grid() , self.deleteListsFrame.tkraise()],
        )
        self.viewDoctorSchedule = self.controller.buttonCreator(
            ipath=d["adminDashboard"][2],
            x=1480, y=60, classname="refresh1", root=self,
            buttonFunction=lambda: [print('refresh')],
        )
        self.viewGRDRequests = self.controller.buttonCreator(
            ipath=d["adminDashboard"][3],
            x=1480, y=580, classname="refresh2", root=self,
            buttonFunction=lambda: [print('refresh')],
        )
        
    def createDoctorList(self):
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
            master=self, width=920, height=h, autohide=True, bootstyle="bg-round")
        self.doctorsScrolledFrame.place(
            x=680, y=145, width=920, height=375
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
                buttonFunction=lambda:[print(doctor)]
            )
            initialCoordinates = (
                initialCoordinates[0], initialCoordinates[1] + 100
            )

    

   