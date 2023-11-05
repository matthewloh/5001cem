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
        self.managePatientsClinicFrame = self.controller.frameCreator(
            x=0, y=0, framewidth=1680, frameheight=1080, classname="managepatientsclinicframe", root=self,
            bg="#dee8e0"
        )
        self.managePatientsClinicFrame.grid_remove()

    def createElements(self):
        self.createLabels()
        self.createButtons()

    def createLabels(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/PatientRequestsBg.png",
            x=0, y=0, classname="patientrequests", root=self
        )
        self.controller.labelCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/ManagePatientRequest.png",
            x=0, y=0, classname="managepatientrequest", root=self.managePatientsClinicFrame
        )

    def createButtons(self):
        all_requests = self.controller.buttonCreator(
            x=940, y=140, classname="all_requests", root=self,
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/AllRequests.png",
            buttonFunction=lambda: [self.controller.threadCreator(
                target=self.createPatientList)],
        )
        pending = self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/Pending.png",
            x=1120, y=140, classname="pending_requests", root=self,
            buttonFunction=lambda: [self.controller.threadCreator(
                self.createPatientList, pending=True)],
        )
        accepted = self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/Accepted.png",
            x=1300, y=140, classname="accepted_requests", root=self,
            buttonFunction=lambda: [self.controller.threadCreator(
                self.createPatientList, confirmed=True)],
        )
        rejected = self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/Rejected.png",
            x=1480, y=140, classname="rejected_requests", root=self,
            buttonFunction=lambda: [self.controller.threadCreator(
                self.createPatientList, cancelled=True)],
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
                "clinic": True,
                "appointments": True,
                "approvedBy": {
                    "include": {
                        "user": True
                    }
                }
            }
        )
        # Loading Current Viewed ScrolledText
        text = f"All Patient Requests" if not pending and not confirmed and not cancelled else f"{'Pending' if pending else 'Confirmed' if confirmed else 'Cancelled'} Patient Requests"
        fg = "#f6f2ff" if pending else "#d9fbfb" if confirmed else "#fff1f3" if cancelled else "#ffffff"
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
        KL = timezone("Asia/Kuala_Lumpur")
        fmt = "%A, %d/%m/%Y, %I:%M%p"
        for i, req in list(enumerate(appRequests)):
            patient = req.patient
            created = KL.convert(req.createdAt).strftime(fmt)
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
                text=f"{i}. { patient.user.fullName }\nAdded: {created}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True, justification="center",
                hasVbar=False
            )
            patientHealthRecord = self.controller.buttonCreator(
                ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/HealthRecordButton.png",
                x=X+220, y=Y+20, classname=f"healthrecord{req.id}", root=R,
                buttonFunction=lambda req=req: [
                    self.createManagePatientRequest(req),
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
            buttonFunction=lambda: [self.controller.threadCreator(
                self.acceptAppointment, req=req)],
            isPlaced=True
        )
        self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/RejectRequest.png",
            x=X + 1480, y=Y + 20, classname=f"reject{req.id}", root=R,
            buttonFunction=lambda: [self.controller.threadCreator(
                self.rejectAppointment, req=req)],
            isPlaced=True
        )

    def loadForAcceptOrReject(self, req: AppointmentRequest, X, Y, R):
        IP = "assets/Dashboard/ClinicAdminAssets/PatientRequests/ResetConfirmed.png" if req.reqStatus == "CONFIRMED" else "assets/Dashboard/ClinicAdminAssets/PatientRequests/ResetCancelled.png"
        self.controller.buttonCreator(
            ipath=IP,
            x=X + 1360 if req.reqStatus == "CONFIRMED" else X + 1420,
            y=Y + 20, classname=f"cancel{req.id}", root=R,
            buttonFunction=lambda: [self.controller.threadCreator(
                self.resetAppointment, req=req)],
            isPlaced=True
        )
        if req.reqStatus == "CONFIRMED":
            self.controller.buttonCreator(
                ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/CreateAppointments.png",
                x=X + 1480, y=Y + 20, classname=f"create_appointments{req.id}", root=R,
                buttonFunction=lambda: [self.managePatientRequest(req)],
                isPlaced=True
            )

    def acceptAppointment(self, req: AppointmentRequest):
        prisma = self.prisma
        prisma.appointmentrequest.update(
            where={
                "id": req.id
            },
            data={
                "reqStatus": "CONFIRMED",
                "approvedBy": {
                    "connect": {
                        "id": prisma.clinicadmin.find_first(
                            where={"AND": [{"userId": self.user.id}, {
                                "clinicId": req.clinic.id}]}
                        ).id
                    }
                }
            }
        )
        self.controller.threadCreator(self.createPatientList, confirmed=True)

    def rejectAppointment(self, req: AppointmentRequest):
        prisma = self.prisma
        prisma.appointmentrequest.update(
            where={
                "id": req.id
            },
            data={
                "reqStatus": "CANCELLED",
                "approvedBy": {
                    "connect": {
                        "id": prisma.clinicadmin.find_first(
                            where={
                                "AND": [{"userId": self.user.id}, {"clinicId": req.clinic.id}]
                            }
                        ).id
                    }
                }
            }
        )
        self.controller.threadCreator(self.createPatientList, cancelled=True)

    def resetAppointment(self, req: AppointmentRequest):
        prisma = self.prisma
        prisma.appointmentrequest.update(
            where={
                "id": req.id
            },
            data={
                "reqStatus": "PENDING",
                "approvedBy": {
                    "disconnect": True
                }
            }
        )
        self.controller.threadCreator(self.createPatientList, pending=True)

    def managePatientRequest(self, req: AppointmentRequest):
        self.controller.threadCreator(
            self.createManagePatientRequest, req=req)

    def createManagePatientRequest(self, req: AppointmentRequest):
        self.managePatientsClinicFrame.grid()
        self.managePatientsClinicFrame.tkraise()
        # Patient Name, Gender and Age (DOB)
        age = dt.datetime.now().year - req.patient.user.dateOfBirth.year
        nameGenderAge = f"Patient: {req.patient.user.fullName}\n{req.patient.user.gender}, {age} years old"
        # Blood Type, Height and Weight
        bloodTypeHeightWeight = f"Blood type: {req.patient.healthRecord.bloodType}\nHeight : {req.patient.healthRecord.height} cm & Weight : {req.patient.healthRecord.weight} kg"
        # Past Medical History (Surgeries, Past Medications, Family History)
        PMH = f"Surgeries: {req.patient.healthRecord.pastSurgery}\nPast Medications: {req.patient.healthRecord.pastMedication}\nFamily History: {req.patient.healthRecord.familyHistory}"
        # Current Health Status (Allergies, Current Medications, Current Symptoms, Additional Info)
        CMH = f"Allergies: {req.patient.healthRecord.allergies}\nCurrent Medications: {req.patient.healthRecord.currentMedication}\nCurrent Symptoms: {req.additionalInfo}"
        # Create Text Spaces
        self.controller.scrolledTextCreator(
            x=260, y=260, width=540, height=60, root=self.managePatientsClinicFrame, classname="manage_req_patientname_gender_age",
            bg=WHITE, hasBorder=BLACK,
            text=f"{nameGenderAge}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )
        self.controller.scrolledTextCreator(
            x=260, y=360, width=540, height=60, root=self.managePatientsClinicFrame, classname="manage_req_bloodtype_height_weight",
            bg=WHITE, hasBorder=BLACK,
            text=bloodTypeHeightWeight, font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )
        self.controller.scrolledTextCreator(
            x=40, y=500, width=760, height=160, root=self.managePatientsClinicFrame, classname="manage_req_PMH",
            bg=WHITE, hasBorder=BLACK,
            text=PMH, font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
        )
        self.controller.scrolledTextCreator(
            x=40, y=740, width=760, height=160, root=self.managePatientsClinicFrame, classname="manage_req_CMH",
            bg=WHITE, hasBorder=BLACK,
            text=CMH, font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
        )

        # Request Information
        # Appointment Preferences of Patient
        KL = timezone("Asia/Kuala_Lumpur")
        createdAt = KL.convert(req.createdAt).strftime("%A, %d/%m/%Y, %I:%M%p")
        appPreferences = f"Preferred Date: {req.preferredDate}\nPreferred Time: {req.preferredTime}\nSpeciality Wanted: {req.specialityWanted}"
        numOfAppointments = len(req.appointments)
        requestInfoHistory = f"Request Status: {req.reqStatus}\nRequest Date: {createdAt}\nNumber of Appointments: {numOfAppointments}\nMost recent approval by: {req.approvedBy.user.fullName if req.approvedBy else 'None'}"
        self.controller.scrolledTextCreator(
            x=880, y=260, width=760, height=160, root=self.managePatientsClinicFrame, classname="manage_req_appointment_preferences",
            bg=WHITE, hasBorder=BLACK,
            text=f"{appPreferences}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
        )
        self.controller.scrolledTextCreator(
            x=880, y=500, width=760, height=160, root=self.managePatientsClinicFrame, classname="manage_req_request_info_history",
            bg=WHITE, hasBorder=BLACK,
            text=requestInfoHistory, font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
        )
        self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/Back.png",
            x=20, y=40, classname="manage_req_back", root=self.managePatientsClinicFrame,
            buttonFunction=lambda: [
                self.managePatientsClinicFrame.grid_remove()],
        )
        if req.reqStatus == "CONFIRMED":
            self.controller.buttonCreator(
                ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/CreateAnAppointment.png",
                x=880, y=760, classname="manage_req_create_appointment", root=self.managePatientsClinicFrame,
                buttonFunction=lambda: [self.controller.threadCreator(
                    self.createAppointment, req=req)],
            )
        elif req.reqStatus == "CANCELLED":
            # Delete Request
            self.controller.buttonCreator(
                ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/DeleteRequest.png",
                x=880, y=760, classname="manage_req_delete_request", root=self.managePatientsClinicFrame,
                buttonFunction=lambda: [self.controller.threadCreator(
                    self.deleteRequest, req=req)],
            )
            try:
                for widgetname, widget in self.managePatientsClinicFrame.children.items():
                    if "manage_req_create_appointment" in widgetname:
                        widget.grid_remove()
            except AttributeError:
                pass
        self.manageAppointments = self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/PatientRequests/ManageAppointmentsRequest.png",
            x=880, y=860, classname="manage_req_manage_appointments", root=self.managePatientsClinicFrame,
            buttonFunction=lambda: [self.controller.threadCreator(
                self.manageAppointment, req=req)],
        ) if req.reqStatus == "CONFIRMED" else None

    def createAppointment(self, req: AppointmentRequest):
        pass
    
    def manageAppointment(self, req: AppointmentRequest):
        pass

    def deleteRequest(self, req: AppointmentRequest):
        result = messagebox.askyesno(
            "Delete Request", "Are you sure you want to delete this request?",
        )
        if result:
            prisma = self.prisma
            prisma.appointmentrequest.delete(where={
                "id": req.id
            })
            self.controller.threadCreator(
                self.createPatientList, cancelled=True)
        else:
            return
