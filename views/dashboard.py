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
            (r"assets\Dashboard\DashboardBG.png", 0, 0, "dashboardbg", self),
        ]
        self.staticBtns = [
            (r"assets\Dashboard\SignOut.png", 20, 980, "signoutbtn",
             self, lambda:[self.grid_remove()]),
            (r"assets\Dashboard\Settings.png", 120, 980, "settingsbtn",
             self, lambda: print("hello")),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.controller.settingsUnpacker(self.staticBtns, "button")
        exampleList = []
        [exampleList.append("Thing " + str(i))
         for i in range(50) if i % 2 == 0]
        h = len(exampleList) * 100 + 20
        if h < 960:
            h = 960
        self.exampleScrolledFrame = ScrolledFrame(
            master=self, width=480, height=h, autohide=True, bootstyle="bg-round"
        )
        self.exampleScrolledFrame.place(x=240, y=100, width=480, height=960)
        initypos = 0
        for thing in exampleList:
            self.controller.textElement(
                ipath=r"assets\Dashboard\thingbg.png", x=20, y=initypos+20,
                classname=f"thing{thing}", root=self.exampleScrolledFrame,
                text=thing, size=32, font=INTER,
                isPlaced=True,
            )
            initypos += 120

    def loadRoleAssets(self, patient: bool = False, doctor: bool = False, clinicAdmin: bool = False, govofficer: bool = False):
        self.profilePictures = {
            "patient": r"assets\Dashboard\PatientAssets\PatientProfilePicture.png",
            "doctor": r"assets/Dashboard/DoctorAssets/DoctorProfilePicture.png",
            "clinicAdmin": r"assets/Dashboard/ClinicAdminAssets/AdminProfilePicture.png",
            "govofficer": r"assets/Dashboard/OfficerAssets/OfficerProfilePicture.png",
        }
        self.dashboardChips = {
            "patient": [
                r"assets\Dashboard\PatientAssets\PatientBrowseClinics.png",
                r"assets\Dashboard\PatientAssets\PatientPrescriptions.png",
                r"assets\Dashboard\PatientAssets\PatientAppointments.png",
            ],
            "doctor": [
                r"assets\Dashboard\DoctorAssets\DoctorYourClinic.png",
                r"assets\Dashboard\DoctorAssets\DoctorPatientPrescriptions.png",
                r"assets\Dashboard\DoctorAssets\DoctorPatientScheduling.png",
            ],
            "clinicAdmin": [
                r"assets\Dashboard\ClinicAdminAssets\AdminManageClinic.png",
                r"assets\Dashboard\ClinicAdminAssets\AdminViewPatientRequests.png",
                r"assets\Dashboard\ClinicAdminAssets\AdminViewDoctorSchedule.png",
            ],
            "govofficer": [
                r"assets\Dashboard\OfficerAssets\OfficerManageClinics.png",
            ],
        }
        if patient:
            role = "patient"
        elif doctor:
            role = "doctor"
        elif clinicAdmin:
            role = "clinicAdmin"
        elif govofficer:
            role = "govofficer"
        else:
            return
        self.pfp = self.controller.buttonCreator(
            ipath=self.profilePictures[role],
            x=20, y=100, classname="profilepicture", root=self,
            buttonFunction=lambda: [print(f"{role} pfp clicked")],
        )
        self.dashboardChip = self.controller.buttonCreator(
            ipath=r"assets\Dashboard\DashboardChip.png",
            x=20, y=300, classname="dashboardchip", root=self,
            buttonFunction=lambda: [print(f"{role} dashboard chip clicked")],
        )
        self.dashboardChipButtons = []
        for i, chip in enumerate(self.dashboardChips[role]):
            self.dashboardChipButtons.append(self.controller.buttonCreator(
                ipath=chip,
                x=20, y=300 + (i * 100), classname=f"dashboardchip{i}", root=self,
                buttonFunction=lambda num = i: [
                    print(f"{role} dashboard chip {num} clicked")],
            ))
