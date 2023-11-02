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


class AdminBrowseClinic(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="browseclinicpanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.manageClinic()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/ManageClinic/ManageClinicBg.png",
            x=0, y=0, classname="secondarypanelbg", root=self
        )

        self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/ScrollFrame/scrollrefreshbutton.png",
            x=1385, y=135, classname="manageclinicrefresh", root=self, 
            buttonFunction=lambda:print("manage clinic requests"), isPlaced=True
        )

    def manageClinic(self):
        prisma = self.prisma
        clinics = prisma.clinic.find_many(
            include={
                "name": True,
            }
        )
        h = len(clinics) * 120
        if h < 640:
            h = 640
        self.manageClinicScrolledFrame = ScrolledFrame(
            master=self, width=1540, height=h, autohide=True, bootstyle="minty-bg"
        )
        self.manageClinicScrolledFrame.grid_propagate(False)
        self.manageClinicScrolledFrame.place(x=60, y=280, width=1540, height=640)
        COORDS = (20,20)
        for clinic in clinics:
            clinic.name
            X = COORDS[0]
            Y = COORDS[1]
            R = self.manageClinicScrolledFrame
            FONT = ("Inter", 12)
            self.controller.labelCreator(
                ipath=r"assets/Dashboard/ClinicAdminAssets/ScrollFrame/scrollbutton.png", 
                x=X, y=Y, classname=f"manageClinic{clinic.id}", root=R,
                isPlaced=True,
            )   
        
            d = {
                "clinicButton": [
                    "assets/Dashboard/ClinicAdminAssets/ScrollFrame/view.png",
                    "assets/Dashboard/ClinicAdminAssets/ScrollFrame/delete.png",
                ]
            }
            self.viewClinicbutton = self.controller.buttonCreator(
                ipath=d["clinicButton"][0],
                x=X+1280, y=Y+30, classname=f"viewclinic{clinic.id}", root=R,
                buttonFunction=lambda: [print('clinicview')],
                isPlaced=True
            )
            self.deleteClinicbutton = self.controller.buttonCreator(
                ipath=d["clinicButton"][1],
                x=X+1360, y=Y+30, classname=f"deleteclinic{clinic.id}", root=R,
                buttonFunction=lambda: [print('clinicdelete')],
                isPlaced=True
            )
            clinicName = self.controller.scrolledTextCreator(
                x = X+50, y=Y+30, width=200, height=60, root=R, classname = f"{clinic.id}_name",
                bg="#f1feff", hasBorder=False,
                text=clinic.name, font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            COORDS = (
                COORDS[0], COORDS[1] + 120
            )