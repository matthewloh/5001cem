from __future__ import annotations
from typing import TYPE_CHECKING

from views.mainPatientRequests import MainPatientRequestsInterface
if TYPE_CHECKING:
    from views.dashboard.adminDashboard import ClinicAdminDashboard
from abc import ABC, abstractmethod
import calendar
import re
import threading
from tkinter import *
from tkinter import messagebox
from prisma.models import Appointment, AppointmentRequest
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
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime


class AdminManageAppointments(Frame):
    def __init__(self, parent: ClinicAdminDashboard = None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="appointmentspanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.user = self.parent.user
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.appointmentImgLabels()
        self.appointmentButtons()
        self.appointmentList()

    def createFrames(self):
        self.createAppointmentsFrame = self.controller.frameCreator(
            x=0, y=0, classname="createframe", root=self, framewidth=1680, frameheight=1080
        )
        self.manageAppointmentsFrame = self.controller.frameCreator(
            x=0, y=0, classname="manageframe", root=self, framewidth=1680, frameheight=1080
        )
        self.unloadStackedFrames()

    def unloadStackedFrames(self):
        self.createAppointmentsFrame.grid_remove()
        self.manageAppointmentsFrame.grid_remove()

    def appointmentImgLabels(self):
        self.bg = self.controller.labelCreator(
            ipath="assets/Appointments/Homepage/AppointmentViewBg.png",
            x=0, y=0, classname="appointmenthomepage", root=self
        )
        self.imgLabels = [
            ("assets/Appointments/Creation/CreationBg.png",
             0, 0, "creationimage", self.createAppointmentsFrame),
            ("assets/Appointments/Management/ManagementBg.png",
             0, 0, "manageimage", self.manageAppointmentsFrame)
        ]
        self.controller.settingsUnpacker(self.imgLabels, "label")

    def appointmentButtons(self):
        d = {
            "appointmentButtons": [
                "assets/Appointments/Homepage/CreateAppointments.png",
                "assets/Appointments/Homepage/ManageAppointments.png",
                "assets/Dashboard/ClinicAdminAssets/ScrollFrame/scrollrefreshbutton.png",
                "assets/Appointments/ReturnButton.png",
                "assets/Appointments/Creation/BookAppointmentBtn.png",
                "assets/Appointments/Creation/BackBtn.png",
                "assets/Appointments/Creation/NextBtn.png",
                "assets/Appointments/ReturnButton.png",
                "assets/Appointments/Management/ViewBtn.png",
                "assets/Appointments/Management/AppointmentRefreshBtn.png",
                "assets/Appointments/Management/CalendarRefreshBtn.png",
                "assets/Appointments/Management/CancelBtn.png",
                "assets/Appointments/Management/SubmitBtn.png",
                "assets/Appointments/Management/CancelBtn.png",
                "assets/Appointments/Management/DeleteBtn.png",
                "assets/Appointments/Management/BackBtn.png",
                "assets/Appointments/Management/NextBtn.png",
            ]
        }
        # Appointment Dashboard
        self.creationButton = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][0],
            x=620, y=800, classname="createbutton", root=self,
            buttonFunction=lambda: [
                self.createAppointmentsFrame.grid(), self.createAppointmentsFrame.tkraise()],
        )
        self.managementButton = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][1],
            x=1140, y=800, classname="managebutton", root=self,
            buttonFunction=lambda: [
                self.manageAppointmentsFrame.grid(), self.manageAppointmentsFrame.tkraise()],
        )
        self.refreshBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][2],
            x=1450, y=120, classname="viewAppointmentrefresh", root=self,
            buttonFunction=lambda: print("view appointment requests"), isPlaced=True
        )
        # Appointment Creation
        self.returncreationBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][3],
            x=100, y=80, classname="returncreation", root=self.createAppointmentsFrame,
            buttonFunction=lambda: [
                self.createAppointmentsFrame.grid_remove()],
        )
        self.bookappointmentBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][4],
            x=740, y=920, classname="bookappointmentrefresh", root=self.createAppointmentsFrame,
            buttonFunction=lambda: [self.createAppointmentsFrame.grid()], isPlaced=True
        )
        self.backBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][5],
            x=930, y=502, classname="backbutton", root=self.createAppointmentsFrame,
            buttonFunction=lambda: [self.createAppointmentsFrame.grid()], isPlaced=True
        )
        self.nextBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][6],
            x=1020, y=502, classname="nextbutton", root=self.createAppointmentsFrame,
            buttonFunction=lambda: [self.createAppointmentsFrame.grid()], isPlaced=True
        )
        # Appointment Management
        self.returnmanagementBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][7],
            x=40, y=80, classname="returnmanagement", root=self.manageAppointmentsFrame,
            buttonFunction=lambda: [
                self.manageAppointmentsFrame.grid_remove()],
        )
        self.viewBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][8],
            x=420, y=240, classname="viewbutton", root=self.manageAppointmentsFrame,
            buttonFunction=lambda: [self.manageAppointmentsFrame.grid()],
        )
        self.appointmentrefreshBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][9],
            x=980, y=200, classname="appointmentrefreshbutton", root=self.manageAppointmentsFrame,
            buttonFunction=lambda: [self.manageAppointmentsFrame.grid()],
        )
        self.calendarrefreshBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][10],
            x=1540, y=180, classname="calendarrefreshbutton", root=self.manageAppointmentsFrame,
            buttonFunction=lambda: [self.manageAppointmentsFrame.grid()],
        )
        self.cancelBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][11],
            x=630, y=660, classname="cancelbutton", root=self.manageAppointmentsFrame,
            buttonFunction=lambda: [self.manageAppointmentsFrame.grid()],
        )
        self.submitBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][12],
            x=840, y=660, classname="submitbutton", root=self.manageAppointmentsFrame,
            buttonFunction=lambda: [self.manageAppointmentsFrame.grid()],
        )
        self.cancelDeletionBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][13],
            x=630, y=820, classname="canceldeletionbutton", root=self.manageAppointmentsFrame,
            buttonFunction=lambda: [self.manageAppointmentsFrame.grid()],
        )
        self.deleteBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][14],
            x=840, y=820, classname="deletebutton", root=self.manageAppointmentsFrame,
            buttonFunction=lambda: [self.manageAppointmentsFrame.grid()],
        )
        self.backBtn2 = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][15],
            x=1430, y=720, classname="backbutton2", root=self.manageAppointmentsFrame,
            buttonFunction=lambda: [self.manageAppointmentsFrame.grid()], isPlaced=True
        )
        self.nextBtn2 = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][16],
            x=1520, y=720, classname="nextbutton2", root=self.manageAppointmentsFrame,
            buttonFunction=lambda: [self.manageAppointmentsFrame.grid()], isPlaced=True
        )

    def appointmentList(self):
        prisma = self.prisma
        app = prisma.appointment.find_many(
            where={
                "appRequest": {"is": {"clinic": {"is": {"admin": {"some": {"userId": self.user.id}}}}}}
            },
            include={
                "doctor": {"include": {"user": True}},
                "appRequest": {"include": {"clinic": True, "patient": {"include": {"user": True, "healthRecord": True}}, "appointments": True}},
                "prescription": True,

            }
        )
        h = len(app) * 120
        if h < 420:
            h = 420
        self.viewAppointmentScrolledFrame = ScrolledFrame(
            master=self, width=1500, height=h, autohide=True, bootstyle="minty-bg"
        )
        self.viewAppointmentScrolledFrame.grid_propagate(False)
        self.viewAppointmentScrolledFrame.place(
            x=80, y=260, width=1500, height=420)
        COORDS = (20, 0)
        for appointment in app:
            createdAt = appointment.createdAt
            X = COORDS[0]
            Y = COORDS[1]
            R = self.viewAppointmentScrolledFrame
            FONT = ("Inter", 12)
            self.controller.labelCreator(
                ipath="assets/Appointments/Homepage/AppItemBg.png",
                x=X, y=Y, classname=f"appointmentlist{appointment.id}", root=R,
                isPlaced=True,
            )

            # d = {
            #     "appointmentButton": [
            #         "assets/Dashboard/ClinicAdminAssets/ScrollFrame/view.png",
            #         "assets/Dashboard/ClinicAdminAssets/ScrollFrame/delete.png",
            #     ]
            # }
            # self.viewbutton = self.controller.buttonCreator(
            #     ipath=d["appointmentButton"][0],
            #     x=X+1280, y=Y+30, classname=f"viewbutton{appointment.id}", root=self.viewAppointmentScrolledFrame,
            #     buttonFunction=lambda: [print('view')],
            #     isPlaced=True
            # )
            # self.deletebutton = self.controller.buttonCreator(
            #     ipath=d["appointmentButton"][1],
            #     x=X+1360, y=Y+30, classname=f"deletebutton{appointment.id}", root=self.viewAppointmentScrolledFrame,
            #     buttonFunction=lambda: [print('delete')],
            #     isPlaced=True
            # )
            self.controller.scrolledTextCreator(
                x=X+20, y=Y, width=220, height=100, root=R, classname=f"{appointment.id}_patient_name",
                bg="#f1feff", hasBorder=False,
                text=f"{appointment.appRequest.patient.user.fullName}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            self.controller.scrolledTextCreator(
                x=X+240, y=Y, width=240, height=100, root=R, classname=f"{appointment.id}_doctor_name",
                bg="#f1feff", hasBorder=False,
                text=f"{appointment.doctor.user.fullName}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            KL = timezone("Asia/Kuala_Lumpur")
            # "DD/MM/YYYY HH:MM"
            fmt = "%d/%m/%Y %H:%M"
            startTime = KL.convert(appointment.startTime).strftime(fmt)
            endTime = KL.convert(appointment.endTime).strftime(fmt)
            formatted = f"Start: {startTime}\nEnd: {endTime}"
            self.controller.scrolledTextCreator(
                x=X+480, y=Y, width=240, height=100, root=R, classname=f"{appointment.id}_dateandtime_time",
                bg="#f1feff", hasBorder=False,
                text=formatted, font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            self.controller.scrolledTextCreator(
                x=X+720, y=Y, width=140, height=100, root=R, classname=f"{appointment.id}_doctor_accept",
                bg="#f1feff", hasBorder=False,
                text=f"{appointment.docAccepted}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            self.controller.scrolledTextCreator(
                x=X+860, y=Y, width=140, height=100, root=R, classname=f"{appointment.id}_patient_accept",
                bg="#f1feff", hasBorder=False,
                text=f"{appointment.patientAccepted}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            self.controller.buttonCreator(
                ipath="assets/Appointments/Homepage/ViewAppRequest.png",
                x=X+1040, y=Y+20, classname=f"viewbutton{appointment.id}", root=R,
                buttonFunction=lambda a=appointment.appRequest: [
                    self.controller.threadCreator(
                        target=self.loadViewPatientRequest, appReq=a
                    )
                ],
                isPlaced=True
            )
            self.controller.scrolledTextCreator(
                x=X+1140, y=Y, width=160, height=100, root=R, classname=f"{appointment.id}_status",
                bg="#f1feff", hasBorder=False,
                text=f"{appointment.status}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            COORDS = (
                COORDS[0], COORDS[1] + 120
            )

    def loadViewPatientRequest(self, appReq: AppointmentRequest):
        self.parent.patientRequests = MainPatientRequestsInterface(
            controller=self.controller, parent=self.parent)
        self.parent.patientRequests.loadRoleAssets(clinicAdmin=True)
        self.parent.patientRequests.primarypanel.createManagePatientRequest(
            req=appReq)
