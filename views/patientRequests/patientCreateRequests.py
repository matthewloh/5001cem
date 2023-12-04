from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.mainDashboard import Dashboard
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
from prisma.models import Appointment, Prescription
from PIL import Image, ImageOps, ImageTk


class PatientCreateRequests(Frame):
    def __init__(self, parent: Dashboard = None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="requestspanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.prisma = self.controller.mainPrisma
        self.user = self.parent.user
        self.createFrames()
        self.createElements()
        self.loadAppointments()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/PatientAssets/PatientRequestPrescription.png",
            x=0, y=0, classname="requestspanelbg", root=self
        )
        self.createButtons()

    def createButtons(self):
        self.controller.buttonCreator(
            ipath="assets/Prescriptions/Patient/PrevApp.png",
            x=740, y=100, classname="patient_prev_app", root=self,
            buttonFunction=lambda: self.loadPrevAppointments()
        )
        self.controller.buttonCreator(
            ipath="assets/Prescriptions/Patient/NextApp.png",
            x=800, y=100, classname="patient_next_app", root=self,
            buttonFunction=lambda: self.loadNextAppointments()
        )

    def loadAppointments(self):
        prisma = self.prisma

        self.appointments = prisma.appointment.find_many(
            where={
                "appRequest": {
                    "is": {
                        "patient": {
                            "is": {
                                "userId": self.user.id
                            }
                        }
                    }
                }
            },
            include={
                "appRequest": {
                    "include": {
                        "clinic": True,
                    }
                },
                "prescription": True,
                "doctor": {
                    "include": {
                        "user": True,
                    }
                },
            }
        )
        self.current_app = 0
        if len(self.appointments) > 0:
            self.render_appointment(self.appointments[0])

    def loadPrevAppointments(self):
        index = (self.current_app - 1) % len(self.appointments)
        self.current_app = index
        self.render_appointment(self.appointments[index])

    def loadNextAppointments(self):
        index = (self.current_app + 1) % len(self.appointments)
        self.current_app = index
        self.render_appointment(self.appointments[index])

    def render_appointment(self, appt: Appointment):
        R = self
        IMGKEY = f"app_clinic_image"
        FONT = ("Inter", 14)
        BG = "#ffffff"
        DOC = appt.doctor
        start_date = appt.startTime.strftime("%d/%m/%y")
        end_date = appt.endTime.strftime("%d/%m/%y")
        start_time = appt.startTime.strftime("%I:%M%p")
        end_time = appt.endTime.strftime("%I:%M%p")
        disp_date = f"{start_date} - {end_date}"
        disp_time = f"{start_time} - {end_time}"
        img = self.controller.decodingBase64Data(
            appt.appRequest.clinic.clinicImg)
        img = ImageOps.contain(img, (200, 200), Image.Resampling.BICUBIC)
        self.clinicImage = self.controller.buttonCreator(
            x=60, y=100, classname=IMGKEY, root=R,
            ipath="assets/BrowseClinic/Patient/BrowseSingleClinic/ClinicImagePlaceholder.png",
            bg="#ffffff",
            isPlaced=True,
        )
        self.controller.imageDict[IMGKEY] = ImageTk.PhotoImage(
            img
        )
        newImage = self.controller.imageDict[IMGKEY]
        self.clinicImage.configure(image=newImage, width=200, height=200)
        self.clinicImage.place(x=60, y=100, width=200, height=200)
        # self.controller.scrolledTextCreator(
        #     x=100, y=320, width=160, height=80, root=R,
        #     text=f"{appt.location}"
        # )
        self.controller.scrolledTextCreator(
            x=360, y=120, width=360, height=60, root=R,
            classname="view_app_appt_date",
            bg=BG, hasBorder=True, borderColor=BLACK,
            text=disp_date, font=FONT, fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False,
        )
        self.controller.scrolledTextCreator(
            x=360, y=200, width=360, height=60, root=R,
            classname="view_app_appt_time",
            bg=BG, hasBorder=True, borderColor=BLACK,
            text=disp_time, font=FONT, fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False,
        )
        # Doctor Name
        self.controller.scrolledTextCreator(
            x=360, y=280, width=160, height=80, root=R,
            classname=f"appt_doctor_{appt.id}\n{DOC.speciality}",
            bg=BG, hasBorder=True, borderColor=BLACK,
            text=DOC.user.fullName, font=FONT, fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False,
        )
        # Status Of Appointment
        self.controller.scrolledTextCreator(
            x=620, y=280, width=160, height=80, root=R,
            classname=f"appt_status_{appt.id}",
            bg=BG, hasBorder=True, borderColor=BLACK,
            text=appt.status, font=FONT, fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False,
        )

        self.load_scrolled_frame_prescriptions(appt)

    def load_scrolled_frame_prescriptions(self, appt: Appointment):
        toast = ToastNotification(
            title="Alert",
            message=f"No Prescriptions Found for this Appointment",
            duration=5000,
            bootstyle=WARNING
        )
        if len(appt.prescription) == 0:
            toast.show_toast()
        height = len(appt.prescription) * 220
        R = self
        self.appRequestScrolledFrame = self.controller.scrolledFrameCreator(
            x=20, y=560, width=840, maxheight=height, minheight=480,
            root=self
        )
        COORDS = (20, 0)
        for i, prescription in list(enumerate(appt.prescription)):
            self.render_prescription(prescription, COORDS, i)
            COORDS = (COORDS[0], COORDS[1] + 220)

    def render_prescription(self, prescription: Prescription, COORDS: tuple, i: int):
        R = self.appRequestScrolledFrame
        X = COORDS[0]
        Y = COORDS[1]
        self.controller.labelCreator(
            ipath="assets/Prescriptions/Patient/PrescriptionBG.png",
            x=X, y=Y, classname=f"{prescription.id}_requestbg", root=R,
            isPlaced=True,
            # buttonFunction=lambda req=req: self.loadSingleAppointment(
            #     req),
        )

        
