from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from views.registration import RegistrationPage

from datetime import datetime
from resource.basewindow import ElementCreator, gridGenerator
from resource.static import *
from tkinter import *

from ttkbootstrap.constants import *


class DoctorRegistrationForm(Frame):
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

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Registration/Doctor/DoctorSignUpForm.png",
            x=0, y=0, classname="secondarypanelbg", root=self
        )
        self.createLabels()
        self.createButtons()

    def createLabels(self):
        self.roleImg = self.controller.labelCreator(
            ipath="assets/Registration/DoctorFormButton.png",
            x=60, y=880, classname="roleimg", root=self.parent,
        )

    def createButtons(self):
        OPT1STR = "Employment History"
        OPT2STR = "Education History"
        OPT3STR = "Specialization"
        OPT4STR = "Other Information"
        optList = [OPT1STR, OPT2STR, OPT3STR, OPT4STR]
        # creating a button arrangement of two per row
        # iterates over the list of options and creates a button for each
        for i, option in enumerate(optList):
            x = 40 if i % 2 == 0 else 420
            y = 120 + (i // 2) * 120
            self.controller.textElement(
                ipath="assets/Registration/Patient/PatientButtonOptionBg.png",
                x=x, y=y, classname="formoption" + str(i + 1), root=self,
                text=option, size=20, font=INTER,
                buttonFunction=lambda o=option: self.loadSpecificSubmission(o)
            )
        self.completeRegBtn = self.controller.buttonCreator(
            ipath="assets/Registration/CompleteRegButton.png",
            x=1420, y=880, classname="completeregbutton", root=self.parent,
            buttonFunction=lambda: self.confirmSubmission()
        )

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
        doctor = prisma.doctor.create(
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
            }
        )
