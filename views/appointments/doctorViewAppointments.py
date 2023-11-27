from abc import ABC, abstractmethod
import calendar
import re
import threading
from tkinter import *
from tkinter import messagebox
from prisma.models import Patient
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
            ipath="assets/Dashboard/DoctorAssets/HealthRecord.png",
            x=0, y=0, classname="secondarypanelbg", root=self
        )

    def loadpatient(self, patient:Patient):
        self.currentPatient : Patient = patient
        patientID = patient.id
        print(patientID)
        self.getPatientHealthRecord(patient)
        pass


    def getPatientHealthRecord(self, patient: Patient):
        prisma = self.prisma
        viewHealthRecord = prisma.patient.find_first(
            where={
                "id": self.currentPatient.id  
            },
            include={
                "healthRecord": True,
            }
        )
        if viewHealthRecord:
            healthRecord = viewHealthRecord.healthRecord 

            allergies = healthRecord.allergies 
            bloodtype = healthRecord.bloodType
            currentMedication = healthRecord.currentMedication
            familyHistory = healthRecord.familyHistory
            height = healthRecord.height
            pastMedication = healthRecord.pastMedication
            pastSurgery = healthRecord.pastSurgery
            weight = healthRecord.weight
                
            allergiesRecord = self.controller.scrolledTextCreator(
               x=302, y=245, width=438, height=50, classname=f"allergiesRecords",
               root=self, bg="#D1E8E2", hasBorder=TRUE,
               text=f"{allergies}", font=("Inter", 20), fg=BLACK,
               isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            bloodtypeRecord = self.controller.scrolledTextCreator(
                x=302, y=345, width=438, height=50, classname=f"bloodtypeRecords",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{currentMedication}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            currentMedicationRecord = self.controller.scrolledTextCreator(
                x=302, y=445, width=438, height=50, classname=f"currentMedicationRecords",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{height}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            familyHistoryRecord = self.controller.scrolledTextCreator(
                x=302, y=545, width=438, height=50, classname=f" familyHistoryRecords",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{pastSurgery}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            heightRecord = self.controller.scrolledTextCreator(
                x=302, y=645, width=438, height=50, classname=f"heightRecords",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{bloodtype}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            pastMedicationRecord = self.controller.scrolledTextCreator(
                x=302, y=745, width=438, height=50, classname=f"pastMedicationRecords",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{familyHistory}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            pastSurgeryRecord = self.controller.scrolledTextCreator(
                x=302, y=845, width=438, height=50, classname=f"pastSurgeryRecords",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{pastMedication}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )

            weightRecord = self.controller.scrolledTextCreator(
                x=302, y=945, width=438, height=50, classname=f"weightRecords",
                root=self, bg="#D1E8E2", hasBorder=True,
                text=f"{weight}", font=("Inter", 20), fg=BLACK,
                isDisabled=True, isJustified=True, justification="center", isPlaced=True,
            )
       


    