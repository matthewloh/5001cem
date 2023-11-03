from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.dashboard.adminDashboard import ClinicAdminDashboard
from abc import ABC, abstractmethod
import calendar
import re
import threading
from tkinter import *
from tkinter import messagebox
from prisma.models import AppointmentRequest
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


class AdminManagePatientRequests(Frame):
    def __init__(self, parent: ClinicAdminDashboard = None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="requestspanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.user = self.parent.user
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.createPatientList()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/PatientRequestsBg.png",
            x=0, y=0, classname="patientrequests", root=self
        )
        self.createButtons()

    def createButtons(self):
        all_requests = self.controller.buttonCreator(
            x=940, y=140, classname="all_requests", root=self,
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/AllRequests.png",
            buttonFunction=lambda: [self.createPatientList()],
        )
        pending = self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/Pending.png",
            x=1120, y=140, classname="pending_requests", root=self,
            buttonFunction=lambda: [self.createPatientList(pending=True)],
        )
        accepted = self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/Accepted.png",
            x=1300, y=140, classname="accepted_requests", root=self,
            buttonFunction=lambda: [self.createPatientList(confirmed=True)],
        )
        rejected = self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/Rejected.png",
            x=1480, y=140, classname="rejected_requests", root=self,
            buttonFunction=lambda: [self.createPatientList(cancelled=True)],
        )

    def createPatientList(self, pending=False, confirmed=False, cancelled=False):
        prisma = self.prisma
        appRequests = prisma.appointmentrequest.find_many(
            where={
                "clinic": {"is": {"admin": {"some": {"userId": self.user.id}}}},
                "reqStatus": "PENDING"
            } if pending else {
                "clinic": {"is": {"admin": {"some": {"userId": self.user.id}}}},
                "reqStatus": "CONFIRMED"
            } if confirmed else {
                "clinic": {"is": {"admin": {"some": {"userId": self.user.id}}}},
                "reqStatus": "CANCELLED"
            } if cancelled else {
                "clinic": {"is": {"admin": {"some": {"userId": self.user.id}}}},
            },
            include={
                "patient": {
                    "include": {
                        "healthRecord": True,
                        "user": True
                    }
                },
                "clinic": True
            }
        )
        # Loading Current Viewed ScrolledText
        text = f"All Patient Requests" if not pending and not confirmed and not cancelled else f"{'Pending' if pending else 'Confirmed' if confirmed else 'Cancelled'} Patient Requests"
        fg = "#f6f2ff" if pending else "#d9fbfb" if confirmed else "#fff1f3" if cancelled else "#e6daff"
        self.controller.scrolledTextCreator(
            x=40, y=146, width=880, height=60, root=self, classname="patientrequesttext",
            bg="#ffbc5b", hasBorder=False,
            text=text, font=("Inter Bold", 32), fg=fg,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )
        h = len(appRequests) * 140
        if h < 760:
            h = 760
        self.patientRequestScrolledFrame = ScrolledFrame(
            master=self, width=1640, height=h, autohide=True, bootstyle="bg-rounded"
        )
        self.patientRequestScrolledFrame.place(
            x=20, y=280, width=1640, height=760)
        COORDS = (20, 0)
        for req in appRequests:
            patient = req.patient
            X = COORDS[0]
            Y = COORDS[1]
            R = self.patientRequestScrolledFrame
            FONT = ("Inter", 12)
            self.controller.labelCreator(
                ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/SinglePatientRequestBG.png",
                x=X, y=Y, classname=f"patientlist{req.id}", root=R,
                isPlaced=True,
            )
            patientName = self.controller.scrolledTextCreator(
                x=X+20, y=Y+20, width=180, height=80, root=R, classname=f"{patient.id}_name",
                bg="#f1feff", hasBorder=False,
                text=patient.user.fullName, font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True, justification="center",
                hasVbar=False
            )
            patientHealthRecord = self.controller.buttonCreator(
                ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/HealthRecordButton.png",
                x=X+220, y=Y+20, classname=f"healthrecord{req.id}", root=R,
                buttonFunction=lambda hr=patient.healthRecord: [
                    print(hr)
                    # self.loadHealthRecord(hr)
                ],
                isPlaced=True
            )
            formattedTime = f"Date: {req.preferredDate}\nTime: {req.preferredTime}"
            formattedInfo = f"Speciality: {req.specialityWanted}\nAdditional Info: {req.additionalInfo}"
            for i, t in enumerate([req.location, formattedTime, formattedInfo]):
                self.controller.scrolledTextCreator(
                    x=X+360 + 300 * i, y=Y + 20, width=280 if i != 2 else 360,
                    height=80, root=R, classname=f"{patient.id}_text{i}",
                    bg="#f1feff", hasBorder=False,
                    text=t, font=FONT, fg=BLACK,
                    isDisabled=True, isJustified=True, justification="center",
                    hasVbar=False
                )
            self.loadForPending(req, X, Y, R) if req.reqStatus == "PENDING" else self.loadForAcceptOrReject(
                req, X, Y, R)
            COORDS = (
                COORDS[0], COORDS[1] + 140
            )

    def loadForPending(self, req: AppointmentRequest, X, Y, R):
        self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/AcceptRequest.png",
            x=X + 1360, y=Y + 20, classname=f"accept{req.id}", root=R,
            buttonFunction=lambda: [self.acceptAppointment(req)],
            isPlaced=True
        )
        self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/RejectRequest.png",
            x=X + 1480, y=Y + 20, classname=f"reject{req.id}", root=R,
            buttonFunction=lambda: [self.rejectAppointment(req)],
            isPlaced=True
        )

    def loadForAcceptOrReject(self, req: AppointmentRequest, X, Y, R):
        IP = "assets/Dashboard/ClinicAdminAssets/PatientRequests/ResetConfirmed.png" if req.reqStatus == "CONFIRMED" else "assets/Dashboard/ClinicAdminAssets/PatientRequests/ResetCancelled.png"
        self.controller.buttonCreator(
            ipath=IP,
            x=X + 1420, y=Y + 20, classname=f"cancel{req.id}", root=R,
            buttonFunction=lambda: [self.cancelAppointment(req)],
            isPlaced=True
        )

    def acceptAppointment(self, req: AppointmentRequest):
        prisma = self.prisma
        prisma.appointmentrequest.update(
            where={
                "id": req.id
            },
            data={
                "reqStatus": "CONFIRMED"
            }
        )
        self.createPatientList(confirmed=True)

    def rejectAppointment(self, req: AppointmentRequest):
        prisma = self.prisma
        prisma.appointmentrequest.update(
            where={
                "id": req.id
            },
            data={
                "reqStatus": "CANCELLED"
            }
        )
        self.createPatientList(cancelled=True)

    def cancelAppointment(self, req: AppointmentRequest):
        prisma = self.prisma
        prisma.appointmentrequest.update(
            where={
                "id": req.id
            },
            data={
                "reqStatus": "PENDING"
            }
        )
        self.createPatientList(pending=True)
