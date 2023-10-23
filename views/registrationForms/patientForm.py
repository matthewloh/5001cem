from __future__ import annotations

from datetime import datetime
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from resource.basewindow import ElementCreator, gridGenerator
from resource.static import *
from tkinter import *
from typing import TYPE_CHECKING

from ttkbootstrap.constants import *

if TYPE_CHECKING:
    from views.registration import RegistrationPage


class PatientRegistrationForm(Frame):
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
        self.inputframe = self.controller.frameCreator(
            x=40, y=100, framewidth=720, frameheight=780,
            bg=WHITE, classname="inputframe", root=self
        )
        self.inputframe.grid_remove()

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Registration/Patient/PatientSignUpForm.png",
            x=0, y=0, classname="secondarypanelbg", root=self
        )
        self.createLabels()
        self.createButtons()
        self.initializeFormVars()

    def createLabels(self):
        self.roleImg = self.controller.labelCreator(
            ipath="assets/Registration/PatientFormButton.png",
            x=60, y=880, classname="roleimg", root=self.parent,
        )

    def createButtons(self):
        self.OPT1STR = "Existing Health Records"
        self.OPT2STR = "Current Medications"
        self.OPT3STR = "Allergies"
        self.OPT4STR = "Family History"
        self.OPT5STR = "Additional Biodata(eg. Past Surgeries)"
        self.OPT6STR = "Input Height, Weight and Blood Type"
        optList = [self.OPT1STR, self.OPT2STR, self.OPT3STR,
                   self.OPT4STR, self.OPT5STR, self.OPT6STR]
        # creating a button arrangement of two per row
        # iterates over the list of options and creates a button for each
        for i, option in enumerate(optList):
            x = 40 if i % 2 == 0 else 420
            y = 120 + (i // 2) * 120
            self.controller.textElement(
                ipath="assets/Registration/Patient/PatientButtonOptionBg.png",
                x=x, y=y, classname="formoption" + str(i + 1), root=self,
                text=option, size=20, font=INTER,
                buttonFunction=lambda o=option: self.loadInputForOption(o)
            )
        self.completeRegBtn = self.controller.buttonCreator(
            ipath="assets/Registration/CompleteRegButton.png",
            x=1420, y=880, classname="completeregbutton", root=self.parent,
            buttonFunction=lambda: self.confirmSubmission()
        )

    def initializeFormVars(self):
        self.vars = {
            self.OPT1STR: StringVar(),
            self.OPT2STR: StringVar(),
            self.OPT3STR: StringVar(),
            self.OPT4STR: StringVar(),
            self.OPT5STR: StringVar(),
        }

    def loadInputForOption(self, option):
        if option == self.OPT6STR:
            # Ask user to input height and weight
            self.weight = Querybox.get_float(
                title="Input Weight", prompt="Input your weight in kg",
                initialvalue=0, minvalue=0, maxvalue=200, parent=self.controller.widgetsDict["formoption6"]
            )
            self.height = Querybox.get_float(
                title="Input Height", prompt="Input your height in cm",
                initialvalue=0, minvalue=0, maxvalue=300, parent=self.controller.widgetsDict["formoption6"]
            )
            # Ask user to input blood type
            self.bloodType = Querybox.get_string(
                title="Input Blood Type", prompt="Input your blood type",
                initialvalue="O+", parent=self.controller.widgetsDict["formoption6"]
            )
            return
        self.loadInfoLabel(option)
        self.createEditText()
        if self.vars[option].get() != "":
            self.inputTextSpace.insert("1.0", self.vars[option].get())
        self.configSaveClearButtons(option)

    def configSaveClearButtons(self, option):
        BUTTONCREATOR = self.controller.buttonCreator

        BUTTONCREATOR(
            ipath="assets/Registration/Patient/Back.png", x=640, y=10,
            classname="reg_backbutton", root=self.inputframe,
            buttonFunction=lambda: [self.inputframe.grid_remove()],
            isPlaced=True
        )
        BUTTONCREATOR(
            ipath="assets/Registration/Patient/ClearText.png", x=100, y=680,
            classname="reg_cleartextbutton", root=self.inputframe,
            buttonFunction=lambda: [self.inputTextSpace.delete("1.0", END)],
        )
        BUTTONCREATOR(
            ipath="assets/Registration/Patient/SaveText.png", x=400, y=680,
            classname="reg_savetext", root=self.inputframe,
            buttonFunction=lambda: [
                self.vars[option].set(self.inputTextSpace.get("1.0", "end-1c"))],
        )

    def createEditText(self):
        self.inputText = ScrolledText(
            master=self.inputframe, width=520, height=520, padding=0,
            bootstyle="success-round", autohide=True)
        self.inputText.place(x=100, y=140, width=520, height=520)
        self.inputTextSpace = self.inputText.text
        self.inputTextSpace.config(font=("Inter", 20), fg=BLACK)

    def loadInfoLabel(self, option):
        self.inputframe.grid()
        self.inputframe.tkraise()
        infolabel = self.controller.textElement(
            ipath="assets/Registration/InputFormTextBG.png", x=0, y=0,
            classname="inputformtext", root=self.inputframe, text=f"Input your {option} here",
            size=30, font=INTER
        )

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
        patient = prisma.patient.create(
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
                "healthRecord": {
                    "create": {
                        "allergies": self.vars[self.OPT3STR].get(),
                        "bloodType": self.bloodType,
                        "height": float(self.height),
                        "weight": float(self.weight),
                        "currentMedication": self.vars[self.OPT2STR].get(),
                        "pastMedication": self.vars[self.OPT1STR].get(),
                        "pastSurgery": self.vars[self.OPT5STR].get(),
                        "familyHistory": self.vars[self.OPT4STR].get(),
                    }
                }
            }
        )
