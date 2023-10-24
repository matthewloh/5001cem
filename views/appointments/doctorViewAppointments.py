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


class DoctorViewAppointments(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="appointmentspanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)

        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Appointments/Doctor/BG.png",
            x=0, y=0, classname="appointmentspanelbg", root=self
        )
        self.loadAppScrolledFrame()

    def loadAppScrolledFrame(self):
        prisma = self.prisma
        # appointments = prisma.appointment.find_many(
        #     where={
        #         "doctor": {
        #             "is": {
        #                 "userId": self.getUserID()
        #             }
        #         }
        #     },
        #     include={
        #         "patient": {
        #             "include": {
        #                 "user": True
        #             }
        #         }
        #     }
        # )
        appointments = [1, 2, 3, 4, 5, 6, 7]
        h = len(appointments) * 120
        if h < 620:
            h = 620
        self.appointmentScrolledFrame = ScrolledFrame(
            master=self, width=1500, height=h, bootstyle="bg-round", autohide=True
        )
        self.appointmentScrolledFrame.place(
            x=80, y=320, width=1500, height=620)
        initCoords = (20, 20)
        for a in appointments:
            bg = self.controller.labelCreator(
                ipath="assets/Appointments/Doctor/SingleAppBG.png",
                x=initCoords[0], y=initCoords[1], classname=f"appointmentbg{a}", root=self.appointmentScrolledFrame,
                isPlaced=True
            )
            initCoords = (initCoords[0], initCoords[1] + 120)
