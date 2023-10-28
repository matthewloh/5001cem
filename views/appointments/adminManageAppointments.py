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
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime


class AdminManageAppointments(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="appointmentspanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)

        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.appointmentImgLabels()
        self.appointmentButtons()
        self.creationFrame.grid_remove()
        self.viewFrame.grid_remove()
        self.KL = timezone("Asia/Kuala_Lumpur")
        self.UTC = timezone("UTC")

    def createFrames(self):
        self.timeSlotFrame = self.controller.frameCreator(
            x=0, y=0, classname="timeslotframe", root=self, framewidth=1680, frameheight=1080
        )
        self.manageAppointmentsFrame = self.controller.frameCreator(
            x=0, y=0, classname="manageframe", root=self, framewidth=1680, frameheight=1080
        )
        self.unloadStackedFrames()

    def unloadStackedFrames(self):
        self.timeSlotFrame.grid_remove()
        self.manageAppointmentsFrame.grid_remove()

    def appointmentImgLabels(self):
        self.bg = self.controller.labelCreator(
            ipath="assets/Appointments/Homepage/AppointmentDashboard.png",
            x=0, y=0, classname="appointmenthomepage", root=self
        )
        self.imgLabels = [
            ("assets/Appointments/Creation/TimeSlotBg.png",
             0, 0, "creationimage", self.timeSlotFrame),
            ("assets/Appointments/Management/AppointmentManagement.png",
             0, 0, "manageimage", self.manageAppointmentsFrame)
        ]
        self.controller.settingsUnpacker(self.imgLabels, "label")

    def appointmentButtons(self):
        d = {
            "appointmentButtons": [
                "assets/Appointments/Homepage/Calendar.png",
                "assets/Appointments/Homepage/CreateAppointments.png",
                "assets/Appointments/Homepage/ManageAppointments.png",
                "assets/Appointments/Creation/ReturnCreationButton.png",
                "assets/Appointments/Creation/ReturnManagementButton.png"
            ]
        }
        self.calendarButton = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][0],
            x=60, y=810, classname="calendarbutton", root=self,
            buttonFunction=lambda: [print('calendar')],
        )
        self.creationButton = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][1],
            x=580, y=810, classname="createbutton", root=self,
            buttonFunction=lambda: [
                self.timeSlotFrame.grid(), self.timeSlotFrame.tkraise()],
        )
        self.managementButton = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][2],
            x=1100, y=810, classname="managebutton", root=self,
            buttonFunction=lambda: [
                self.manageAppointmentsFrame.grid(), self.manageAppointmentsFrame.tkraise()],
        )
        self.returncreationBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][3],
            x=40, y=80, classname="returncreation", root=self.timeSlotFrame,
            buttonFunction=lambda: [self.timeSlotFrame.grid_remove()],
        )
        self.returnmanagementBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][4],
            x=40, y=60, classname="returnmanagement", root=self.manageAppointmentsFrame,
            buttonFunction=lambda: [self.manageAppointmentsFrame.grid_remove()],
        )

        self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/ScrollFrame/scrollrefreshbutton.png",
            x=1450, y=130, classname="viewAppointmentrefresh", root=self, 
            buttonFunction=lambda:print("view appointment requests"), isPlaced=True
        )

        exampleList = []
        [exampleList.append("Thing " + str(i))
         for i in range(30) if i % 2 == 0]
        h = len(exampleList) * 120
        if h < 380:
            h = 380
        self.viewAppointmentScrolledFrame = ScrolledFrame(
            master=self, width=1540, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.viewAppointmentScrolledFrame.grid_propagate(False)
        self.viewAppointmentScrolledFrame.place(x=60, y=280, width=1540, height=380)
        initialcoordinates = (20,20)
        for appointment in exampleList:
            x = initialcoordinates[0]
            y = initialcoordinates[1]
            self.controller.textElement(
                ipath=r"assets/Dashboard/ClinicAdminAssets/ScrollFrame/srollbutton.png", x=x, y=y,
                classname=f"appointment{appointment}", root=self.viewAppointmentScrolledFrame,
                text=appointment, size=30, font=INTER,
                isPlaced=True,
            )

            initialcoordinates = (
                initialcoordinates[0], initialcoordinates[1] + 120
            )