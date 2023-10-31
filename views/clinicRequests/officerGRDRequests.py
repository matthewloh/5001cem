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


class OfficerGRDRequests(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="clinicgrdrequests")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.loadClinicsRequests()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath=r"assets/Dashboard/OfficerAssets/OfficerClinicsRequestsBG.png",
            x=0, y=0, classname="grdrequestsbg", root=self
        )

    def loadClinicsRequests(self):
        prisma = self.prisma
        clinicsrequests = prisma.clinicenrolment.find_many(
            where={
                "status":"PENDING"
                },
            include={
                "clinic":True,
                "govRegDocSystem":True
                }   
        )
        h = len(clinicsrequests) * 120
        if h < 600:
            h = 600
        self.exampleScrolledFrame = ScrolledFrame(
            master=self, width=1500, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.exampleScrolledFrame.grid_propagate(False)
        self.exampleScrolledFrame.place(x=80, y=280, width=1500, height=620)
        initialcoordinates = (20, 20)
        for requests in clinicsrequests:
            clinicid = requests.clinicId
            clinicName = requests.clinic.name
            contact = requests.clinic.phoneNum
            opHrs = requests.clinic.clinicHrs

            x = initialcoordinates[0]
            y = initialcoordinates[1]
            self.controller.textElement(
                ipath=r"assets\Dashboard\clinicdetailsbg.png", x=x, y=y,
                classname=f"clinic{clinicid}", root=self.exampleScrolledFrame,
                text=clinicName, size=30, font=INTER,
                isPlaced=True,
            )

            self.controller.textElement(
                ipath=r"assets\Dashboard\clinicdetailsrectangle.png", x=340, y=y+15,
                classname=f"reg_id{clinicid}", root=self.exampleScrolledFrame,
                text=clinicid, size=30, font=INTER,
                isPlaced=True,
            )

            self.controller.textElement(
                ipath=r"assets\Dashboard\clinicdetailsrectangle.png", x=540, y=y+15,
                classname=f"contact{clinicid}", root=self.exampleScrolledFrame,
                text=contact, size=30, font=INTER,
                isPlaced=True,
            )

            self.controller.textElement(
                ipath=r"assets\Dashboard\clinicdetailsrectangle.png", x=780, y=y+15,
                classname=f"opHrs{clinicid}", root=self.exampleScrolledFrame,
                text=opHrs, size=30, font=INTER,
                isPlaced=True,
            )

            self.controller.buttonCreator(
                ipath="assets/Dashboard/OfficerAssets/OfficerAcceptClinic.png",
                classname=f"acceptclinic{clinicid}", root=self.exampleScrolledFrame,
                x=1055, y=y+20, buttonFunction=lambda t = requests: [print(f"acceptclinic {clinicName}")],
                isPlaced=True,
            )
            self.controller.buttonCreator(
                ipath="assets/Dashboard/OfficerAssets/OfficerRejectClinic.png",
                classname=f"rejectclinic{clinicid}", root=self.exampleScrolledFrame,
                x=1055+216, y=y+20, buttonFunction=lambda t = requests: [print(f"rejectclinic {clinicName}")],
                isPlaced=True
            )

            initialcoordinates = (
                initialcoordinates[0], initialcoordinates[1] + 120
            )

