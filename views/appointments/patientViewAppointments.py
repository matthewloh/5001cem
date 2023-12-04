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
        self.createButtons()

    def reloadPage(self):
        self.loadAppRequests()

    def createLabels(self):
        self.controller.labelCreator(
            ipath="assets/Appointments/Patient/BG.png",
            x=0, y=0, classname="appointmentspanelbg", root=self
        )

    def createButtons(self):
        self.reloadPageButton = self.controller.buttonCreator(
            ipath="assets/Appointments/Patient/Refresh.png",
            x=700, y=100, classname="view_apprequest_reload_page", root=self,
            buttonFunction=lambda: [
                self.controller.threadCreator(
                    target=self.reloadPage
                )
            ],
        )

    def loadAppRequests(self):
        prisma = self.prisma
        self.patient = self.parent.primarypanel.patient
        all_requests = prisma.appointmentrequest.find_many(
            where={"patientId": self.patient.id},
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
                },
            },
        )
        height = len(all_requests) * 320
        self.appRequestScrolledFrame = self.controller.scrolledFrameCreator(
            x=20, y=220, width=840, maxheight=height, minheight=780,
            root=self
        )
        COORDS = (20, 20)
        for i, req in list(enumerate(all_requests)):
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
            self.controller.scrolledTextCreator(
                x=X+260, y=Y, width=60, height=40, root=R,
                classname=f"req_number_{req.id}",
                bg="#a8ebee", hasBorder=False,
                text=f"#{i+1}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True,
                hasVbar=False,
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
                buttonFunction=lambda r=req, i=i+1: self.viewApptsPerRequest(
                    r, i),
            )
            self.controller.scrolledTextCreator(
                x=X+735, y=Y+25, width=50, height=50, root=R,
                classname=f"req_appointments_created_{req.id}",
                bg="#86cff5", hasBorder=False,
                text=f"{len(req.appointments)}", font=FONT, fg=WHITE,
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

    def viewApptsPerRequest(self, req: AppointmentRequest, reqIndex: int):
        height = len(req.appointments) * 220
        self.appRequestScrolledFrame = self.controller.scrolledFrameCreator(
            x=880, y=240, width=780, maxheight=height, minheight=400,
            root=self
        )
        COORDS = (20, 0)
        for i, appt in list(enumerate(req.appointments)):
            X = COORDS[0]
            Y = COORDS[1]
            R = self.appRequestScrolledFrame
            FONT = ("Inter", 14)
            BG = "#ffffff"
            DOC = appt.doctor
            start_date = appt.startTime.strftime("%d/%m/%y")
            end_date = appt.endTime.strftime("%d/%m/%y")
            start_time = appt.startTime.strftime("%I:%M%p")
            end_time = appt.endTime.strftime("%I:%M%p")
            disp_date = f"{start_date} - {end_date}"
            disp_time = f"{start_time} - {end_time}"
            self.controller.labelCreator(
                ipath="assets/Appointments/Patient/AppointmentBG.png",
                x=X, y=Y, classname=f"{appt.id}_app_bg", root=R,
                isPlaced=True,
                # buttonFunction=lambda req=req: self.loadSingleAppointment(
                #     req),
            )
            # Appointment Count
            self.controller.scrolledTextCreator(
                x=X+20, y=Y, width=620, height=40, root=R,
                classname=f"appt_count_{appt.id}",
                bg="#bbe6fd", hasBorder=False,
                text=f"Appointment #{i+1} for Request #{reqIndex}", font=("Inter Bold", 15), fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
                hasVbar=False,
            )

            # Date
            self.controller.scrolledTextCreator(
                x=X+80, y=Y+40, width=180, height=60, root=R,
                classname=f"appt_date_{appt.id}",
                bg=BG, hasBorder=True, borderColor=BLACK,
                text=disp_date, font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
                hasVbar=False,
            )
            # Time
            self.controller.scrolledTextCreator(
                x=X+340, y=Y+40, width=180, height=60, root=R,
                classname=f"appt_time_{appt.id}",
                bg=BG, hasBorder=True, borderColor=BLACK,
                text=disp_time, font=("Inter", 12), fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
                hasVbar=False,
            )
            # Doctor Name
            self.controller.scrolledTextCreator(
                x=X+80, y=Y+120, width=180, height=60, root=R,
                classname=f"appt_doctor_{appt.id}\n{DOC.speciality}",
                bg=BG, hasBorder=True, borderColor=BLACK,
                text=DOC.user.fullName, font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
                hasVbar=False,
            )
            # Status Of Appointment
            self.controller.scrolledTextCreator(
                x=X+340, y=Y+120, width=180, height=60, root=R,
                classname=f"appt_status_{appt.id}",
                bg=BG, hasBorder=True, borderColor=BLACK,
                text=appt.status, font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
                hasVbar=False,
            )
            # Go to Prescriptions for this Appointment
            self.controller.buttonCreator(
                ipath="assets/Appointments/Patient/ViewPrescriptions.png",
                x=X+660, y=Y+50, classname=f"{appt.id}_viewprescriptions", root=R,
                isPlaced=True,
                buttonFunction=lambda a=appt: self.viewPrescriptions(a),
            )
            self.controller.scrolledTextCreator(
                x=X+675, y=Y+55, width=50, height=50, root=R,
                classname=f"appt_prescriptions_{appt.id}",
                bg="#ccc3f7", hasBorder=False,
                text=f"{len(appt.prescription)}", font=FONT, fg=WHITE,
                isDisabled=True, isJustified=True,
                hasVbar=False,
            )

            COORDS = (COORDS[0], COORDS[1] + 220)

    def cancelRequest(self, req: AppointmentRequest):
        print(req.id)

    def viewPrescriptions(self, appt: Appointment):
        self.parent.primarypanel.loadViewPatients()
