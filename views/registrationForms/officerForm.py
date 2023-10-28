from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.registration import RegistrationPage
import calendar
import re
import threading
from tkinter import *
from views.citystatesdict import states_dict
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


class OfficerRegistrationForm(Frame):
    def __init__(self, parent: RegistrationPage = None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1,
                         bg="#dee8e0", name="roleregistrationform")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 40, 46, "#dee8e0")
        self.grid(row=4, column=28, columnspan=40, rowspan=46, sticky=NSEW)

        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()

    def createFrames(self):
        pass

    def createLabels(self):
        self.roleImg = self.controller.labelCreator(
            ipath="assets/Registration/OfficerFormButton.png",
            x=60, y=880, classname="roleimg", root=self.parent,
        )

    def initializeFormVars(self):
        self.vars = {k: StringVar() for k in self.optList}

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Registration/Officer/OfficerSignUpForm.png",
            x=0, y=0, classname="secondarypanelbg", root=self
        )
        self.createLabels()
        self.createButtons()
        self.createEntries()
        self.initializeFormVars()

    def createButtons(self):
        self.completeRegBtn = self.controller.buttonCreator(
            ipath="assets/Registration/CompleteRegButton.png",
            x=1420, y=880, classname="completeregbutton", root=self.parent,
            buttonFunction=lambda: self.confirmSubmission()
        )

    def createEntries(self):
        self.OPT1STR = "Government Registered Doctor ID"
        self.OPT2STR = "Area of Jurisdiction"
        self.OPT3STR = "Start of Duty"
        self.OPT4STR = "End of Duty"
        self.optList = [self.OPT1STR, self.OPT2STR, self.OPT3STR, self.OPT4STR]
        X, Y, W, H, R, CN, PH = "x", "y", "width", "height", "root", "classname", "placeholder"
        statelist = list(states_dict.keys())
        ENTCREATOR = self.controller.ttkEntryCreator
        param = {
            self.OPT1STR: {
                X: 340,
                Y: 100,
                W: 420,
                H: 60,
                CN: "grdidentry",
                R: self,
                PH: "Enter your GRD ID",
            },
            "startOfDuty": {
                X: 340,
                Y: 300,
                W: 360,
                H: 60,
                CN: "startofdutyentry",
                R: self,
                PH: "Select Start of Duty",
            },
            "endOfDuty": {
                X: 340,
                Y: 400,
                W: 360,
                H: 60,
                CN: "endofdutyentry",
                R: self,
                PH: "Select End of Duty",
            }
        }
        for p in param:
            ENTCREATOR(**param[p])
        WD = self.controller.widgetsDict
        self.jurisdictionState = StringVar()
        self.controller.menubuttonCreator(
            x=340, y=200, width=420, height=60,
            root=self, classname="stateofjurisdiction",
            text=f"Please Select State", listofvalues=statelist,
            variable=self.jurisdictionState, font=("Helvetica", 12),
            command=lambda: [None]
        )

        self.startDatePicker = self.controller.buttonCreator(
            ipath="assets/Registration/DatePicker.png",
            x=700, y=300, classname="datepicker_start", root=self,
            buttonFunction=lambda: self.selectDate(
                self.startDatePicker, WD["startofdutyentry"])
        )
        self.endDatePicker = self.controller.buttonCreator(
            ipath="assets/Registration/DatePicker.png",
            x=700, y=400, classname="datepicker_end", root=self,
            buttonFunction=lambda: self.selectDate(
                self.endDatePicker, WD["endofdutyentry"])
        )

    def selectDate(self, button: Button, entry: Entry):
        dialog = DatePickerDialog(
            parent=button, title="Select Date",
            firstweekday=0,
            startdate=dt.date.today(),
        )
        if dialog.date_selected is None:
            return
        date = dialog.date_selected.strftime("%d/%m/%Y")
        entry.configure(state="normal")
        entry.delete(0, END)
        entry.insert(0, date)

    def loadSpecificSubmission(self, option: str):
        print(option)

    def confirmSubmission(self):
        prisma = self.prisma
        WD = self.controller.widgetsDict
        # get the values from the entry boxes
        entries = (WD["regfullname"], WD["regemail"], WD["regnric"],
                   WD["regrace"], WD["regcontactnumber"], WD["countryoforigin"],
                   WD["regpassent"], WD["regconfpassent"], WD["regaddressline1"],
                   WD["regaddressline2"], WD["regpostcode"])
        self.country, self.state, self.city = self.parent.country.get(
        ), self.parent.state.get(), self.parent.city.get()
        dateStr = self.parent.dateOfBirthEntry.get()  # "%d/%m/%Y"
        # datetimeObj
        dateObj = datetime.strptime(dateStr, "%d/%m/%Y")
        UTC = timezone("UTC")
        KL = timezone("Asia/Kuala_Lumpur")
        officer = prisma.govhealthofficer.create(
            data={
                "user": {
                    "create": {
                        "fullName": entries[0].get(),
                        "email": entries[1].get(),
                        "nric_passport": entries[2].get(),
                        "dateOfBirth": dateObj,
                        "contactNo": entries[4].get(),
                        "password": self.parent.encryptPassword(entries[6].get()),
                        "race": entries[3].get(),
                        "countryOfOrigin": WD["countryoforigin"].get(),
                        "addressLine1": WD["regaddressline1"].get(),
                        "addressLine2": WD["regaddressline2"].get(),
                        "postcode": WD["regpostcode"].get(),
                        "city": self.city,
                        "state": self.state,
                        "country": self.country,
                    }
                },
                "govRegId": WD["grdidentry"].get(),
                "stateManaged": self.jurisdictionState.get().upper().replace(" ", "_"),
                "startDate": KL.convert(
                    datetime.strptime(WD["startofdutyentry"].get(), "%d/%m/%Y")
                ),
                "endDate": KL.convert(
                    datetime.strptime(WD["endofdutyentry"].get(), "%d/%m/%Y")
                )
            }
        )
