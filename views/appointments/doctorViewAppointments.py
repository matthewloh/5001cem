from abc import ABC, abstractmethod
import calendar
import re
import os
import threading
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
import pyperclip
from prisma.models import Patient
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from ttkbootstrap.dialogs.dialogs import DatePickerDialog
from resource.basewindow import gridGenerator
from resource.static import *
from resource.basewindow import ElementCreator
import tkintermapview
from geopy.geocoders import GoogleV3
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
        self.user = self.parent.user
        self.createFrames()
        self.createElements()
        self.InputLocation()
        self.searchLocation()
        self.LoadClinicList()
        self.ImplementMap()
        self.createButtonRefresh()
        self.refreshPage()
       
    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/DoctorAssets/AssignToClinic.png",
            x=0, y=0, classname="secondarypanelbg", root=self
        )
    
    

    def InputLocation(self):
        CREATOR = self.controller.ttkEntryCreator
        FONT = ("Arial", 24)

        self.SelectAddress = CREATOR(
            x=20, y=250, width=739, height=80,
            root=self, classname="Search_Clinic",
            font=FONT, isPlaced=True
        )

    def searchLocation(self):
        def updateLocation():
            new_address = self.SelectAddress.get()
            print("New Address:", new_address)
            self.clinicsMap.set_address(new_address)
        self.searchButton = self.controller.buttonCreator(
            ipath="assets/Dashboard/DoctorAssets/DoctorListButton/SearchLocation.png",
            classname=f"SearchLocations", root=self,
            x=684, y=257, buttonFunction=updateLocation,
            isPlaced=True,
        )

    
    def LoadClinicList(self):   
        prisma = self.prisma
        doctor = prisma.doctor.find_first(
            where={
                "userId": self.user.id
            }
        )
        print("Doctor", doctor)

        if doctor:
        # If the doctor is found, exclude clinics associated with the doctor
            Clinics = prisma.clinic.find_many(
                where={
                    "NOT": {
                        "id": doctor.clinicId
                    }
                }
            )
        else:
            # If the doctor is not found, retrieve all clinics
            clinics = prisma.clinic.find_many()

        h = len(str(Clinics)) * 120
        if h < 760:
            h = 760
        self.appointmentListFrame = ScrolledFrame(
            master=self, width=1500, height=h, autohide=True, bootstyle="DoctorDashboard.bg"
        )
        self.appointmentListFrame.grid_propagate(False)
        self.appointmentListFrame.place(x=835, y=281, width=795, height=717)
        COORDS = (0, 0)
        for clinicDoctor in Clinics:
            ClinicName = clinicDoctor.name
            ClinicLocation = clinicDoctor.address
            ClinicState = clinicDoctor.state
            ClinicOpenHrs = clinicDoctor.clinicHrs

            X = COORDS[0]
            Y = COORDS[1]
            R = self.appointmentListFrame
            self.controller.labelCreator(
                x=X, y=Y, classname=f"{clinicDoctor.id}_bg", root=R,
                ipath="assets/Dashboard/DoctorAssets/DoctorListButton/ClinicList.png",
                isPlaced=True,
            )
            ClinicNames = self.controller.scrolledTextCreator(
                x=X+25, y=Y+16, width=145, height=55, root=R, classname=f"{clinicDoctor.id}_ClinicNames",
                bg="#3D405B", hasBorder=False,
                text=f"{ClinicName}", font=("Inter", 20), fg=WHITE,
                isDisabled=True, isJustified=True, justification="center",
                isPlaced=True,
            )
            ClinicLocations = self.controller.scrolledTextCreator(
                x=X+185, y=Y+16, width=145, height=55, root=R, classname=f"{clinicDoctor.id}_ClinicLocations",
                bg="#3D405B", hasBorder=False,
                text=f"{ClinicLocation}", font=("Inter", 18), fg=WHITE,
                isDisabled=True, isJustified=True, justification="center",
                isPlaced=True,
            )
            ClinicStates = self.controller.scrolledTextCreator(
                x=X+350, y=Y+16, width=145, height=55, root=R, classname=f"{clinicDoctor.id}_ClinicStates",
                bg="#3D405B", hasBorder=False,
                text=f"{ClinicState}", font=("Inter", 18), fg=WHITE,
                isDisabled=True, isJustified=True, justification="center",
                isPlaced=True,
            )
            ClinicOpenHrs = self.controller.scrolledTextCreator(
                x=X+505, y=Y+16, width=145, height=55, root=R, classname=f"{clinicDoctor.id}_ClinicOpenHrs",
                bg="#3D405B", hasBorder=False,
                text=f"{ClinicOpenHrs}", font=("Inter", 18), fg=WHITE,
                isDisabled=True, isJustified=True, justification="center",
                isPlaced=True,
            )
            self.controller.buttonCreator(
                ipath="assets/Dashboard/DoctorAssets/DoctorListButton/FindLocation.png",
                classname=f"FindLocation{clinicDoctor.id}", root=R,
                x=X+666, y=Y,  buttonFunction=lambda loc=ClinicLocation: self.copy_location(loc),
                isPlaced=True,
            )
            self.controller.buttonCreator(
                ipath="assets/Dashboard/DoctorAssets/DoctorListButton/SendRequest.png",
                classname=f"SendRequest{clinicDoctor.id}", root=R,
                x=725, y=Y, buttonFunction=lambda doc_id=doctor.id, clinic_id=clinicDoctor.id: self.submit_request(doc_id, clinic_id),
                isPlaced=True,
            )
            COORDS = (COORDS[0], COORDS[1] + 120)

    def submit_request(self, doctor_id, clinic_id):
        prisma = self.prisma
        prisma.doctorassignclinic.create({
            "doctorId": doctor_id,
            "clinicId": clinic_id,
            "status": "PENDING", 
        })

        messagebox.showinfo("Request Submitted", "Your request has been submitted successfully.")
        
    def copy_location(self, location):
        pyperclip.copy(location)

    def ImplementMap(self):
        self.loc = GoogleV3(api_key=os.getenv(
            "MAPS_API_KEY"), user_agent="myGeocoder")
        
        self.clinicsMap = tkintermapview.TkinterMapView(
            self,  width=739, height=638, corner_radius=12)
        self.clinicsMap.place(x=20, y=352)
        self.clinicsMap.set_address("Penang, Malaysia")
        self.clinicsMap.set_zoom(13)
        self.clinicsMap.set_tile_server(
            "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)


    def createButtonRefresh(self):
        self.navigateToClinicPage = self.controller.buttonCreator(
        ipath="assets/Dashboard/DoctorAssets/DoctorListButton/RefreshButton.png", x=1535, y=116,
        classname="ButtonRefreshClinic", root=self, buttonFunction=lambda: self.refreshPage(),
        isPlaced=True,
    )
           
    def refreshPage(self):
        self.createButtonRefresh()

    







        
 


    