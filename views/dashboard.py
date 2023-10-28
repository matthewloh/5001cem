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


class Dashboard(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None, name="registration"):
        super().__init__(parent, width=1, height=1, bg="#344557", name=name)
        self.controller = controller
        self.prisma = self.controller.mainPrisma
        self.parent = parent
        self.name = name
        gridGenerator(self, 96, 54, LIGHTYELLOW)
        self.createFrames()
        self.createElements()

    def createFrames(self):
        pass

    def createElements(self):
        """
        (imagepath, x, y, classname, root)
        """
        self.staticImgLabels = [
            (r"assets/Dashboard/DashboardBG.png", 0, 0, "dashboardbg", self),
        ]
        self.staticBtns = [
            (r"assets/Dashboard/SignOut.png", 20, 980, "signoutbtn",
             self, lambda:[self.grid_remove()]),
            (r"assets/Dashboard/Settings.png", 120, 980, "settingsbtn",
             self, lambda: print("hello")),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.controller.settingsUnpacker(self.staticBtns, "button")

    def loadRoleAssets(self, patient: bool = False, doctor: bool = False, clinicAdmin: bool = False, govofficer: bool = False):
        self.profilePictures = {
            "patient": r"assets/Dashboard/PatientAssets/PatientProfilePicture.png",
            "doctor": r"assets/Dashboard/DoctorAssets/DoctorProfilePicture.png",
            "clinicAdmin": r"assets/Dashboard/ClinicAdminAssets/AdminProfilePicture.png",
            "govofficer": r"assets/Dashboard/OfficerAssets/OfficerProfilePicture.png",
        }
        self.dashboardChips = {
            "patient": [
                r"assets/Dashboard/PatientAssets/PatientBrowseClinics.png",
                r"assets/Dashboard/PatientAssets/PatientPrescriptions.png",
                r"assets/Dashboard/PatientAssets/PatientAppointments.png",
            ],
            "doctor": [
                r"assets/Dashboard/DoctorAssets/DoctorYourClinic.png",
                r"assets/Dashboard/DoctorAssets/DoctorPatientPrescriptions.png",
                r"assets/Dashboard/DoctorAssets/DoctorPatientScheduling.png",
            ],
            "clinicAdmin": [
                r"assets/Dashboard/ClinicAdminAssets/AdminManageClinic.png",
                r"assets/Dashboard/ClinicAdminAssets/AdminViewPatientRequests.png",
                r"assets/Dashboard/ClinicAdminAssets/AdminViewDoctorSchedule.png",
            ],
            "govofficer": [
                r"assets/Dashboard/OfficerAssets/OfficerManageClinics.png",
                r"assets/Dashboard/OfficerAssets/OfficerClinicRequests.png",
            ],
        }
        if patient:
            role = "patient"
            self.primarypanel = PatientDashboard(
                parent=self, controller=self.controller)
            self.primarypanel.grid(
                row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        elif doctor:
            role = "doctor"
            self.primarypanel = DoctorDashboard(
                parent=self, controller=self.controller)
            self.primarypanel.grid(
                row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        elif clinicAdmin:
            role = "clinicAdmin"
            self.primarypanel = ClinicAdminDashboard(
                parent=self, controller=self.controller)
            self.primarypanel.grid(
                row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        elif govofficer:
            role = "govofficer"
            self.primarypanel = GovOfficerDashboard(
                parent=self, controller=self.controller)
            self.primarypanel.grid(
                row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        else:
            return
        self.pfp = self.controller.buttonCreator(
            ipath=self.profilePictures[role],
            x=20, y=100, classname="profilepicture", root=self,
            buttonFunction=lambda: [print(f"{role} pfp clicked")],
        )
        self.dashboardChip = self.controller.buttonCreator(
            ipath=r"assets/Dashboard/DashboardChip.png",
            x=20, y=300, classname="dashboardchip", root=self,
            buttonFunction=lambda: [print(f"home dashboard clicked")],
        )
        self.dashboardChipButtons = []
        for i, chip in enumerate(self.dashboardChips[role]):
            self.dashboardChipButtons.append(self.controller.buttonCreator(
                ipath=chip,
                x=20, y=380 + (i * 80), classname=f"dashboardchip{i}", root=self,
                buttonFunction=lambda num=i: [
                    print(f"{role} chip {num} clicked")],
            ))


class PatientDashboard(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="primarypanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath=r"assets/Dashboard/PatientAssets/PatientPrimaryPanelBG.png",
            x=0, y=0, classname="primarypanelbg", root=self
        )


class DoctorDashboard(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="primarypanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath=r"assets/Dashboard/DoctorAssets/DoctorPrimaryPanelBG.png",
            x=0, y=0, classname="primarypanelbg", root=self
        )


class ClinicAdminDashboard(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="primarypanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath=r"assets/Dashboard/ClinicAdminAssets/AdminPrimaryPanelBG.png",
            x=0, y=0, classname="primarypanelbg", root=self
        )
        view = tkintermapview.TkinterMapView(
            master=self, width=800, height=600, corner_radius=0
        )
        view.place(relx=0.5, rely=0.5, anchor=CENTER)


class GovOfficerDashboard(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="primarypanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath=r"assets/Dashboard/OfficerAssets/OfficerPrimaryPanelBG.png",
            x=0, y=0, classname="primarypanelbg", root=self
        )
