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


class DoctorBrowseClinic(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="secondarypanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.createFormEntries()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/DoctorAssets/DoctorClinic.png",
            x=0, y=0, classname="DoctorClinic", root=self
        )

    def createFormEntries(self):
        CREATOR = self.controller.ttkEntryCreator
        FONT = ("Arial", 16)

        self.patientName = CREATOR(
            x=302, y=322, width=435, height=35,
            root=self, classname="doc_name",
            font=FONT, isPlaced=True
        )
        self.patientContact = CREATOR(
            x=302, y=382, width=435, height=35,
            root=self, classname="doc_email",
            font=FONT, isPlaced=True
        )
        self.patientEmail = CREATOR(
            x=302, y=441, width=435, height=35,
            root=self, classname="doc_phoneNo",
            font=FONT, validation="isEmail",
            isPlaced=True
        )
        self.patientAge = CREATOR(
            x=302, y=500, width=435, height=35,
            root=self, classname="doc_age",
            font=FONT, isPlaced=True
        )
        self.patientGender = CREATOR(
            x=302, y=559, width=435, height=35,
            root=self, classname="doc_gender",
            font=FONT, isPlaced=True
        )
        self.patientICNo = CREATOR(
            x=302, y=618, width=435, height=35,
            root=self, classname="doc_races",
            font=FONT, isPlaced=True
        )
        self.medReportMedicines = CREATOR(
            x=302, y=677, width=435, height=35,
            root=self, classname="doc_nationality",
            font=FONT, isPlaced=True
        )
        self.medReportSymptoms = CREATOR(
            x=302, y=736, width=435, height=35,
            root=self, classname="doc_passport",
            font=FONT, isPlaced=True
        )
        self.medReportAllergies = CREATOR(
            x=1024, y=322, width=435, height=35,
            root=self, classname="doc_clinic_name1",
            font=FONT, isPlaced=True
        )
        self.appDetailsDate = CREATOR(
            x=1024, y=378, width=435, height=35,
            root=self, classname="doc__clinic_email",
            font=FONT, isPlaced=True
        )
        self.appDetailsTime = CREATOR(
            x=1024, y=434, width=435, height=35,
            root=self, classname="doc_clinic_name",
            font=FONT, isPlaced=True
        )
        self.appDetailsTime = CREATOR(
            x=1024, y=490, width=435, height=35,
            root=self, classname="doc_address_1",
            font=FONT, isPlaced=True
        )
        self.appDetailsTime = CREATOR(
            x=1024, y=544, width=435, height=35,
            root=self, classname="doc_address_2",
            font=FONT, isPlaced=True
        )

        
        




