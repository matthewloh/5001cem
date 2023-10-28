from abc import ABC, abstractmethod
import calendar
import re
import threading
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from prisma.models import Appointment
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from tkinter import Scrollbar
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from ttkbootstrap.dialogs.dialogs import DatePickerDialog
from resource.basewindow import gridGenerator
from resource.static import *
from resource.basewindow import ElementCreator
from datetime import datetime, timedelta
import datetime as dt
from pendulum import timezone
import tkintermapview
from prisma.models import doctorPrescription


class DoctorViewPatientRequests(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="requestspanel")
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
            ipath="assets/Dashboard/DoctorAssets/patientPrescription/interfacepatientprescription.png",
            x=0, y=0, classname="requestspanelbg", root=self
        )

    def createFormEntries(self):
        # Using these constants as an alias, it's dependent on you to structure the code
        CREATOR = self.controller.ttkEntryCreator
        FONT = ("Arial", 16)

        self.patientName = CREATOR(
            x=480, y=56, width=370, height=42,
            root=self, classname="doc_searchprescription",
            font=FONT, isPlaced=True
        )

        self.patientName = CREATOR(
            x=300, y=281, width=440, height=40,
            root=self, classname="doc_patientnameentry",
            font=FONT, isPlaced=True
        )
        self.patientContact = CREATOR(
            x=300, y=330, width=440, height=40,
            root=self, classname="doc_patientcontactentry",
            font=FONT, isPlaced=True
        )
        self.patientEmail = CREATOR(
            x=300, y=380, width=440, height=40,
            root=self, classname="doc_patientemailentry",
            font=FONT, validation="isEmail",
            isPlaced=True
        )
        self.patientAge = CREATOR(
            x=300, y=429, width=440, height=40,
            root=self, classname="doc_patientageentry",
            font=FONT, isPlaced=True
        )
        self.patientGender = CREATOR(
            x=300, y=478, width=440, height=40,
            root=self, classname="doc_patientgenderentry",
            font=FONT, isPlaced=True
        )
        self.patientICNo = CREATOR(
            x=300, y=527, width=440, height=40,
            root=self, classname="doc_patienticnoentry",
            font=FONT, isPlaced=True
        )
        # Consider updating the placements on figma
        # to be a clean multiple of 20
        # You might have to use isPlaced=True and then use place_forget in the future
        self.medReportMedicines = CREATOR(
            x=300, y=650, width=440, height=40,
            root=self, classname="doc_medreportmedicinesentry",
            font=FONT, isPlaced=True
        )
        self.medReportSymptoms = CREATOR(
            x=300, y=699, width=440, height=40,
            root=self, classname="doc_medreportsymptomsentry1",
            font=FONT, isPlaced=True
        )
        self.medReportAllergies = CREATOR(
            x=300, y=748, width=440, height=40,
            root=self, classname="doc_medreportsymptomsentry",
            font=FONT, isPlaced=True
        )
        self.appDetailsDate = CREATOR(
            x=1030, y=281, width=440, height=40,
            root=self, classname="doc_appdetailsdateentry",
            font=FONT, isPlaced=True
        )
        self.appDetailsTime = CREATOR(
            x=1030, y=330, width=440, height=40,
            root=self, classname="doc_appdetailstimeentry",
            font=FONT, isPlaced=True
        )
        self.appDetailsDuration = CREATOR(
            x=1030, y=378, width=440, height=40,
            root=self, classname="doc_appdetailsdurationentry",
            font=FONT, isPlaced=True
        )
        self.detailsText = ScrolledText(
            master=self, autohide=True, width=640, height=345,
        )
        self.detailsText.place(
            x=920, y=495, width=645, height=330
        )
        self.detailsTextArea = self.detailsText.text

    def createbutton(self):
        self.submitButton = self.controller.buttonCreator(
            ipath="assets/Dashboard/DoctorAssets/patientPrescription/DoctorSubmitButton.png", x=682 , y=880,
            classname = "doctorSubmitbutton" , root=self, buttonFunction=lambda:[print('print=Submit')]
        )
