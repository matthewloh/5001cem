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
        self.patientImgLabels()
        self.createPatientList()

    def createFrames(self):
        pass

    def patientImgLabels(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/PatientRequestsBg.png",
            x=0, y=0, classname="patientrequests", root=self
        )

        exampleList = []
        [exampleList.append("Thing " + str(i))
         for i in range(30) if i % 2 == 0]
        h = len(exampleList) * 120
        if h < 280:
            h = 280
        self.viewAppointmentScrolledFrame = ScrolledFrame(
            master=self, width=1500, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.viewAppointmentScrolledFrame.grid_propagate(False)
        self.viewAppointmentScrolledFrame.place(
            x=60, y=240, width=1540, height=290)
        initialcoordinates = (20, 20)
        for request in exampleList:
            X = initialcoordinates[0]
            Y = initialcoordinates[1]
            self.controller.textElement(
                ipath=r"assets/Dashboard/ClinicAdminAssets/ScrollFrame/scrollbutton.png", x=X, y=Y,
                classname=f"request{request}", root=self.viewAppointmentScrolledFrame,
                text=request, size=30, font=INTER,
                isPlaced=True,
            )

        d = {
            "requestButton": [
                "assets/Dashboard/ClinicAdminAssets/ScrollFrame/accept.png",
                "assets/Dashboard/ClinicAdminAssets/ScrollFrame/reject.png",
            ]
        }
        self.acceptbutton = self.controller.buttonCreator(
            ipath=d["requestButton"][0],
            x=X+1060, y=Y+30, classname=f"acceptbutton{request}", root=self.viewAppointmentScrolledFrame,
            buttonFunction=lambda: [print('accept')],
            isPlaced=True
        )
        self.rejectbutton = self.controller.buttonCreator(
            ipath=d["requestButton"][1],
            x=X+1260, y=Y+30, classname=f"rejectbutton{request}", root=self.viewAppointmentScrolledFrame,
            buttonFunction=lambda: [print('reject')],
            isPlaced=True
        )

        initialcoordinates = (
            initialcoordinates[0], initialcoordinates[1] + 120
        )

    def createPatientList(self):
        prisma = self.prisma
        appRequests = prisma.appointmentrequest.find_many(
            where={
                "clinic": {
                    "is": {
                        "admin": {
                            "some": {
                                "userId": self.user.id
                            }
                        }
                    }
                }
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
        h = len(appRequests) * 140
        if h < 400:
            h = 400
        self.patientRequestScrolledFrame = ScrolledFrame(
            master=self, width=1640, height=h, autohide=True, bootstyle="bg-rounded"
        )
        self.patientRequestScrolledFrame.place(
            x=20, y=140, width=1640, height=400)
        COORDS = (20, 0)
        for req in appRequests:
            patient = req.patient
            X = COORDS[0]
            Y = COORDS[1]
            R = self.patientRequestScrolledFrame
            FONT = ("Inter", 12)
            self.controller.labelCreator(
                ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/SinglePatientRequestBG.png",
                x=X, y=Y, classname=f"patientlist{patient.id}", root=R,
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
                x=X+220, y=Y+20, classname=f"healthrecord{patient.id}", root=R,
                buttonFunction=lambda hr=patient.healthRecord: [
                    print(hr)
                    # self.loadHealthRecord(hr)
                ],
                isPlaced=True
            )
            remainingCoords = (360, 20)
            formattedTime = f"Date: {req.preferredDate}\nTime: {req.preferredTime}"
            formattedInfo = f"Speciality: {req.specialityWanted}\nAdditional Info: {req.additionalInfo}"
            for i, t in enumerate([req.location, formattedTime, formattedInfo]):
                REMX = remainingCoords[0]
                REMY = remainingCoords[1]
                self.controller.scrolledTextCreator(
                    x=REMX, y=REMY, width=280 if i != 2 else 340,
                    height=80, root=R, classname=f"{patient.id}_text{i}",
                    bg="#f1feff", hasBorder=False,
                    text=t, font=FONT, fg=BLACK,
                    isDisabled=True, isJustified=True, justification="center",
                    hasVbar=False
                )
                remainingCoords = (
                    remainingCoords[0] + 320, remainingCoords[1]
                )
            self.controller.buttonCreator(
                ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/AcceptRequest.png",
                x=1380, y=Y+20, classname=f"accept{patient.id}", root=R,
                buttonFunction=lambda: [self.acceptAppointment(req)],
                isPlaced=True
            )
            self.controller.buttonCreator(
                ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/RejectRequest.png",
                x=1500, y=Y+20, classname=f"reject{patient.id}", root=R,
                buttonFunction=lambda: [self.rejectAppointment(req)],
                isPlaced=True
            )
            COORDS = (
                COORDS[0], COORDS[1] + 140
            )
