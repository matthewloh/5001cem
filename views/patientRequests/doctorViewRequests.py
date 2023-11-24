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
        self.submitPrescription() 
        # self.loadAppointment()
       # self.ScrolledFrame()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/DoctorAssets/DoctorRequestPrecription.png",
            x=0, y=0, classname="requestspanelbg", root=self
        )

    def createFormEntries(self):
        CREATOR = self.controller.ttkEntryCreator
        FONT = ("Arial", 16)

        self.presTitle = ScrolledText(
            master=self, autohide=True, width=640, height=345,
        )
        self.presTitle.place(
            x=40, y=299, w=839 ,h=120,
        )
        self.presTitleTextArea = self.presTitle.text

        self.presDesc = ScrolledText(
            master=self, autohide=True, width=640, height=345,
        )
        self.presDesc.place(
            x=40, y=521 ,w=839 ,h=288,
        )
        self.presTitleTextArea = self.presTitle.text


    def createbutton(self):
        self.submitButton = self.controller.buttonCreator(
            ipath="assets/Dashboard/DoctorAssets/DoctorListButton/Pressubmitbutton.png", x=314 , y=948,
            classname = "doctorSubmitbutton" , root=self, buttonFunction=lambda: self.submitPrescription(),
        )
        
    def submitPrescription(self):
        title_data = self.presTitle.get("1.0", "end-1c")
        desc_data = self.presDesc.get("1.0", "end-1c")

        try:
            prescription = self.prisma.prescription.create(
                data={
                    "title": title_data,
                    "desc": desc_data,
                    "appointmentId": self.currentAppointment.id,  # Replace with the actual appointment ID
                }
            )
            print("Prescription submitted successfully:", prescription)
        except Exception as e:
            print("Error submitting prescription:", e)

       
        self.presTitle.delete("1.0", "end")
        self.presDesc.delete("1.0", "end")

    def loadAppointment(self, appointment:Appointment):
        #pass appointment details
        self.currentAppointment : Appointment = appointment
        appId = appointment.id
        prescriptionList = appointment.prescription
        patient = appointment.appRequest.patient
        patientName = patient.user.fullName
        patientEmail = patient.user.email
        patientPhone = patient.user.contactNo
        print(appId,)
        print(patientName, patientEmail, patientPhone)
        pass

    def ScrolledFrame(self, appointment: Appointment):
        prisma = self.prisma
        viewPrescriptionList = prisma.appointment.find_many(
            include={
                    "include": {
                        "patient": {
                            "include": {
                                "user": True,
                            }
                        }
                    }
                }
            )
               
        h = len(viewPrescriptionList) * 120
        if h < 760:
            h = 760
        self.viewPrescriptionList = ScrolledFrame(
            master=self, width=1500, height=h, autohide=True, bootstyle="border.bg"
        )
        self.viewPrescriptionList.grid_propagate(False)
        self.viewPrescriptionList.place(x=949, y=282, width=681, height=721)
        COORDS = (5, 5)
        for prescriptions in viewPrescriptionList:

            patientName = prescriptions.appRequest.patient.user.fullName
            patientContact = prescriptions.appRequest.patient.user.contactNo
            patientEmail = prescriptions.appRequest.patient.user.email

            X = COORDS[0]
            Y = COORDS[1]
            R = self.viewPrescriptionList
            self.controller.labelCreator(
                x=X, y=Y, classname=f"{prescriptions.id}_bg", root=R,
                ipath="assets/Dashboard/DoctorAssets/DoctorListButton/RequestPrescriptionList.png",
                isPlaced=True,
            )
            PresPatientName = self.controller.scrolledTextCreator(
                x=X+5, y=Y+30, width=145, height=60, root=R, classname=f"{prescriptions.id}_Pres_req_name",
                bg="#3D405B", hasBorder=False,
                text=f"{patientName}", font=("Inter", 20), fg=WHITE,
                isDisabled=True, isJustified=True, justification="center",
            )
            PresPatientContact = self.controller.scrolledTextCreator(
                x=X+170, y=Y+30, width=145, height=60, root=R, classname=f"{prescriptions.id}_Pres_req_phone_num",
                bg="#3D405B", hasBorder=False,
                text=f"{patientContact}", font=("Inter", 18), fg=WHITE,
                isDisabled=True, isJustified=True, justification="center",
            )  
            PresPatientEmail = self.controller.scrolledTextCreator(
                x=X+335, y=Y+30, width=145, height=60, root=R, classname=f"{prescriptions.id}_Pres_req_Email",
                bg="#3D405B", hasBorder=False,
                text=f"{patientEmail}", font=("Inter", 18), fg=WHITE,
                isDisabled=True, isJustified=True, justification="center",
            )
            self.controller.buttonCreator(
                ipath="assets/Dashboard/DoctorAssets/DoctorListButton/AccpectPrescription.png",
                classname=f"AcceptPrescriptonbutton{prescriptions.id}", root=R,
                x=510, y=Y+30, buttonFunction=lambda t = prescriptions.id: [print(f"hide {t}")],
                isPlaced=True,
            )
            self.controller.buttonCreator(
                ipath="assets/Dashboard/DoctorAssets/DoctorListButton/RejectPrescription.png",
                classname=f"RejectPrescriptonbutton{prescriptions.id}", root=R,
                x=X+590, y=Y+30, buttonFunction=lambda t = prescriptions.id: [print(f"delete {t}")],
                isPlaced=True
            )
            COORDS = (COORDS[0], COORDS[1] + 120)

