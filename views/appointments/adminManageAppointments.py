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
            ipath="assets/Appointments/Homepage/AppointmentDashboard.png",
            x=0, y=0, classname="appointmenthomepage", root=self
        )
        self.imgLabels = [
            ("assets/Appointments/Creation/AppointmentCreation.png",
             0, 0, "creationimage", self.createAppointmentsFrame),
            ("assets/Appointments/Management/AppointmentManagement.png",
             0, 0, "manageimage", self.manageAppointmentsFrame)
        ]
        self.controller.settingsUnpacker(self.imgLabels, "label")

    def appointmentButtons(self):
        d = {
            "appointmentButtons": [
                "assets/Appointments/Homepage/CreateAppointments.png",
                "assets/Appointments/Homepage/ManageAppointments.png",
                "assets/Appointments/Creation/ReturnCreationButton.png",
                "assets/Appointments/Creation/ReturnManagementButton.png"
            ]
        }
        self.creationButton = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][0],
            x=60, y=680, classname="createbutton", root=self,
            buttonFunction=lambda: [
                self.createAppointmentsFrame.grid(), self.createAppointmentsFrame.tkraise()],
        )
        self.managementButton = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][1],
            x=600, y=680, classname="managebutton", root=self,
            buttonFunction=lambda: [
                self.manageAppointmentsFrame.grid(), self.manageAppointmentsFrame.tkraise()],
        )
        self.returncreationBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][2],
            x=0, y=40, classname="returncreation", root=self.createAppointmentsFrame,
            buttonFunction=lambda: [self.createAppointmentsFrame.grid_remove()],
        )
        self.returnmanagementBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][3],
            x=40, y=60, classname="returnmanagement", root=self.manageAppointmentsFrame,
            buttonFunction=lambda: [self.manageAppointmentsFrame.grid_remove()],
        )
