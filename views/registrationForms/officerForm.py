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
from prisma.errors import RecordNotFoundError
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
            buttonFunction=lambda: self.confirmSubmission() if self.validateOfficerInfo() else None
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
        WD["startofdutyentry"].configure(state=READONLY, foreground=BLACK)
        WD["endofdutyentry"].configure(state=READONLY, foreground=BLACK)
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
        if int(date.split("/")[2]) < 2018:
            messagebox.showerror("Invalid Year", "Please select a year after 2018")
            return
        entry.configure(state="normal")
        entry.delete(0, END)
        entry.insert(0, date)
        entry.configure(foreground=BLACK)
        entry.configure(state=READONLY)

    #validate officer info
    def validateOfficerInfo(self):
        WD = self.controller.widgetsDict
        if WD["grdidentry"].get() == "Enter your GRD ID":
            messagebox.showerror("Error", "Please enter your GRD ID")
            return False
        elif self.jurisdictionState.get() == "":
            messagebox.showerror("Error", "Please select a state of jurisdiction")
            return False
        elif WD["startofdutyentry"].get() == "Select Start of Duty" or WD["endofdutyentry"].get() == "Select End of Duty":
            messagebox.showerror("Error", "Please select a date of duty")
            return False
        startDate = datetime.strptime(WD["startofdutyentry"].get(), "%d/%m/%Y")
        endDate = datetime.strptime(WD["endofdutyentry"].get(), "%d/%m/%Y")
        if startDate == endDate:
            messagebox.showerror("Error", "Start and end date cannot be the same")
            return False
        elif startDate > endDate:
            messagebox.showerror("Error", "Please select a valid start date and end date")
            return False
        return True
        

    def confirmSubmission(self):
        try:
            prisma = self.prisma
            WD = self.controller.widgetsDict
            # get the values from the entry boxes
            self.country, self.state, self.city = self.parent.country.get(
            ), self.parent.state.get(), self.parent.city.get()
            dateStr = self.parent.dateOfBirthEntry.get()  # "%d/%m/%Y"
            # datetimeObj
            dateObj = datetime.strptime(dateStr, "%d/%m/%Y")
            UTC = timezone("UTC")
            KL = timezone("Asia/Kuala_Lumpur")
            try:
                govRegSystem = prisma.govregsystem.find_first_or_raise(
                    where={
                        "state": self.jurisdictionState.get().upper().replace(" ", "_"),
                    }
                )
            except RecordNotFoundError:
                govRegSystem = prisma.govregsystem.create(
                    data={
                        "state": self.jurisdictionState.get().upper().replace(" ", "_"),
                    }
                )
            officer = prisma.govhealthofficer.create(
                data={
                    "user": {
                        "create": {
                            "fullName": self.parent.fullname.get(),
                            "email": self.parent.email.get(),
                            "nric_passport": self.parent.nric_passno.get(),
                            "dateOfBirth": dateObj,
                            "contactNo": self.parent.contactnumber.get(),
                            "password": self.parent.encryptPassword(self.parent.password.get()),
                            "race": self.parent.race.get().upper().replace(" ", "_"),
                            "gender": self.parent.gender.get().upper().replace(" ", "_"),
                            "countryOfOrigin": self.parent.countryoforigin.get(),
                            "addressLine1": self.parent.addressline1.get(),
                            "addressLine2": self.parent.addressline2.get(),
                            "postcode": self.parent.postcode.get(),
                            "city": self.city,
                            "state": self.state,
                            "country": self.country,
                        }
                    },
                    "govRegId": WD["grdidentry"].get(),
                    "startDate": KL.convert(
                        datetime.strptime(WD["startofdutyentry"].get(), "%d/%m/%Y")
                    ),
                    "endDate": KL.convert(
                        datetime.strptime(WD["endofdutyentry"].get(), "%d/%m/%Y")
                    ),
                    "systemSupervising": {
                        "connect": {
                            "id": govRegSystem.id
                        }
                    }
                }
            )
            toast = ToastNotification("Registration", f"{officer.user.fullName} has been registered as a government health officer", duration=3000, bootstyle="success").show_toast()
            self.parent.loadSignIn()
        except Exception as e:
            print(e)
            messagebox.showerror("Error", "Please make sure all fields are filled in correctly.")
            return
            