from abc import ABC, abstractmethod
import calendar
import re
import threading
from tkinter import *
from tkinter import ttk
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


class PatientBrowseClinic(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="browseclinicpanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.createFormEntries()
        self.createbutton()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/PatientAssets/BrowserClinic.png",
            x=0, y=0, classname="secondarypanelbg", root=self
        )

        self.clinicsMap = tkintermapview.TkinterMapView(
            self,  width=860, height=640)
        self.clinicsMap.place(x=0, y=180)
        self.clinicsMap.set_address("Penang, Malaysia")
        self.clinicsMap.set_tile_server(
            "https://mt0.google.com/vt/lyrs=m&hl=en&x ={x}&y={y}&z={z}&s=Ga", max_zoom=22) 
        
    def createFormEntries(self):
        CREATOR = self.controller.ttkEntryCreator
        FONT = ("Arial", 24)

        self.patientBrowserSelectAddress = CREATOR(
            x=0, y=80, width=780, height=80,
            root=self, classname="Patient_Browse_Clinic1",
            font=FONT, isPlaced=True
        )

        # Add a placeholder/hint text
        self.patientBrowserSelectAddress.insert(0, "Enter your address here")
       

        self.patientBrowserSearchClinic = CREATOR(
            x=1494, y=195, width=158, height=75,
            root=self, classname="Patient_Browse_Clinic",
            font=FONT, isPlaced=True
        )

    def createbutton(self):
        self.submitButton = self.controller.buttonCreator(
            ipath="assets/Dashboard/PatientAssets/PatientBrowseClinicSearchButton.png", x=780 , y=80,
            classname = "PatientSetLocation" , root=self, buttonFunction=lambda:[print('print=Submit')]
        )
