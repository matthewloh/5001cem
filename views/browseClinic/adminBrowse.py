from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.dashboard.adminDashboard import ClinicAdminDashboard
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


class AdminBrowseClinic(Frame):
    def __init__(self, parent: ClinicAdminDashboard = None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="browseclinicpanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.user = self.parent.user
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.createButtons()
        self.createVars()
        self.loadSpecificSubmission()
        self.loadClinicInformation()
        self.createClinicInfoEntries()
        self.loadClinicHoursMenu()
        self.validateDateVars()
        self.loadClinicInformationInput()
        self.saveClinicInformation()
        self.loadCloseAndSaveButtons()

    def createFrames(self):
        pass

    def createElements(self):
        self.bg = self.controller.labelCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/ManageClinic/ManageClinicBg.png",
            x=0, y=0, classname="manageclinicbg", root=self
        )
    
    def createButtons(self):
        self.closebutton = self.controller.buttonCreator(
            ipath="assets/Registration/Close.png", x=100, y=820,
            classname="reg_closebutton", root=self,
            buttonFunction=lambda: [print('remain')]
        )
        self.savebutton = self.controller.buttonCreator(
            ipath="assets/Registration/Save.png", x=400, y=820,
            classname="reg_savebutton", root=self,
            buttonFunction=lambda: [print('test')]
        )
        
    def createVars(self):
        self.clinicnameVar = StringVar()
        self.clinicaddressVar = StringVar()
        self.cliniccityVar = StringVar()
        self.clinicStateVar = StringVar()
        self.cliniczipVar = StringVar()
        self.cliniccontactnumberVar = StringVar()
        self.clinichrsVar = StringVar()

    def loadSpecificSubmission(self, option: str):
        if option == self.OPT1STR:
            self.loadClinicInformation(option)
        elif option == self.OPT2STR:
            self.loadUploadClinicImage(option)
        elif option == self.OPT3STR:
            self.loadManageDoctors(option)
        elif option == self.OPT4STR:
            self.loadOtherInformation(option)

    def loadClinicInformation(self, option: str):
        frame = self.inputframe
        self.inputframe.grid()
        self.inputframe.tkraise()
        for widgetname, widget in self.inputframe.children.items():
            if widgetname in ["padoption", "thumbnailoption", "fitoption", "uploadclinicimg"]:
                widget.grid_remove()
            elif widgetname in ["imgplaceholder"]:
                widget.place_forget()
            elif widgetname.endswith("hostfr"):
                widget.grid()
                widget.tkraise()
        infolabel = self.controller.textElement(
            ipath="assets/Registration/InputFormTextBG.png", x=0, y=0,
            classname="inputformtext", root=frame, text=f"Input your {option} here",
            size=30, font=INTER
        )
        bg = self.controller.labelCreator(
            ipath="assets/Registration/Admin/ClinicInfoLabelBg.png", x=0, y=80,
            classname="clinicinfobg", root=frame
        )
        bg.tk.call("lower", bg._w)
        vars = [self.clinicnameVar, self.clinicaddressVar, self.cliniccityVar,
                self.clinicStateVar, self.cliniczipVar, self.cliniccontactnumberVar
                ]
        if any([var.get() != "" for var in vars]):
            self.loadClinicInformationInput()
        else:
            self.createClinicInfoEntries(frame)

        self.savebutton.config(
            command=lambda: [
                self.saveClinicInformation()]
        )
        self.loadCloseAndSaveButtons()

    
    def createClinicInfoEntries(self):
        CREATOR = self.controller.ttkEntryCreator
        X, Y, W, H, R, CN, PH = "x", "y", "width", "height", "root", "classname", "placeholder"
        param = {
            "clinicname": {
                X: 40,
                Y: 40,
                W: 640,
                H: 80,
                CN: "clinicnameentry",
                R: self,
                PH: "Clinic Name"
            },
            "clinicaddress": {
                X: 40,
                Y: 160,
                W: 640,
                H: 80,
                CN: "clinicaddressentry",
                R: self,
                PH: "Clinic Address"
            },
            "cliniccontactnumber": {
                X: 40,
                Y: 280,
                W: 300,
                H: 80,
                CN: "cliniccontactnumberentry",
                R: self,
                PH: "Clinic Contact Number"
            },
            "cliniccity": {
                X: 380,
                Y: 280,
                W: 300,
                H: 80,
                CN: "cliniccityentry",
                R: self,
                PH: "Clinic City"
            },
            "cliniczip": {
                X: 380,
                Y: 400,
                W: 300,
                H: 80,
                CN: "cliniczipentry",
                R: self,
                PH: "Clinic Zip"
            },
        }
        for p in param:
            CREATOR(**param[p])
        self.clinicStateVar = StringVar()
        states = list(states_dict.keys())
        self.menuframe = self.controller.frameCreator(
            x=40, y=400, framewidth=300, frameheight=80,
            bg=WHITE, classname="clinicstateframe", root=self
        )
        self.clinicStateMenu = self.controller.menubuttonCreator(
            x=0, y=0, width=300, height=80,
            root=self.menuframe, classname="reg_clinicstate",
            text=f"State", listofvalues=states,
            variable=self.clinicStateVar, font=("Helvetica", 12),
            command=lambda:
                ToastNotification(title="Success", bootstyle="success", duration=3000,
                                  message=f"State Selected: {self.clinicStateVar.get()}").show_toast()
        )
        self.startTimeVar = StringVar()
        self.startTimeVar.set("12:00AM")
        self.endTimeVar = StringVar()
        self.endTimeVar.set("12:00PM")
        self.loadClinicHoursMenu()

    def loadClinicHoursMenu(self):
        start_time = datetime.strptime("12:00AM", HUMANTIME)
        end_time = datetime.strptime("12:00PM", HUMANTIME)
        time_slots = [start_time +
                      timedelta(minutes=30 * i) for i in range(24 * 2)]
        time_slots_str = [ts.strftime(HUMANTIME) for ts in time_slots]
        self.startTimeHostFrame = self.controller.frameCreator(
            x=80, y=600, framewidth=240, frameheight=80,
            bg=WHITE, classname="starttimehostfr", root=self.inputframe
        )
        self.startTimeMenu = self.controller.menubuttonCreator(
            x=0, y=0, width=240, height=80, root=self.startTimeHostFrame,
            classname="reg_clinichrs", text="Start Time", listofvalues=time_slots_str,
            variable=self.startTimeVar, font=("Helvetica", 12),
            command=lambda:
            [self.validateDateVars()],
        )
        self.endTimeHostFrame = self.controller.frameCreator(
            x=400, y=600, framewidth=240, frameheight=80,
            bg=WHITE, classname="endtimehostfr", root=self.inputframe
        )
        self.endTimeMenu = self.controller.menubuttonCreator(
            x=0, y=0, width=240, height=80, root=self.endTimeHostFrame,
            classname="reg_clinichrs", text="End Time", listofvalues=time_slots_str,
            variable=self.endTimeVar, font=("Helvetica", 12),
            command=lambda:
                [self.validateDateVars()]
        )
        self.startTimeMenu.config(text=self.startTimeVar.get())
        self.endTimeMenu.config(text=self.endTimeVar.get())

    def validateDateVars(self):
        start = datetime.strptime(self.startTimeVar.get(), HUMANTIME)
        end = datetime.strptime(self.endTimeVar.get(), HUMANTIME)
        diff = timedelta(hours=end.hour, minutes=end.minute) - \
            timedelta(hours=start.hour, minutes=start.minute)
        # TODO: add validation for clinic hours
        self.clinichrsVar.set(
            f"{self.startTimeVar.get()} - {self.endTimeVar.get()}")

    def loadClinicInformationInput(self):
        WD = self.controller.widgetsDict
        WD["clinicnameentry"].delete(0, END)
        WD["clinicaddressentry"].delete(0, END)
        WD["cliniccontactnumberentry"].delete(0, END)
        self.menuframe.grid()
        self.menuframe.tkraise()
        self.clinicStateMenu.config(text=self.clinicStateVar.get())
        WD["cliniccityentry"].delete(0, END)
        WD["cliniczipentry"].delete(0, END)
        WD["clinicnameentry"].insert(0, self.clinicnameVar.get())
        WD["clinicaddressentry"].insert(0, self.clinicaddressVar.get())
        WD["cliniccontactnumberentry"].insert(
            0, self.cliniccontactnumberVar.get())
        WD["cliniccityentry"].insert(0, self.cliniccityVar.get())
        self.clinicStateMenu.config(text=self.clinicStateVar.get())
        WD["cliniczipentry"].insert(0, self.cliniczipVar.get())
        self.startTimeMenu.config(text=self.startTimeVar.get())
        self.endTimeMenu.config(text=self.endTimeVar.get())

    def saveClinicInformation(self):
        prisma = self.prisma
        WD = self.controller.widgetsDict
        self.clinicnameVar.set(
            WD["clinicnameentry"].get())
        self.clinicaddressVar.set(
            WD["clinicaddressentry"].get())
        self.cliniccontactnumberVar.set(
            WD["cliniccontactnumberentry"].get())
        self.cliniccityVar.set(
            WD["cliniccityentry"].get())
        self.cliniczipVar.set(
            WD["cliniczipentry"].get())
        self.clinichrsVar.set(
            f"{self.startTimeVar.get()} - {self.endTimeVar.get()}")

        msg = f"""
        Clinic Information Saved!
        Name: {self.clinicnameVar.get()}
        Address: {self.clinicaddressVar.get()}
        Contact Number: {self.cliniccontactnumberVar.get()}
        City: {self.cliniccityVar.get()}
        State: {self.clinicStateVar.get()}
        Zip: {self.cliniczipVar.get()} 
        Hours: {self.clinichrsVar.get()}
        """
        Messagebox.show_info(
            title="Clinic Information",
            message=msg,
            parent=self.inputframe
        )

    def loadCloseAndSaveButtons(self):
        self.closebutton.grid()
        self.savebutton.grid()
        self.closebutton.tkraise()
        self.savebutton.tkraise()
    
   