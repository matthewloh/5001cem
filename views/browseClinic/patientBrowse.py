from abc import ABC, abstractmethod
import calendar
import re
import threading
import ttkbootstrap as tb
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
        self.loadAppScrolledFrame()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/PatientAssets/PatientBrowseClinic.png",
            x=0, y=0, classname="secondarypanelbg", root=self
        )
        self.createButtons()
        self.createEntry()

    def createButtons(self):
        CREATOR = self.controller.buttonCreator
        IP, X, Y, CN, R, BF = "ipath", "x", "y", "classname", "root", "buttonFunction"
        name = "browseclinic"
        params = {
            "searchbutton": {
                IP: "assets/BrowseClinic/Patient/Search.png",
                X: 780,
                Y: 80,
                CN: f"{name}_searchbtn",
                R: self,
                BF: lambda: [print('test')]
            },
        }
        for param in params:
            CREATOR(**params[param])

    def createEntry(self):
        CREATOR = self.controller.ttkEntryCreator
        self.searchEntry = CREATOR(
            x=0, y=80,
            width=780, height=80,
            classname="searchentry", root=self,
            placeholder="Search for clinics"
        )

        self.clinicsMap = tkintermapview.TkinterMapView(
            self,  width=860, height=640)
        self.clinicsMap.place(x=0, y=180)
        self.clinicsMap.set_address("Penang, Malaysia")
        self.clinicsMap.set_tile_server(
            "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22) 
        
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

        #first scroll frame
        self.viewClinicStatus = ScrolledFrame(
            master=self, width=1500, height=h, bootstyle="bg-round", autohide=True
        )
        self.viewClinicStatus.place(
            x=8, y=906, width=837, height=136)
        initCoords = (5, 5)
        for a in appointments:
            bg = self.controller.labelCreator(
                ipath="assets/Dashboard/PatientAssets/PatientListButton/PatientBrowseClinicStatus.png",
                x=initCoords[0], y=initCoords[1], classname=f"browseClinicStatus{a}", root=self.viewClinicStatus,
                isPlaced=True
            )
            initCoords = (initCoords[0], initCoords[1] + 55)

    
        self.viewClinicList = ScrolledFrame(
            master=self, width=1500, height=h, bootstyle="bg-round", autohide=True
        )
        self.viewClinicList.place(
            x=907, y=350, width=750, height=692)
        initCoords = (5, 5)
        for a in appointments:
            #a.fullname.userId
            bg = self.controller.labelCreator(
                ipath="assets/Dashboard/PatientAssets/PatientListButton/PatientBrowseClinicLIst.png",
                x=initCoords[0], y=initCoords[1], classname=f"browseClinicList{a}", root=self.viewClinicList,
                isPlaced=True
            )
            initCoords = (initCoords[0], initCoords[1] + 120)


        
    def createFormEntries(self):
        CREATOR = self.controller.ttkEntryCreator
        FONT = ("Arial", 24)

        self.patientBrowserSelectAddress = CREATOR(
            x=0, y=80, width=780, height=80,
            root=self, classname="Patient_Browse_Clinic1",
            font=FONT, isPlaced=True
        )

        # Add a placeholder/hint text
        self.patientBrowserSelectAddress.insert(50, "Enter your address here")
       

        self.patientBrowserSearchClinic = CREATOR(
            x=1494, y=190, width=158, height=75,
            root=self, classname="Patient_Browse_Clinic",
            font=FONT, isPlaced=True
        )

        self.patientBrowserSearchClinic.insert(0, "Search")

    def createbutton(self):
        self.submitButton = self.controller.buttonCreator(
            ipath="assets/Dashboard/PatientAssets/PatientBrowseClinicSearchButton.png", x=780 , y=80,
            classname = "PatientSetLocation" , root=self, buttonFunction=lambda:[print('print=Submit')]
        )
