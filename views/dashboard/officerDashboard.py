from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from views.mainDashboard import Dashboard

import calendar
import datetime as dt
import os
import re
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
    def __init__(self, parent: Dashboard = None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="primarypanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.prisma = self.controller.mainPrisma
        self.user = self.parent.user
        self.createFrames()
        self.createElements()

    def createFrames(self):
        pass

    def unloadStackedFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath=r"assets/Dashboard/OfficerAssets/OfficerDashboardPanelBG.png",
            x=0, y=0, classname="primarypanelbg", root=self
        )

        self.controller.buttonCreator(
            ipath=r"assets/Dashboard/OfficerAssets/officerrefreshbtn.png",
            x=1560, y=120, classname="refreshbtn", root=self,
            buttonFunction=lambda: [self.refreshClinicsSideFrame()]
        )

        self.initializeGovRegSystem()
        self.initializeApprovedClinicDetails()
        self.loadSupervisedClinicsOnMap()
        self.loadClinicsIntoSideFrame()
        self.loadClinicsIntoBottomFrame()
        self.loadClinicsSearchBar()

    def loadClinicsIntoSideFrame(self):
        h = len(self.systemManaged.programmeRegistration) * 120
        if h < 760:
            h = 760
        self.clinicsListFrame = ScrolledFrame(
            master=self, width=780, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.clinicsListFrame.grid_propagate(False)
        self.clinicsListFrame.place(x=880, y=260, width=780, height=750)
        COORDS = (20, 20)
        for clinicEnrolment in self.systemManaged.programmeRegistration:
            clinic = clinicEnrolment.clinic
            X = COORDS[0]
            Y = COORDS[1]
            R = self.clinicsListFrame
            self.controller.labelCreator(
                x=X, y=Y, classname=f"{clinic.id}_bg", root=R,
                ipath="assets/Dashboard/OfficerAssets/clinicsstatusbg.png",
                isPlaced=True, bg="#f1feff"
            )
            clinicname = self.controller.scrolledTextCreator(
                x=X+20, y=Y, width=180, height=100, root=R, classname=f"{clinic.id}_name",
                bg="#f1feff", hasBorder=False,
                text=clinic.name, font=("Inter", 14), fg=BLACK,
                isDisabled=True, isJustified=True,
            )
            clinicPhone = self.controller.scrolledTextCreator(
                x=X+220, y=Y, width=180, height=100, root=R, classname=f"{clinic.id}_phone_num",
                bg="#f1feff", hasBorder=False,
                text=clinic.phoneNum, font=("Inter", 14), fg=BLACK,
                isDisabled=True, isJustified=True
            )
            clinicAddress = self.controller.scrolledTextCreator(
                x=X+420, y=Y, width=220, height=100, root=R, classname=f"{clinic.id}_address",
                bg="#f1feff", hasBorder=False,
                text=clinic.address, font=("Inter", 12), fg=BLACK,
                isDisabled=True, isJustified=True, justification="left",
            )

            if clinicEnrolment.status == "APPROVED":
                statusimage = "assets/Dashboard/OfficerAssets/approved.png"
            elif clinicEnrolment.status == "PENDING":
                statusimage = "assets/Dashboard/OfficerAssets/pending.png"
            elif clinicEnrolment.status == "REJECTED":
                statusimage = "assets/Dashboard/OfficerAssets/rejected.png"

            clinicStatus = self.controller.buttonCreator(
                x=X+660, y=Y+20, classname=f"{clinic.id}_status", root=R,
                ipath=statusimage,
                buttonFunction=lambda c=clinic.id: [self.updateClinicStatus(c)],
                isPlaced=True
            )
            COORDS = (
                COORDS[0], COORDS[1] + 120
            )

    def loadClinicsIntoBottomFrame(self):
        h = len(self.approvedClinics.programmeRegistration) * 120
        if h < 150:
            h = 150
        self.clinicStatusFrame = ScrolledFrame(
            master=self, width=840, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.clinicStatusFrame.grid_propagate(False)
        self.clinicStatusFrame.place(x=20, y=820, width=840, height=185)
        COORDS = (20, 20)
        for clinicEnrolment in self.approvedClinics.programmeRegistration:
            clinic = clinicEnrolment.clinic
            X = COORDS[0]
            Y = COORDS[1]
            R = self.clinicStatusFrame
            self.controller.labelCreator(
                x=X, y=Y, classname=f"{clinic.id}_statusname", root=R,
                ipath="assets/Dashboard/OfficerAssets/clinicstatusrectangle.png",
                isPlaced=True,
            )
            clinicname = self.controller.scrolledTextCreator(
                x=X+20, y=Y, width=180, height=60, root=R, classname=f"{clinic.id}_name",
                bg="#f1feff", hasBorder=False,
                text=clinic.name, font=("Inter", 14), fg=BLACK,
                isDisabled=True, isJustified=True,

            )
            clinicContact = self.controller.scrolledTextCreator(
                x=X+210, y=Y, width=180, height=60, root=R, classname=f"{clinic.id}_phone_num",
                bg="#f1feff", hasBorder=False,
                text=clinic.phoneNum, font=("Inter", 14), fg=BLACK,
                isDisabled=True, isJustified=True

            )
            numOfDoctors = len(clinic.doctor) if not clinic.doctor == None else 0
            clinicNumOfDoctors = self.controller.scrolledTextCreator(
                x=X+420, y=Y, width=180, height=60, root=R, classname=f"{clinic.id}_num_of_doctors",
                bg="#f1feff", hasBorder=False,
                text=f"{numOfDoctors} doctor(s)", font=("Inter", 12), fg=BLACK,
                isDisabled=True, isJustified=True,
            )
            clinicPatients = self.controller.scrolledTextCreator(
                x=X+620, y=Y, width=180, height=60, root=R, classname=f"{clinic.id}_patients",
                bg="#f1feff", hasBorder=False,
                text="patient", font=("Inter", 12), fg=BLACK,
                isDisabled=True, isJustified=True,
            )

            COORDS = (
                COORDS[0], COORDS[1] + 75
            )

    def loadClinicsSearchBar(self):
        clinicsSearchBar = self.controller.buttonCreator(
            x=1241, y=19, classname="officer_search_bar", root=self,
            ipath="assets/Dashboard/OfficerAssets/officersearchbar.png",
            isPlaced=True, buttonFunction=lambda: [self.loadClinicsEntry()]
        )
    
    def loadClinicsEntry(self):
        clinicsSearchEntry = self.controller.ttkEntryCreator(
            x=1241, y=19, width=419, height=70, root=self,
            classname="officer_search_entry", placeholder="Search",
            isPlaced=True, font=("Inter", 14), fg=BLACK,
            bgcolor="#f1feff"
        )
        clinicsSearchEntry.bind("<Return>", lambda e: [self.searchFromSearchBar(clinicsSearchEntry.get())])  
        clinicsSearchEntry.bind("<FocusIn>", lambda e: [clinicsSearchEntry.delete(0, END)] if clinicsSearchEntry.get() == "Search" else None)
        clinicsSearchEntry.bind("<FocusOut>", lambda e: [clinicsSearchEntry.grid_forget(), self.loadClinicsSearchBar()])

    def refreshClinicsSideFrame(self):
        self.initializeGovRegSystem()
        self.loadClinicsIntoSideFrame()
        self.loadClinicsIntoBottomFrame()
        

    def loadSupervisedClinicsOnMap(self):
        self.loc = GoogleV3(api_key=os.getenv(
            "MAPS_API_KEY"), user_agent="myGeocoder")
        # insert map

        self.clinicsMap = tkintermapview.TkinterMapView(
            self,  width=840, height=620, corner_radius=12)
        self.clinicsMap.place(x=20, y=100)
        self.clinicsMap.set_address(
            f"{self.systemManaged.state.replace('_', ' ').title()}, Malaysia")
        self.clinicsMap.set_zoom(13)
        self.clinicsMap.set_tile_server(
            "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

        for clinicEnrolment in self.systemManaged.programmeRegistration:
            clinic = clinicEnrolment.clinic
            structuredAddress = f"{clinic.address}, {clinic.zip}, {clinic.city}, {clinic.state.replace('_', ' ').title()}"
            clinicCoordinates = self.loc.geocode(structuredAddress)
            self.clinicsMap.set_marker(
                clinicCoordinates.latitude, clinicCoordinates.longitude, text=clinic.name
            )

    


    def initializeGovRegSystem(self):
        self.systemManaged = self.prisma.govregsystem.find_first(
            where={
                "supervisingOfficer": {"some": {"userId": self.user.id}}
            },
            include={
                "programmeRegistration": {
                    "include":
                    {
                        "clinic": True
                    }
                }
            }
        )

    def updateClinicStatus(self, clinic):
        #if clinic is approved, then change clinic to pending, change approved image to pending image
        #if clinic is pending, then change clinic to approved, change pending image to approved image
        self.clinicEnrolment = self.prisma.clinicenrolment.find_first(
            where={
                "clinicId": clinic
            }
        )

        if self.clinicEnrolment.status == "APPROVED":
            self.clinicEnrolment = self.prisma.clinicenrolment.update(
                data={"status": "PENDING"},
                where={"clinicId_govRegId": {"clinicId": clinic, "govRegId": self.systemManaged.id}},
                include={"clinic": True}
            )
            
            self.initializeGovRegSystem()
            self.initializeApprovedClinicDetails()
            self.loadClinicsIntoSideFrame()
            self.loadClinicsIntoBottomFrame()
            self.loadAssets()
            
        elif self.clinicEnrolment.status == "PENDING":  
            self.clinicEnrolment = self.prisma.clinicenrolment.update(
                data={"status": "APPROVED"},
                where={"clinicId_govRegId": {"clinicId": clinic, "govRegId": self.systemManaged.id}},
                include={"clinic": True}
            )

            self.initializeGovRegSystem()
            self.initializeApprovedClinicDetails()
            self.loadClinicsIntoSideFrame()
            self.loadClinicsIntoBottomFrame()

        
        elif self.clinicEnrolment.status == "REJECTED":
            self.clinicEnrolment = self.prisma.clinicenrolment.update(
                data={"status": "REJECTED"},
                where={"clinicId_govRegId": {"clinicId": clinic, "govRegId": self.systemManaged.id}},
                include={"clinic": True}
            )

            self.initializeGovRegSystem()
            self.initializeApprovedClinicDetails()
            self.loadClinicsIntoSideFrame()
            self.loadClinicsIntoBottomFrame()


    def initializeApprovedClinicDetails(self):
        self.approvedClinics = self.prisma.govregsystem.find_first(
            where={
                "supervisingOfficer": {"some": {"userId": self.user.id}}
            },
            include={
                "programmeRegistration": {
                    "where": {
                        "status": "APPROVED"
                    },
                    "include":
                    {
                        "clinic": {
                            "include": {
                                "doctor": True
                            }
                        }
                    }
                }
            }
        )

    def searchFromSearchBar(self, query:str):
        if query == "" or query == "Search":
            messagebox.showerror("Error", "Please enter a search request")
            
            return
        query = query.lower()
        
        self.systemManaged = self.prisma.govregsystem.find_first(
            where={
                "supervisingOfficer": {"some": {"userId": self.user.id}}
            },
            include={
                "programmeRegistration": {
                    "where":{
                        "clinic":{
                            "is":{
                                "name":{"contains": query}
                            }
                        }
                    }
                    ,"include":
                    {
                        "clinic": True
                    }
                }
            }
        )
        
        self.loadClinicsIntoSideFrame()
        
            

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
