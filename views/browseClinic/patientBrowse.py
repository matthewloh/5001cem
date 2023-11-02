from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from views.mainDashboard import Dashboard
    from views.dashboard.patientDashboard import PatientDashboard

import calendar
import datetime as dt
import re
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from resource.basewindow import ElementCreator, gridGenerator
from resource.static import *
from tkinter import *
from tkinter import messagebox, ttk
from PIL import ImageTk, Image
import tkintermapview
from geopy.geocoders import GoogleV3
from geopy.distance import geodesic as GD
from pendulum import timezone
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from ttkbootstrap.dialogs.dialogs import DatePickerDialog
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.toast import ToastNotification
from prisma.models import Clinic


class PatientBrowseClinic(Frame):
    def __init__(self, parent: PatientDashboard = None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="browseclinicpanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.user = self.parent.user
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.createFormEntries()
        self.createbutton()
        self.loadAppScrolledFrame()

    def createFrames(self):
        self.loadedClinicFrame = self.controller.frameCreator(
            x=0, y=0, framewidth=1680, frameheight=1080, classname="patient_loadedclinicframe", root=self
        )
        self.loadedClinicFrame.grid_remove()
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Dashboard/PatientAssets/PatientBrowseClinic.png",
            x=0, y=0, classname="secondarypanelbg", root=self
        )
        self.controller.labelCreator(
            ipath="assets/BrowseClinic/Patient/BrowseSingleClinic/BG.png",
            x=0, y=0, classname="browseclinicpanelbg", root=self.loadedClinicFrame
        )
        self.createButtons()
        self.createEntry()
        self.loadApprovedClinicsForUserState()
        self.initializeMapAndPins()
        self.loadClinicsIntoSideFrame()
        self.loadClinicsIntoBottomFrame()

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

    def loadApprovedClinicsForUserState(self):
        self.approvedClinics = self.prisma.clinic.find_many(
            where={
                "clinicRegistration": {
                    "every": {
                        "AND": [
                            {"status": "APPROVED"},
                            {"govRegDocSystem": {
                                "is": {"state": self.user.state.replace(' ', '_').upper()}}}
                        ]
                    }
                }
            },
            include={
                "doctor": {
                    "include": {
                        "user": True
                    }
                }
            }
        )

    def initializeMapAndPins(self):
        self.loc = GoogleV3(api_key=os.getenv(
            "MAPS_API_KEY"), user_agent="myGeocoder")
        # insert map
        HOME = "home"
        self.latitudes = {}
        homeAddress = f"{self.user.addressLine1} {self.user.addressLine2}, {self.user.postcode}, {self.user.city}, {self.user.state.replace('_', ' ').title()}, {self.user.country}"
        homeCoords = self.loc.geocode(homeAddress)
        self.latitudes[HOME] = {}
        self.latitudes[HOME]["latitude"] = homeCoords.latitude
        self.latitudes[HOME]["longitude"] = homeCoords.longitude
        self.clinicsMap = tkintermapview.TkinterMapView(
            self,  width=840, height=540, corner_radius=120,
            bg_color="#dee8e0")
        self.clinicsMap.place(x=20, y=180, width=840, height=540)
        self.clinicsMap.set_address(
            f"{self.user.state.replace('_', ' ').title()}, Malaysia")
        self.clinicsMap.set_zoom(13)
        self.clinicsMap.set_tile_server(
            "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.clinicsMap.set_marker(
            homeCoords.latitude, homeCoords.longitude, text="Home"
        )
        for clinic in self.approvedClinics:
            structuredAddress = f"{clinic.address}, {clinic.zip}, {clinic.city}, {clinic.state.replace('_', ' ').title()}"
            clinicCoordinates = self.loc.geocode(structuredAddress)
            self.latitudes[clinic.id] = {}
            self.latitudes[clinic.id]["latitude"] = clinicCoordinates.latitude
            self.latitudes[clinic.id]["longitude"] = clinicCoordinates.longitude
            self.clinicsMap.set_marker(
                self.latitudes[clinic.id]["latitude"],
                self.latitudes[clinic.id]["longitude"],
                text=clinic.name
            )
            self.latitudes[clinic.id]["distance"] = round(GD((
                self.latitudes[HOME]["latitude"], self.latitudes[HOME]["longitude"]
            ), (clinicCoordinates.latitude, clinicCoordinates.longitude)).km, 2)

    def loadClinicsIntoSideFrame(self):
        h = len(self.approvedClinics) * 120
        if h < 760:
            h = 760
        self.clinicsListFrame = ScrolledFrame(
            master=self, width=780, height=h, autohide=True, bootstyle="bg-rounded"
        )
        self.clinicsListFrame.place(x=880, y=260, width=780, height=760)
        COORDS = (20, 20)
        FONT = ("Inter", 14)
        for clinic in self.approvedClinics:
            X = COORDS[0]
            Y = COORDS[1]
            R = self.clinicsListFrame
            self.controller.labelCreator(
                x=X, y=Y, classname=f"{clinic.id}_bg", root=R,
                ipath="assets/BrowseClinic/Patient/SideFrameRow.png",
                isPlaced=True,
            )
            clinicname = self.controller.scrolledTextCreator(
                x=X+20, y=Y, width=180, height=100, root=R, classname=f"{clinic.id}_name",
                bg="#f1feff", hasBorder=False,
                text=clinic.name, font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True,
            )
            clinicPhone = self.controller.scrolledTextCreator(
                x=X+220, y=Y, width=180, height=100, root=R, classname=f"{clinic.id}_phone_num",
                bg="#f1feff", hasBorder=False,
                text=clinic.phoneNum, font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True
            )
            dist = self.latitudes[clinic.id]["distance"]
            clinicDistance = self.controller.scrolledTextCreator(
                x=X+460, y=Y, width=120, height=100, root=R, classname=f"{clinic.id}_distance",
                bg="#f1feff", hasBorder=False,
                text=dist, font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True
            )
            loadClinic = self.controller.buttonCreator(
                x=X+640, y=Y, classname=f"{clinic.id}_load", root=R,
                ipath="assets/BrowseClinic/Patient/ClickClinic.png",
                buttonFunction=lambda c=clinic: [self.loadClinic(c)],
                isPlaced=True
            )
            COORDS = (
                COORDS[0], COORDS[1] + 120
            )

    def loadClinicsIntoBottomFrame(self):
        h = len(self.approvedClinics) * 100
        h = 180 if h < 180 else h
        self.bottomClinicsListFrame = ScrolledFrame(
            master=self, width=840, height=h, autohide=True, bootstyle="bg-rounded"
        )
        self.bottomClinicsListFrame.place(x=20, y=860, width=840, height=180)
        COORDS = (20, 0)
        for clinic in self.approvedClinics:
            X = COORDS[0]
            Y = COORDS[1]
            R = self.bottomClinicsListFrame
            FONT = ("Inter", 16)
            self.controller.labelCreator(
                x=X, y=Y, classname=f"{clinic.id}_bottom_bg", root=R,
                ipath="assets/BrowseClinic/Patient/BottomRow.png",
                isPlaced=True,
            )
            clinicname = self.controller.scrolledTextCreator(
                x=X+20, y=Y, width=120, height=80, root=R, classname=f"{clinic.id}_name_bottom",
                bg="#f1feff", hasBorder=False,
                text=clinic.name, font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True,
            )
            specialities = [doctor.speciality.title() for doctor in clinic.doctor]
            specialityText = ", ".join(specialities) if len(
                specialities) > 0 else "No doctors yet, check back soon!"
            clinicSpecialities = self.controller.scrolledTextCreator(
                x=X+180, y=Y, width=180, height=80, root=R, classname=f"{clinic.id}_specialities_bottom",
                bg="#f1feff", hasBorder=False,
                text=specialityText, font=("Inter", 12), fg=BLACK,
                isDisabled=True, isJustified=True
            )
            doctorNum = len(clinic.doctor)
            clinicDoctors = self.controller.scrolledTextCreator(
                x=X+400, y=Y, width=80, height=80, root=R, classname=f"{clinic.id}_doctors_bottom",
                bg="#f1feff", hasBorder=False,
                text=doctorNum, font=FONT, fg=BLACK,
                isDisabled=True, isJustified=True
            )
            clinicHours = self.controller.scrolledTextCreator(
                x=X+520, y=Y, width=200, height=80, root=R, classname=f"{clinic.id}_hours_bottom",
                bg="#f1feff", hasBorder=False,
                text=f"{clinic.clinicHrs}", font=("Inter", 12), fg=BLACK,
                isDisabled=True, isJustified=True
            )
            self.controller.buttonCreator(
                x=X+740, y=Y, classname=f"{clinic.id}_bottom_load", root=R,
                ipath="assets/BrowseClinic/Patient/BottomClickClinic.png",
                buttonFunction=lambda c=clinic: [
                    self.loadClinicAndViewDoctors(c)],
                isPlaced=True
            )
            COORDS = (
                COORDS[0], COORDS[1] + 100
            )

    def loadClinic(self, clinic: Clinic):
        self.loadedClinicFrame.grid()
        self.loadedClinicFrame.tkraise()
        self.viewedClinic = clinic
        self.backButton = self.controller.buttonCreator(
            x=20, y=20, classname="patient_loadedclinic_back", root=self.loadedClinicFrame,
            ipath="assets/BrowseClinic/Patient/BrowseSingleClinic/BackButton.png",
            buttonFunction=lambda: [self.loadedClinicFrame.grid_remove()]
        )
        self.loadCreateAppointmentRequestForm()
        img = self.controller.decodingBase64Data(clinic.clinicImg)
        self.viewedClinicTitle = self.controller.scrolledTextCreator(
            x=120, y=20, width=720, height=80, root=self.loadedClinicFrame, classname="patient_loadedclinic_title",
            bg="#dee8e0",
            text=f"Browsing Details of { clinic.name }", font=("Inter Bold", 24), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
        )
        self.clinicImage = self.controller.labelCreator(
            x=40, y=120, classname="patient_loadedclinic_image", root=self.loadedClinicFrame,
            ipath="assets/BrowseClinic/Patient/BrowseSingleClinic/ClinicImagePlaceholder.png",
        )
        self.controller.imageDict["patient_loadedclinic_image"] = ImageTk.PhotoImage(
            img
        )
        newImage = self.controller.imageDict["patient_loadedclinic_image"]
        self.clinicImage.configure(image=newImage, width=800, height=800)
        self.clinicImage.place(x=40, y=120, width=800, height=800)
        formatAddress = f"{clinic.address}, {clinic.zip}, {clinic.city}, {clinic.state.replace('_', ' ').title()}"
        self.clinicAddress = self.controller.scrolledTextCreator(
            x=160, y=950, width=660, height=100, root=self.loadedClinicFrame, classname="patient_loadedclinic_address",
            bg=WHITE, hasBorder=BLACK,
            text=formatAddress, font=("Inter Bold", 18), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )

    def loadCreateAppointmentRequestForm(self):
        self.formScrolledFrame = ScrolledFrame(
            master=self.loadedClinicFrame, width=720, height=1260, autohide=True, bootstyle="bg-rounded"
        )
        self.formScrolledFrame.place(x=900, y=120, width=720, height=900)
        clinic = self.viewedClinic
        FONT = ("Inter Medium", 12)
        R = self.formScrolledFrame
        PAR = "patient_appointment_request"
        Q1 = "Where would you like to have your consultation?"
        Q2 = "From what day/date would you prefer to have your consultation?"
        Q3 = "Between what time would you like to have your consultation?"
        Q4 = "Is there a particular speciality of doctor you would like to consult with?"
        Q5 = "Kindly provide a brief description of your status and current medical condition, as well as any specific symptoms you are experiencing. This information will help our healthcare professionals better understand your needs and ensure that you receive the most appropriate care during your appointment request."
        self.consultationLocationTitle = self.controller.scrolledTextCreator(
            x=0, y=0, width=720, height=40, root=R, classname=f"{PAR}_location_title",
            bg="#ecf2ff", hasBorder=False,
            text=Q1, font=FONT, fg=BLACK,
            isDisabled=True, isJustified=True
        )
        self.consultationLocationText = self.controller.scrolledTextCreator(
            x=180, y=40, width=520, height=120, root=R, classname=f"{PAR}_location_text",
            bg=WHITE, hasBorder=BLACK,
            text="", font=FONT, fg=BLACK,
            isDisabled=False, isJustified=True
        )
        self.whichLocation = IntVar()
        self.whichLocation.set(1)
        ADDLINE1 = self.user.addressLine1
        ADDLINE2 = self.user.addressLine2
        userLocation = f"{ADDLINE1 + ' ,' +ADDLINE2 if ADDLINE2 is not None else ADDLINE1}, {self.user.postcode}, {self.user.city}, {self.user.state.replace('_', ' ').title()}, {self.user.country}"
        clinicLocation = f"{clinic.name}, {clinic.address}, {clinic.zip}, {clinic.city}, {clinic.state.replace('_', ' ').title()}"
        self.consultationLocationText.text.insert(END, userLocation)
        self.consultationLocationText.text.config(state=DISABLED)
        self.setUseCurrentLocation = ttk.Checkbutton(
            master=self.formScrolledFrame, bootstyle="info-toolbutton",
            onvalue=1, offvalue=0, variable=self.whichLocation,
            text="Use my current location", cursor="hand2",
            command=lambda: [
                self.whichLocation.set(1),
                self.consultationLocationText.text.config(state=NORMAL),
                self.consultationLocationText.text.delete(1.0, END),
                self.consultationLocationText.text.insert(
                    END, userLocation
                ),
                self.consultationLocationText.text.config(state=DISABLED)
            ]
        )
        self.setUseCurrentLocation.place(x=0, y=40, width=180, height=40)
        self.setUseClinicLocation = ttk.Checkbutton(
            master=self.formScrolledFrame, bootstyle="success-toolbutton",
            onvalue=2, offvalue=0, variable=self.whichLocation,
            text="Use clinic location", cursor="hand2",
            command=lambda: [
                self.whichLocation.set(2),
                self.consultationLocationText.text.config(state=NORMAL),
                self.consultationLocationText.text.delete(1.0, END),
                self.consultationLocationText.text.insert(
                    END, clinicLocation
                ),
                self.consultationLocationText.text.config(state=DISABLED)
            ]
        )
        self.setUseClinicLocation.place(x=0, y=80, width=180, height=40)
        self.setUseCustomLocation = ttk.Checkbutton(
            master=self.formScrolledFrame, bootstyle="secondary-toolbutton",
            onvalue=3, offvalue=0, variable=self.whichLocation,
            text="Use custom location", cursor="hand2",
            command=lambda: [
                self.whichLocation.set(3),
                self.consultationLocationText.text.config(state=NORMAL),
                self.consultationLocationText.text.delete(1.0, END),
            ]
        )
        self.setUseCustomLocation.place(x=0, y=120, width=180, height=40)
        self.consultationDateTitle = self.controller.scrolledTextCreator(
            x=0, y=180, width=720, height=60, root=R, classname=f"{PAR}_date_title",
            bg="#ecf2ff", hasBorder=False,
            text=Q2, font=FONT, fg=BLACK,
            isDisabled=True, isJustified=True
        )
        self.consultationDatePickerBtn = self.controller.buttonCreator(
            x=0, y=240, classname=f"{PAR}_date_picker", root=R,
            ipath="assets/BrowseClinic/Patient/BrowseSingleClinic/WideCalendarTimePicker.png",
            buttonFunction=lambda: [
                self.loadDatePicker(self.consultationDateText.text)
            ],
            isPlaced=True
        )
        self.consultationDateText = self.controller.scrolledTextCreator(
            x=180, y=240, width=520, height=100, root=R, classname=f"{PAR}_date_text",
            bg=WHITE, hasBorder=BLACK,
            text="", font=FONT, fg=BLACK,
            isDisabled=False, isJustified=True, 
        )
        self.consultationDateText.text.insert(END, "Choose a date")
        self.consultationDateText.text.config(state=DISABLED)
        self.consultationTimeTitle = self.controller.scrolledTextCreator(
            x=0, y=360, width=720, height=60, root=R, classname=f"{PAR}_time_title",
            bg="#ecf2ff", hasBorder=False,
            text=Q3, font=FONT, fg=BLACK,
            isDisabled=True, isJustified=True
        )
        self.consultationStartTimeText = self.controller.scrolledTextCreator(
            x=0, y=420, width=180, height=60, root=R, classname=f"{PAR}_start_time_text",
            bg="#78aeff",
            text="Start Time", font=FONT, fg=WHITE,
            isDisabled=True, isJustified=True,
            hasVbar=False
        )
        self.consultationEndTimeText = self.controller.scrolledTextCreator(
            x=0, y=480, width=180, height=60, root=R, classname=f"{PAR}_end_time_text",
            bg="#ffb3bd",
            text="End Time", font=FONT, fg=WHITE,
            isDisabled=True, isJustified=True,
            hasVbar=False
        )
        # TODO: Add time picker
        self.consultationPreferredSpecialityTitle = self.controller.scrolledTextCreator(
            x=0, y=560, width=720, height=60, root=R, classname=f"{PAR}_speciality_title",
            bg="#ecf2ff", hasBorder=False,
            text=Q4, font=FONT, fg=BLACK,
            isDisabled=True, isJustified=True,
        )
        self.consultationPreferredSpecialityText = self.controller.scrolledTextCreator(
            x=0, y=620, width=700, height=120, root=R, classname=f"{PAR}_speciality_text",
            bg=WHITE, hasBorder=BLACK,
            text="", font=FONT, fg=BLACK,
            isDisabled=False, isJustified=True, justification="left"
        )
        self.consultationPurposeTitle = self.controller.scrolledTextCreator(
            x=0, y=760, width=720, height=180, root=R, classname=f"{PAR}_purpose_title",
            bg="#ecf2ff", hasBorder=False,
            text=Q5, font=FONT, fg=BLACK,
            isDisabled=True, isJustified=True
        )
        self.consultationPurposeText = self.controller.scrolledTextCreator(
            x=0, y=940, width=700, height=180, root=R, classname=f"{PAR}_purpose_text",
            bg=WHITE, hasBorder=BLACK,
            text="", font=FONT, fg=BLACK,
            isDisabled=False, isJustified=True, justification="left",
        )
        self.requestSubmitButton = self.controller.buttonCreator(
            x=40, y=1140, classname=f"{PAR}_submit", root=R,
            ipath="assets/BrowseClinic/Patient/BrowseSingleClinic/TermsButton.png",
            buttonFunction=lambda: [
                self.submitAppointmentRequest()
            ],
            isPlaced=True
        )

    def loadDatePicker(self, text: Text):
        dialog = DatePickerDialog(
            parent=self.consultationDatePickerBtn, title="Select Date", firstweekday=0, startdate=datetime.now(),
        )
        if dialog.date_selected is None:
            return
        self.dateTimeDOB = dialog.date_selected
        date = dialog.date_selected.strftime("%d/%m/%Y")
        text.configure(state=NORMAL)
        text.delete(1.0, END)
        text.insert(END, date)
        text.configure(state=DISABLED)

    def createEntry(self):
        CREATOR = self.controller.ttkEntryCreator
        self.searchEntry = CREATOR(
            x=20, y=80,
            width=760, height=80,
            classname="searchentry", root=self,
            placeholder="Search for clinics"
        )

    def createFormEntries(self):
        CREATOR = self.controller.ttkEntryCreator
        FONT = ("Inter", 16)

    def createbutton(self):
        def update_map_location():
            new_address = self.patientBrowserSelectAddress.get()
            self.clinicsMap.set_address(new_address)

        self.submitButton = self.controller.buttonCreator(
            ipath="assets/Dashboard/PatientAssets/PatientBrowseClinicSearchButton.png",
            x=780, y=80, classname="PatientSetLocation", root=self,
            buttonFunction=update_map_location  
        )

