import calendar
import datetime as dt
import re,os
import textwrap
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from resource.basewindow import ElementCreator, gridGenerator
from resource.static import *
from tkinter import *
from tkinter import messagebox

import tkintermapview
from geopy.geocoders import GoogleV3
from pendulum import timezone
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from ttkbootstrap.dialogs.dialogs import DatePickerDialog
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.toast import ToastNotification

from views.mainBrowseClinic import MainBrowseClinic
from views.mainGRDRequests import MainGRDRequestsInterface


class GovOfficerDashboard(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="primarypanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.loadClinicsList()
        self.loadClinicsStatusList()

    def createFrames(self):
        pass

    def unloadStackedFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath=r"assets/Dashboard/OfficerAssets/OfficerDashboardPanelBG.png",
            x=0, y=0, classname="primarypanelbg", root=self
        )

        # insert map
        self.clinicsMap = tkintermapview.TkinterMapView(
            self,  width=841, height=618)
        self.clinicsMap.place(x=13, y=101)
        self.clinicsMap.set_address("Penang, Malaysia")
        self.loc = GoogleV3(api_key=os.getenv("MAPS_API_KEY"), user_agent="myGeocoder")
        self.clinic1 = self.loc.geocode("603, Jalan Datuk Keramat,Georgetown, Pulau Pinang")
        self.clinic2 = self.loc.geocode("163-1-2, Jalan Permai, Taman Brown, 11700 Georgetown, Pulau Pinang")
        self.clinic3 = self.loc.geocode("725-U, Jalan Sungai Dua, Desa Permai Indah, 11700 Gelugor, Pulau Pinang")
        self.clinic4 = self.loc.geocode("20, Lebuh Penang, George Town, 10450 George Town, Pulau Pinang")
        self.clinic5 = self.loc.geocode("Jln Perak, Taman Desa Green, 11600 George Town, Pulau Pinang")
        self.clinicsMap.set_marker(self.clinic1.latitude, self.clinic1.longitude, text="Klinik Aman")
        self.clinicsMap.set_marker(self.clinic2.latitude, self.clinic2.longitude, text="Klinik Permai")
        self.clinicsMap.set_marker(self.clinic3.latitude, self.clinic3.longitude, text="Klinik Health Plus")
        self.clinicsMap.set_marker(self.clinic4.latitude, self.clinic4.longitude, text="Klinik Sentosa")
        self.clinicsMap.set_marker(self.clinic5.latitude, self.clinic5.longitude, text="Klinik Comfort Care")


        # self.clinicsMap.set_marker("Kuala Lumpur, Malaysia", text="Clinic 2")

        self.clinicsMap.set_tile_server(
            "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        

    def loadClinicsList(self):
        prisma = self.prisma
        clinicsList = prisma.clinicenrolment.find_many(
            include={
                "govRegDocSystem":True,
                "clinic":True,
            }
        )
        h = len(clinicsList) * 120
        if h < 600:
            h = 600
        self.exampleScrolledFrame = ScrolledFrame(
            master=self, width=750, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.exampleScrolledFrame.grid_propagate(False)
        self.exampleScrolledFrame.place(x=888, y=314, width=750, height=620)
        initialcoordinates = (20, 10)

        for clinic in clinicsList:
            clinicid=clinic.clinicId
            clinicName=clinic.clinic.name
            contactNo=clinic.clinic.phoneNum
            address=clinic.clinic.address
            status=clinic.status
            print(status)
            
            x = initialcoordinates[0]
            y = initialcoordinates[1]
            self.controller.textElement(
                ipath=r"assets\Dashboard\cliniclistbg.png", x=x, y=y,
                classname=f"clinicname{clinicid}", root=self.exampleScrolledFrame,
                text=clinicName, size=30, font=INTER,
                isPlaced=True,
            )

            self.controller.textElement(
                ipath=r"assets/Dashboard/clinicdetailsrectangle.png", x=x+200, y=y+15,
                classname=f"contactNo{clinicid}", root=self.exampleScrolledFrame,
                text=contactNo, size=30, font=INTER,
                isPlaced=True,
            )

            self.controller.textElement(
                ipath=r"assets\Dashboard\clinicdetailsrectangle.png", x=x+400, y=y+15,
                classname=f"address{clinicid}", root=self.exampleScrolledFrame,
                text=address, size=10, font=INTER,
                isPlaced=True
            )

            self.controller.textElement(
                ipath=r"assets\Dashboard\clinicstatusrectanglebg.png", x=x+580, y=y+25,
                classname=f"status{clinicid}", root=self.exampleScrolledFrame,
                text=status, size=22, font=INTER,
                isPlaced=True,
            )

            initialcoordinates = (
                initialcoordinates[0], initialcoordinates[1] + 120
            )
    
    def loadClinicsStatusList(self):
        prisma =self.prisma 
        clinicstatus = prisma.clinicenrolment.find_many(
            where={
                "status":"APPROVED"
            }
            ,include={
                "clinic":True,
                "govRegDocSystem":True
            }
        )
       
        h = len(clinicstatus) * 120
        if h < 150:
            h = 150
        self.clinicStatusScrolledFrame = ScrolledFrame(
            master=self, width=798, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.clinicStatusScrolledFrame.grid_propagate(False)
        self.clinicStatusScrolledFrame.place(x=20, y=826, width=825, height=193)
        initialcoordinates = (10, 10)
        for clinics in clinicstatus:
            clinicIdManage = clinics.clinicId
            clinicNameManage = clinics.clinic.name
            clinicContact = clinics.clinic.phoneNum
            clinicDocAvailable = "doctor "
            clinicPatients = "patient"

            x = initialcoordinates[0]
            y = initialcoordinates[1]
            self.controller.textElement(
                ipath=r"assets\Dashboard\OfficerAssets\clinicsstatusbg.png", x=x, y=y,
                classname=f"clinicstatus{clinicIdManage}", root=self.clinicStatusScrolledFrame,
                text=clinicNameManage, size=18, font=INTER,
                isPlaced=True,
            )

            self.controller.textElement(
                ipath=r"assets\Dashboard\miniclinicsdetailsbg.png", x=240, y=y+15,
                classname=f"contacts{clinicIdManage}", root=self.clinicStatusScrolledFrame,
                text=clinicContact, size=18, font=INTER,
                isPlaced=True,
            )

            self.controller.textElement(
                ipath=r"assets\Dashboard\miniclinicsdetailsbg.png", x=440, y=y+15,
                classname=f"docAvailable{clinicIdManage}", root=self.clinicStatusScrolledFrame,
                text=clinicDocAvailable, size=18, font=INTER,
                isPlaced=True,
            )

            self.controller.textElement(
                ipath=r"assets\Dashboard\miniclinicsdetailsbg.png", x=650, y=y+15,
                classname=f"patients{clinicIdManage}", root=self.clinicStatusScrolledFrame,
                text=clinicPatients, size=18, font=INTER,
                isPlaced=True,
            )

            initialcoordinates = (
                initialcoordinates[0], initialcoordinates[1] + 70
            )
        

    def loadAssets(self):
        self.pfp = self.controller.buttonCreator(
            ipath="assets/Dashboard/OfficerAssets/OfficerProfilePicture.png",
            x=20, y=100, classname="profilepicture", root=self.parent,
            buttonFunction=lambda: [print('hello')]
        )
        d = {
            "govofficer": [
                r"assets/Dashboard/OfficerAssets/OfficerManageClinics.png",
                r"assets/Dashboard/OfficerAssets/OfficerClinicRequests.png",
            ],
        }
        self.browseClinic = self.controller.buttonCreator(
            ipath=d["govofficer"][0],
            x=20, y=380, classname="browseclinic_chip", root=self.parent,
            buttonFunction=lambda: [self.loadBrowseClinic()],
        )
        self.viewGRDRequests = self.controller.buttonCreator(
            ipath=d["govofficer"][1],
            x=20, y=460, classname="viewpatients_chip", root=self.parent,
            buttonFunction=lambda: [self.loadGRDRequests()],
        )

    def loadBrowseClinic(self):
        try:
            self.mainInterface.primarypanel.grid()
            self.mainInterface.primarypanel.tkraise()
        except:
            self.mainInterface = MainBrowseClinic(
                controller=self.controller, parent=self.parent)
            self.mainInterface.loadRoleAssets(govofficer=True)

    def loadGRDRequests(self):
        try:
            self.grdRequests.primarypanel.grid()
            self.grdRequests.primarypanel.tkraise()
        except:
            self.grdRequests = MainGRDRequestsInterface(
                controller=self.controller, parent=self.parent)
            self.grdRequests.loadRoleAssets(govofficer=True)
