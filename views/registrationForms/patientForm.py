from __future__ import annotations
from datetime import datetime
from tkinter import messagebox
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from ttkbootstrap.toast import ToastNotification
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
        self.OPT5STR = "Input Height, Weight\nand Blood Type"
        optList = [self.OPT1STR, self.OPT2STR, self.OPT3STR,
                   self.OPT4STR, self.OPT5STR]
        # creating a button arrangement of two per row
        # iterates over the list of options and creates a button for each
        for i, option in enumerate(optList):
            x = 40 if i % 2 == 0 else 420
            y = 120 + (i // 2) * 120
            self.controller.textElement(
                ipath="assets/Registration/Patient/PatientButtonOptionBg.png",
                x=x, y=y, classname="formoption" + str(i + 1), root=self,
                text=option, size=20, font=INTER,
                buttonFunction=lambda o=option: self.loadInputForOption(o),
                yIndex=-2/3 if i == 5 else 0
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
        self.weight = DoubleVar()
        self.height = DoubleVar()
        self.bloodType = StringVar()

    def loadInputForOption(self, option: str):
        if option == self.OPT5STR:
            # Ask user to input height and weight
            self.inputframe.grid()
            self.inputframe.tkraise()
            self.loadInfoLabel(option)
            self.controller.buttonCreator(
                ipath="assets/Registration/Patient/Back.png", x=640, y=10,
                classname="reg_backbutton", root=self.inputframe,
                buttonFunction=lambda: [self.inputframe.grid_remove(),
                                        self.entriesFrame.grid_remove()],
                isPlaced=True
            )
            self.entriesFrame = self.controller.frameCreator(
                x=0, y=80, framewidth=720, frameheight=700,
                bg=WHITE, classname="weightheightbloodtypeframe", root=self.inputframe
            )
            PHWEIGHT = "Enter your weight in kg"
            PHHEIGHT = "Enter your height in cm"
            self.entriesFrame.tkraise()
            self.entriesframebg = self.controller.labelCreator(
                x=0, y=0, classname="weightheightbloodtypeframebg", root=self.entriesFrame,
                ipath="assets/Registration/Patient/WeightHeightBloodTypeBG.png"
            )
            self.weightEntry = self.controller.ttkEntryCreator(
                x=160, y=80, width=400, height=80,
                classname="weightentry", root=self.entriesFrame,
                placeholder=PHWEIGHT
            )
            self.heightEntry = self.controller.ttkEntryCreator(
                x=160, y=220, width=400, height=80,
                classname="heightentry", root=self.entriesFrame,
                placeholder=PHHEIGHT
            )
            bloodTypes = [
                "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"
            ]
            self.bloodTypeVar = StringVar()
            self.controller.menubuttonCreator(
                x=160, y=360, width=400, height=80,
                root=self.entriesFrame, classname="bloodtypemenubutton",
                text="Select your blood type", listofvalues=bloodTypes,
                variable=self.bloodTypeVar, font=("Helvetica", 16),
                command=lambda: [
                    ToastNotification(title="Saved", bootstyle="success", duration=3000,
                                      message=f"Saved {self.bloodTypeVar.get()}").show_toast()
                ]
            )
            self.saveForWHB = self.controller.buttonCreator(
                ipath="assets/Registration/Patient/WeightHeightBloodSave.png",
                x=280, y=560, classname="weightheightbloodtypesavebutton",
                root=self.entriesFrame,
                buttonFunction=lambda: [
                    self.validateSaveWeightHeightBloodType(),
                ]
            )
            return
        self.loadInfoLabel(option)
        self.createEditText()
        if self.vars[option].get() != "":
            self.inputTextSpace.insert("1.0", self.vars[option].get())
        self.configSaveClearButtons(option)

    def validateSaveWeightHeightBloodType(self):
        try:
            weightFormatted = self.weightEntry.get().replace(" ", "").replace("kg", "")
            float(weightFormatted)
            heightFormatted = self.heightEntry.get().replace(" ", "").replace("cm", "")
            float(heightFormatted)
        except ValueError:
            messagebox.showerror(
                title="Invalid Input", message="Please enter a valid number for weight and height")
            return
        if self.bloodTypeVar.get() == "":
            messagebox.showerror(
                title="Invalid Input", message="Please select a blood type")
            return
        self.weight.set(float(weightFormatted))
        self.height.set(float(heightFormatted))
        self.bloodType.set(self.bloodTypeVar.get())
        messagebox.showinfo(
            title="Saved", message="Saved weight, height and blood type"),
        self.entriesFrame.grid_remove(),
        self.inputframe.grid_remove()

    def configSaveClearButtons(self, option: str):
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
                self.vars[option].set(
                    self.inputTextSpace.get("1.0", "end-1c")),
                ToastNotification(title="Saved", bootstyle="success", duration=3000,
                                  message=f"Saved {option}").show_toast()
            ]
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
            size=30, font=INTER,
            yIndex=-2/3 if option == self.OPT5STR else 0
        )

    def confirmSubmission(self):
        prisma = self.prisma
        self.country, self.state, self.city = self.parent.country.get(
        ), self.parent.state.get(), self.parent.city.get()
        dateStr = self.parent.dateOfBirthEntry.get()  # "%d/%m/%Y"
        # datetimeObj
        dateObj = datetime.strptime(dateStr, "%d/%m/%Y")
        patient = prisma.patient.create(
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
                "healthRecord": {
                    "create": {
                        "allergies": self.vars[self.OPT3STR].get(),
                        "bloodType": self.bloodType.get(),
                        "height": self.height.get(),
                        "weight": self.weight.get(),
                        "currentMedication": self.vars[self.OPT2STR].get(),
                        "pastMedication": self.vars[self.OPT1STR].get(),
                        "pastSurgery": self.vars[self.OPT5STR].get(),
                        "familyHistory": self.vars[self.OPT4STR].get(),
                    }
                }
            }
        )
