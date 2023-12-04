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
from prisma.models import Patient
import tkintermapview
from pendulum import timezone
from PIL import Image, ImageTk, ImageOps
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
        self.patient: Patient = None
        self.createFrames()
        self.createElements()

    def createFrames(self):
        pass

    def unloadStackedFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/PatientAssets/PatientDashboard/PatientDashboard.png",
            x=0, y=0, classname="primarypanelbg", root=self
        )

    def loadAssets(self):
        self.patient = self.prisma.patient.find_first(
            where={"userId": self.user.id},
            include={
                "user": True,
                "healthRecord": True,
                "madeAppRequests": {
                    "include": {
                        "clinic": True,
                        "appointments": {
                            "include": {
                                "doctor": {
                                    "include": {
                                        "user": True,
                                    }
                                },
                                "prescription": True,
                            }
                        }
                    }
                }
            }
        )
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
        self.load_latest_appointment_request()

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
            # "dash_manage_profile": {
            #     IP: "assets/Dashboard/PatientAssets/PatientDashboard/ManageCallADoctorProfile.png",
            #     X: 1180,
            #     Y: 240,
            #     CN: "dash_manage_profile",
            #     R: self,
            #     BF: lambda: [self.loadViewPatients()]
            # }
        }
        for param in params:
            CREATOR(**params[param])

    def load_latest_appointment_request(self):
        prisma = self.prisma
        app_req = prisma.appointmentrequest.find_many(
            where={
                "patientId": self.patient.id,
            },
            include={
                "clinic": True,
                "appointments": {
                    "include": {
                        "doctor": {
                            "include": {
                                "user": True,
                            }
                        },
                        "prescription": True,
                    }
                }
            },
            order={"createdAt": "desc"},
            take=1
        )
        req = app_req[0]
        clinic = req.clinic
        R = self
        BG = "#ffffff"
        FONT = ("Inter", 14)
        img = self.controller.decodingBase64Data(req.clinic.clinicImg)
        img = ImageOps.contain(img, (200, 200), Image.Resampling.BICUBIC)
        self.clinicImage = self.controller.buttonCreator(
            x=620, y=180, classname=f"dash_req_loadedclinic_image_{req.id}", root=R,
            ipath="assets/BrowseClinic/Patient/BrowseSingleClinic/ClinicImagePlaceholder.png",
            bg="#ffffff",
            isPlaced=True,
        )
        self.controller.imageDict[f"dash_req_loadedclinic_image_{req.id}"] = ImageTk.PhotoImage(
            img
        )
        newImage = self.controller.imageDict[f"dash_req_loadedclinic_image_{req.id}"]
        self.clinicImage.configure(image=newImage, width=200, height=200)
        self.clinicImage.place(x=620, y=180, width=200, height=200)

        self.controller.scrolledTextCreator(
            x=700, y=400, width=120, height=60, root=R,
            classname=f"dash_req_loadedclinic_name_{req.id}",
            bg=BG, hasBorder=False,
            text=clinic.name, font=FONT, fg=BLACK,
            isDisabled=True, isJustified=True,
            hasVbar=False,
        )
        # # Status
        self.controller.scrolledTextCreator(
            x=940, y=400, width=120, height=60, root=R,
            classname=f"dash_req_status_{req.id}",
            bg=BG, hasBorder=False,
            text=f"{req.reqStatus}", font=FONT, fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False,
        )
        # # Speciality Wanted & Additional Info
        self.controller.scrolledTextCreator(
            x=700, y=480, width=360, height=60, root=R,
            classname=f"dash_req_speciality_{req.id}",
            bg=BG, hasBorder=False,
            text=f"{req.specialityWanted}\n{req.additionalInfo}", font=FONT, fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False,
        )
        # # Preferred Date
        self.controller.scrolledTextCreator(
            x=700, y=560, width=360, height=40, root=R,
            classname=f"dash_req_preferred_date_{req.id}",
            bg=BG, hasBorder=False,
            text=f"{req.preferredDate}", font=FONT, fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False,
        )
        # Preferred Time
        self.controller.scrolledTextCreator(
            x=700, y=620, width=360, height=40, root=R,
            classname=f"dash_req_preferred_time_{req.id}",
            bg=BG, hasBorder=False,
            text=f"{req.preferredTime}", font=FONT, fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False,
        )
        # Created Ago
        KL = timezone("Asia/Kuala_Lumpur")
        created = KL.convert(req.createdAt)
        now = KL.convert(datetime.now())
        timedelta = now - created
        if timedelta.days > 0:
            diffText = f"{timedelta.days} days ago"
        elif timedelta.seconds//3600 > 0:
            diffText = f"{timedelta.seconds//3600} hours ago"
        elif timedelta.seconds//60 > 0:
            diffText = f"{timedelta.seconds//60} minutes ago"
        else:
            diffText = f"{timedelta.seconds} seconds ago"
        self.controller.scrolledTextCreator(
            x=860, y=200, width=200, height=40, root=R,
            classname=f"dash_req_created_ago_{req.id}",
            bg=BG, hasBorder=False,
            text=diffText, font=FONT, fg=BLACK,
            isDisabled=True, isJustified=True,
            hasVbar=False,
        )
        self.controller.buttonCreator(
            ipath="assets/Dashboard/PatientAssets/PatientDashboard/ViewAppointmentsDashMiddle.png",
            x=860, y=280, classname=f"dash_{req.id}_viewappointments", root=R,
            isPlaced=True,
        )
        self.controller.scrolledTextCreator(
            x=875, y=285, width=50, height=50, root=R,
            classname=f"dash_req_appointments_created_{req.id}",
            bg="#86cff5", hasBorder=False,
            text=f"{len(req.appointments)}", font=FONT, fg=WHITE,
            isDisabled=True, isJustified=True,
            hasVbar=False,
        )
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
