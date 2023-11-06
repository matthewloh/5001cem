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


class AdminGRDRequest(Frame):
    def __init__(self, parent: ClinicAdminDashboard = None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="clinicgrdrequests")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.user = self.parent.user
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.loadClinicRequestStatus()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath=r"assets/Dashboard/ClinicAdminAssets/AdminViewGRDStatusBG.png",
            x=0, y=0, classname="grdrequestsbg", root=self
        )

        

        self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/adminrefreshbtn.png",
            x=680+440, y=351+84, classname="grdrequestsrefresh", root=self, 
            buttonFunction=lambda:print("refresh grd requests"), isPlaced=True
        )

        

    def loadClinicRequestStatus(self):
        prisma = self.prisma
        self.clinicstatusdetails = prisma.clinicenrolment.find_first(
            where={
                "clinicId": self.user.clinicAdmin[0].clinicId,
            },
            include={
                "govRegDocSystem": True,
                 "clinic": True,
            },    
        )

        clinicName = self.clinicstatusdetails.clinic.name
        createdAt = datetime.strptime(str(self.clinicstatusdetails.createdAt)[:19], '%Y-%m-%d %H:%M:%S')
        updatedAt = datetime.strptime(str(self.clinicstatusdetails.updatedAt)[:19], '%Y-%m-%d %H:%M:%S')
        status = self.clinicstatusdetails.status

        self.controller.textElement(
            ipath="assets/Dashboard/ClinicAdminAssets/clinicstatusfields.png",
            x=240+440, y=351+84, classname="grdstatusclinicname", root=self,
            text=clinicName, size=22, font=INTER,
            isPlaced=True
        )

        self.controller.textElement(
            ipath="assets/Dashboard/ClinicAdminAssets/clinicstatusfields.png",
            x=240+440, y=451+84, classname="grdstatuscreatedat", root=self,
            text=str(createdAt), size=22, font=INTER,
            isPlaced=True
        )

        self.controller.textElement(
            ipath="assets/Dashboard/ClinicAdminAssets/clinicstatusfields.png",
            x=240+440, y=551+84, classname="grdstatusupdatedat", root=self,
            text=str(updatedAt), size=22, font=INTER,
            isPlaced=True
        )

        self.controller.textElement(
            ipath="assets/Dashboard/ClinicAdminAssets/clinicstatusfields.png",
            x=240+440, y=651+84, classname="grdstatustext", root=self,
            text=status, size=22, font=INTER,
            isPlaced=True
        )

        if status == "APPROVED":
            statusimg = "assets/Dashboard/ClinicAdminAssets/clinicaccepted.png"
            statustext="Request approved"
            statusdes="Your GRD request has been approved.\nYou can now add doctors to your clinic."

        elif status == "REJECTED":
            statusimg="assets\Dashboard\ClinicAdminAssets\clinicrejected.png"
            statustext="Request rejected"
            statusdes="Your GRD request has been rejected.\nPlease contact the GRD for more info."

        else: 
            statusimg="assets\Dashboard\ClinicAdminAssets\clinicpending.png"
            statustext="Request pending"
            statusdes="Your GRD request is still pending. Check\nback again later for updates."

        self.grdrequeststatus = self.controller.labelCreator(
            ipath=statusimg,
            x=350+440, y=77+84, classname="grdrequeststatus", root=self, isPlaced=True
        )

        self.grdstatustext = self.controller.textElement(
            ipath="assets/Dashboard/ClinicAdminAssets/requeststatustextbg.png",
            x=290+440, y=177+84, classname="grdstatus",text=statustext, 
            size=24, font=INTERBOLD,
            root=self, isPlaced=True,
            xoffset=-0.5
        )

        self.grdstatusdesc = self.controller.textElement(
            ipath="assets/Dashboard/ClinicAdminAssets/requeststatusdesc.png",
            x=182+440, y=220+84, classname="grdstatusdesc",
            text=statusdes,
            size=22, font=INTER,
            root=self, isPlaced=True,
            yIndex=-1
        )
