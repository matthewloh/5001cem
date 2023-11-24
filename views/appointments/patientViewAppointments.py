from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.mainDashboard import Dashboard
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
from PIL import Image, ImageOps, ImageTk


class PatientViewAppointments(Frame):
    def __init__(self, parent: Dashboard = None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="appointmentspanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.user = self.parent.user
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()

    def createFrames(self):
        pass

    def createElements(self):
        self.createLabels()

    def createLabels(self):
        self.controller.labelCreator(
            ipath="assets/Appointments/Patient/BG.png",
            x=0, y=0, classname="appointmentspanelbg", root=self
        )

    def loadAppRequests(self):
        self.patient = self.parent.primarypanel.patient
        height = len(self.patient.madeAppRequests) * 320
        self.appRequestScrolledFrame = self.controller.scrolledFrameCreator(
            x=20, y=220, width=840, maxheight=height, minheight=780,
            root=self
        )
        COORDS = (20, 20)
        for req in self.patient.madeAppRequests:
            X = COORDS[0]
            Y = COORDS[1]
            R = self.appRequestScrolledFrame
            FONT = ("Inter", 14)
            BG = "#ffffff"
            clinic = req.clinic
            self.controller.labelCreator(
                ipath="assets/Appointments/Patient/RequestBG.png",
                x=X, y=Y, classname=f"{req.id}_requestbg", root=R,
                isPlaced=True,
                # buttonFunction=lambda req=req: self.loadSingleAppointment(
                #     req),
            )
            img = self.controller.decodingBase64Data(req.clinic.clinicImg)
            img = ImageOps.contain(img, (200, 200), Image.Resampling.BICUBIC)
            self.clinicImage = self.controller.buttonCreator(
                x=X+40, y=Y+20, classname=f"req_loadedclinic_image_{req.id}", root=R,
                ipath="assets/BrowseClinic/Patient/BrowseSingleClinic/ClinicImagePlaceholder.png",
                bg="#ffffff",
                isPlaced=True,
            )
            self.controller.imageDict[f"req_loadedclinic_image_{req.id}"] = ImageTk.PhotoImage(
                img
            )
            newImage = self.controller.imageDict[f"req_loadedclinic_image_{req.id}"]
            self.clinicImage.configure(image=newImage, width=200, height=200)
            self.clinicImage.place(x=X+40, y=Y+20, width=200, height=200)
            self.controller.scrolledTextCreator(
                x=X+100, y=Y+230, width=140, height=60, root=R,
                classname=f"req_loadedclinic_name_{req.id}",
                bg=BG, hasBorder=False,
                text=clinic.name, font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True,
                hasVbar=False,
            )
            # Preferred Date
            self.controller.scrolledTextCreator(
                x=X+340, y=Y+20, width=360, height=40, root=R,
                classname=f"req_preferred_date_{req.id}",
                bg=BG, hasBorder=False,
                text=f"{req.preferredDate}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
                hasVbar=False,
            )
            # Preffered Time
            self.controller.scrolledTextCreator(
                x=X+340, y=Y+80, width=360, height=40, root=R,
                classname=f"req_preferred_time_{req.id}",
                bg=BG, hasBorder=False,
                text=f"{req.preferredTime}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
                hasVbar=False,
            )
            # Speciality Wanted & Additional Info
            self.controller.scrolledTextCreator(
                x=X+340, y=Y+140, width=160, height=80, root=R,
                classname=f"req_speciality_{req.id}",
                bg=BG, hasBorder=False,
                text=f"{req.specialityWanted}\n{req.additionalInfo}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
                hasVbar=False,
            )
            # Request Status
            self.controller.scrolledTextCreator(
                x=X+600, y=Y+140, width=100, height=80, root=R,
                classname=f"req_status_{req.id}",
                bg=BG, hasBorder=False,
                text=f"{req.reqStatus}", font=("Inter", 10), fg=BLACK,
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
                x=X+360, y=Y+250, width=340, height=40, root=R,
                classname=f"req_created_ago_{req.id}",
                bg=BG, hasBorder=False,
                text=diffText, font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True,
                hasVbar=False,
            )
            self.controller.buttonCreator(
                ipath="assets/Appointments/Patient/ViewAppointments.png",
                x=X+720, y=Y+20, classname=f"{req.id}_viewappointments", root=R,
                isPlaced=True,
                buttonFunction=lambda r=req: self.loadSingleAppointment(r),
            )
            self.controller.scrolledTextCreator(
                x=X+735, y=Y+25, width=50, height=50, root=R,
                classname=f"req_appointments_created_{req.id}",
                bg=BG, hasBorder=False,
                text=f"{len(req.appointments)}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True,
                hasVbar=False,
            )
            self.controller.buttonCreator(
                ipath="assets/Appointments/Patient/Delete.png",
                x=X+720, y=Y+180, classname=f"{req.id}_cancelrequest", root=R,
                isPlaced=True,
                buttonFunction=lambda r=req: self.cancelRequest(r),
            )
            COORDS = (COORDS[0], COORDS[1] + 320)

    def loadSingleAppointment(self, req: AppointmentRequest):
        print(req.id)

    def cancelRequest(self, req: AppointmentRequest):
        print(req.id)