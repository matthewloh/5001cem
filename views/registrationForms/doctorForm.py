from __future__ import annotations
from tkinter import messagebox

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from views.registration import RegistrationPage

from datetime import datetime
from resource.basewindow import ElementCreator, gridGenerator
from resource.static import *
from tkinter import *

from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.scrolled import ScrolledText
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
        self.inputframe = self.controller.frameCreator(
            x=40, y=100, framewidth=720, frameheight=780,
            bg=WHITE, classname="inputframe", root=self
        )
        self.menuframe = self.controller.frameCreator(
            x=0, y=80, framewidth=720, frameheight=700,
            bg=WHITE, classname="specializationframe", root=self.inputframe
        )
        self.inputframe.grid_remove()

    def createElements(self):
        self.controller.labelCreator(
            ipath="assets/Registration/Doctor/DoctorSignUpForm.png",
            x=0, y=0, classname="secondarypanelbg", root=self
        )
        self.createLabels()
        self.createButtons()
        self.initializeFormVars()

    def createLabels(self):
        self.roleImg = self.controller.labelCreator(
            ipath="assets/Registration/DoctorFormButton.png",
            x=60, y=880, classname="roleimg", root=self.parent,
        )

    def createButtons(self):
        self.OPT1STR = "Employment History"
        self.OPT2STR = "Education History"
        self.OPT3STR = "Specialization"
        optList = [self.OPT1STR, self.OPT2STR, self.OPT3STR]
        # creating a button arrangement of two per row,
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
            buttonFunction=lambda: self.confirmSubmission() if self.validateDoctorForm() else None
        )

    def initializeFormVars(self):
        self.vars = {k: StringVar() for k in [
            self.OPT1STR, self.OPT2STR, self.OPT3STR]}

    def loadInputForOption(self, option: str):
        try:
            self.specializationMenu.grid_remove()
        except AttributeError:
            pass
        self.loadInfoLabel(option)
        if option == self.OPT3STR:
            self.loadSpecializationMenu()
            return
        self.createEditText()
        if self.vars[option].get() != "":
            self.inputTextSpace.insert("1.0", self.vars[option].get())
        self.configSaveClearButtons(option)

    def loadSpecializationMenu(self):
        self.menuframe.grid()
        self.menuframe.tkraise()
        try:
            self.inputTextSpace.place_forget()
        except AttributeError:
            pass
        try:
            self.controller.widgetsDict["reg_cleartextbutton"].grid_remove()
            self.controller.widgetsDict["reg_savetext"].grid_remove()
        except KeyError:
            pass
        specializations = [
            "General Practice",
            "Dermatology",
            "Cardiology",
            "Gynaecology",
            "Neurology",
            "Ophthalmology",
            "Orthopaedics",
            "Paediatrics",
            "Urology",
            "Other",
            "None"
        ]
        self.specializationMenu = self.controller.menubuttonCreator(
            x=40, y=20, width=640, height=80,
            root=self.menuframe, classname="specializationmenu",
            text=f"Please Select Specialization", listofvalues=specializations,
            variable=self.vars[self.OPT3STR], font=("Helvetica", 12),
            command=lambda:
                ToastNotification(title="Specialization Selected", bootstyle="success", duration=3000,
                                  message=f"Specialization Selected: {self.vars[self.OPT3STR].get()}").show_toast()
        )
        try:
            if self.vars[self.OPT3STR].get() != "":
                self.specializationMenu.config(
                    text=f"{self.vars[self.OPT3STR].get()}")
        except AttributeError:
            pass
        self.configSaveClearButtons(self.OPT3STR)

    def configSaveClearButtons(self, option):
        BCR = self.controller.buttonCreator
        saveCoords = (400, 680)
        BCR(
            ipath="assets/Registration/Patient/Back.png", x=640, y=10,
            classname="reg_backbutton", root=self.inputframe,
            buttonFunction=lambda: [self.inputframe.grid_remove()],
            isPlaced=True
        )
        BCR(
            ipath="assets/Registration/Patient/ClearText.png", x=100, y=680,
            classname="reg_cleartextbutton", root=self.inputframe,
            buttonFunction=lambda: [self.inputTextSpace.delete("1.0", END)],
        ) if option != self.OPT3STR else None
        BCR(
            ipath="assets/Registration/Patient/SaveText.png", x=saveCoords[0], y=saveCoords[1],
            classname="reg_savetext", root=self.inputframe,
            buttonFunction=lambda: [
                self.vars[option].set(
                    self.inputTextSpace.get("1.0", "end-1c")),
                ToastNotification(title="Saved", bootstyle="success", duration=3000,
                                  message=f"Saved {option}").show_toast(),
            ]
        ) if option != self.OPT3STR else None

    def createEditText(self):
        self.inputText = ScrolledText(
            master=self.inputframe, width=520, height=520, padding=0,
            bootstyle="success-round", autohide=True, name="inputtext")
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
    
    def validateDoctorForm(self):
        if self.vars[self.OPT3STR].get() == "":
            messagebox.showerror(title="Error", message="Please select a specialization")
            return False
        elif self.vars[self.OPT1STR].get() == "":
            messagebox.showerror(title="Error", message="Please fill in  your employment history")
            return False
        elif self.vars[self.OPT2STR].get() == "":
            messagebox.showerror(title="Error", message="Please fill in your education history")
            return False

    def confirmSubmission(self):
        prisma = self.prisma
        WD = self.controller.widgetsDict
        # get the values from the entry boxes
        self.country, self.state, self.city = self.parent.country.get(
        ), self.parent.state.get(), self.parent.city.get()
        dateStr = self.parent.dateOfBirthEntry.get()  # "%d/%m/%Y"
        # datetimeObj
        dateObj = datetime.strptime(dateStr, "%d/%m/%Y")
        doctor = prisma.doctor.create(
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
                "employmentHistory": self.vars[self.OPT1STR].get(),
                "educationHistory": self.vars[self.OPT2STR].get(),
                "speciality": self.vars[self.OPT3STR].get().upper().replace(" ", "_"),
            }
        )
        toast = ToastNotification("Registration", f"{doctor.user.fullName} has been registered as a doctor", duration=3000,
                          bootstyle="success", )
        toast.show_toast()
        self.parent.loadSignIn()
