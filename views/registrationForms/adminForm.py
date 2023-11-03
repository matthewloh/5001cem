from __future__ import annotations
import io
from tkinter import filedialog

from typing import TYPE_CHECKING

from prisma import Base64
from views.citystatesdict import states_dict
if TYPE_CHECKING:
    from views.registration import RegistrationPage
import calendar
import re
import threading
from tkinter import *
from tkinter import messagebox
from prisma.models import Appointment
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from ttkbootstrap.dialogs.dialogs import DatePickerDialog
from prisma.errors import RecordNotFoundError
from resource.basewindow import gridGenerator
from resource.static import *
from resource.basewindow import ElementCreator
from datetime import datetime, timedelta
import datetime as dt
from PIL import Image, ImageOps, ImageTk
from pendulum import timezone
import tkintermapview


class AdminRegistrationForm(Frame):
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
            ipath="assets/Registration/Admin/AdminSignUpForm.png",
            x=0, y=0, classname="secondarypanelbg", root=self
        )
        self.createLabels()
        self.createButtons()
        self.createVars()

    def createLabels(self):
        self.roleImg = self.controller.labelCreator(
            ipath="assets/Registration/AdminFormButton.png",
            x=60, y=880, classname="roleimg", root=self.parent,
        )

    def createButtons(self):
        self.OPT1STR = "Clinic Details"
        self.OPT2STR = "Upload Clinic Image"
        self.OPT3STR = "Manage Doctors"
        self.OPT4STR = "Other Information"
        optList = [self.OPT1STR, self.OPT2STR,
                   #    self.OPT3STR,
                   #    self.OPT4STR
                   ]
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
        self.closebutton = self.controller.buttonCreator(
            ipath="assets/Registration/Close.png", x=80, y=680,
            classname="reg_closebutton", root=self.inputframe,
            buttonFunction=lambda: [self.inputframe.grid_remove()]
        )
        self.savebutton = self.controller.buttonCreator(
            ipath="assets/Registration/Save.png", x=420, y=680,
            classname="reg_savebutton", root=self.inputframe,
            buttonFunction=lambda: [print('test')]
        )
        self.closebutton.grid_remove()
        self.savebutton.grid_remove()

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

    def createClinicInfoEntries(self, frame):
        CREATOR = self.controller.ttkEntryCreator
        X, Y, W, H, R, CN, PH = "x", "y", "width", "height", "root", "classname", "placeholder"
        param = {
            "clinicname": {
                X: 40,
                Y: 120,
                W: 640,
                H: 80,
                CN: "clinicnameentry",
                R: frame,
                PH: "Clinic Name"
            },
            "clinicaddress": {
                X: 40,
                Y: 240,
                W: 640,
                H: 80,
                CN: "clinicaddressentry",
                R: frame,
                PH: "Clinic Address"
            },
            "cliniccontactnumber": {
                X: 40,
                Y: 360,
                W: 300,
                H: 80,
                CN: "cliniccontactnumberentry",
                R: frame,
                PH: "Clinic Contact Number"
            },
            "cliniccity": {
                X: 380,
                Y: 360,
                W: 300,
                H: 80,
                CN: "cliniccityentry",
                R: frame,
                PH: "Clinic City"
            },
            "cliniczip": {
                X: 380,
                Y: 480,
                W: 300,
                H: 80,
                CN: "cliniczipentry",
                R: frame,
                PH: "Clinic Zip"
            },
        }
        for p in param:
            CREATOR(**param[p])
        self.clinicStateVar = StringVar()
        states = list(states_dict.keys())
        self.menuframe = self.controller.frameCreator(
            x=40, y=480, framewidth=300, frameheight=80,
            bg=WHITE, classname="clinicstateframe", root=frame
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

    def loadUploadClinicImage(self, option: str):
        frame = self.inputframe
        for widgetname, widget in self.inputframe.children.items():
            if widgetname.endswith("hostfr"):
                widget.grid_remove()
        try:
            self.menuframe.grid_remove()
        except AttributeError:
            pass
        self.inputframe.grid()
        self.inputframe.tkraise()
        infolabel = self.controller.textElement(
            ipath="assets/Registration/InputFormTextBG.png", x=0, y=0,
            classname="inputformtext", root=frame, text=f"{option}",
            size=30, font=INTER
        )
        self.bg = self.controller.labelCreator(
            ipath="assets/Registration/Admin/UploadClinicImage.png", x=0, y=80,
            classname="clinicinfobg", root=frame
        )
        self.bg.tk.call("lower", self.bg._w)
        try:
            self.imageLabel.tk.call("raise", self.imageLabel._w)
        except AttributeError:
            pass
        self.uploadClinicImgBtn = self.controller.buttonCreator(
            ipath="assets/Registration/Admin/UploadImg.png", x=560, y=140,
            classname="uploadclinicimg", root=frame,
            buttonFunction=lambda: self.uploadImage()
        )
        self.loadCloseAndSaveButtons()

    def uploadImage(self):
        self.imagePath = ""
        self.imagePath = filedialog.askopenfilename(
            initialdir="Assets", title="Select File", filetypes=(
                ("Image Files", "*.jpg *.png *.jpeg *.webp"),
            )
        )
        if self.imagePath == "":
            self.imagePath = ""
            messagebox.showerror(
                title="Error", message="Aborting image upload."
            )
            return
        ask = MessageDialog(
            parent=self.uploadClinicImgBtn,
            title="Select an option",
            message="Submit using Pad to maintain a 4:3 aspect ratio with white border\nSubmit using Thumbnail in original aspect ratio with no padding\nSelect fit for completely filling 800x600\nYou may hover over the image to see the size submitted.",
            buttons=["Pad:success", "Thumbnail:secondary",
                     "Fit:info", "Cancel"],
        )
        ask.show()
        CREATOR = self.controller.labelCreator
        IP, X, Y, CN, R, BF = "ipath", "x", "y", "classname", "root", "buttonFunction"
        self.imageLabel = self.controller.labelCreator(
            ipath=self.imagePath, x=40, y=140,
            classname="imgplaceholder", root=self.inputframe,
            isPlaced=True
        )
        self.cropImage(ask.result)
        self.cropOptions = [
            ("assets/Registration/Admin/Pad.png", 560, 220,
             "padoption", self.inputframe, lambda: self.cropImage("Pad")),
            ("assets/Registration/Admin/Thumbnail.png", 560, 300,
             "thumbnailoption", self.inputframe, lambda: self.cropImage("Thumbnail")),
            ("assets/Registration/Admin/Fit.png", 560, 380,
             "fitoption", self.inputframe, lambda: self.cropImage("Fit")),
        ]
        self.controller.settingsUnpacker(self.cropOptions, "button")

    def cropImage(self, option: str):
        if option == "Pad":
            image = self.controller.imagePathDict["imgplaceholder"]
            image = Image.open(image)
            image = ImageOps.pad(image, (500, 500))
        elif option == "Thumbnail":
            image = self.controller.imagePathDict["imgplaceholder"]
            image = Image.open(image)
            image.thumbnail((500, 500))
        elif option == "Fit":
            image = self.controller.imagePathDict["imgplaceholder"]
            image = Image.open(image)
            image = ImageOps.fit(image, (500, 500))
        else:
            messagebox.showerror(
                title="Error", message="Aborting image upload."
            )
            return
        self.controller.imageDict["imgplaceholder"] = ImageTk.PhotoImage(
            image)
        newImage = self.controller.imageDict["imgplaceholder"]
        self.imageLabel.config(image=newImage, width=500, height=500)
        self.imageLabel.place(x=40+(500-image.width)//2,
                              y=140+(500-image.height)//2,
                              width=image.width, height=image.height)
        self.finalImage = image
        self.imageLabel.bind("<Enter>", self.showImageSize)
        self.imageLabel.bind("<Leave>", self.hideImageSize)

    def showImageSize(self, event):
        try:
            self.imageLabel.config(relief=SOLID)
        except AttributeError:
            pass

    def hideImageSize(self, event):
        try:
            self.imageLabel.config(relief=FLAT)
        except AttributeError:
            pass

    def getBase64Data(self):
        byteIMGIO = io.BytesIO()
        format = self.imagePath.split(".")[-1]
        if format == "jpg":
            format = "jpeg"
        self.finalImage.save(byteIMGIO, f"{format.upper()}")
        byteIMGIO.seek(0)
        byteIMG = byteIMGIO.read()
        b64 = Base64.encode(byteIMG)
        return b64

    def loadManageDoctors(self, option: str):
        frame = self.inputframe
        self.inputframe.grid()
        self.inputframe.tkraise()
        for widgetname, widget in self.inputframe.children.items():
            if widgetname in ["padoption", "thumbnailoption", "fitoption", "uploadclinicimg"]:
                widget.grid_remove()
            elif widgetname in ["imgplaceholder"]:
                widget.place_forget()
            elif widgetname.endswith("hostfr"):
                widget.grid_remove()
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
        self.loadCloseAndSaveButtons()

    def loadOtherInformation(self, option: str):
        frame = self.inputframe
        self.inputframe.grid()
        self.inputframe.tkraise()
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
        self.loadCloseAndSaveButtons()

    def confirmSubmission(self):
        prisma = self.prisma
        # get the values from the entry boxes
        self.country, self.state, self.city = self.parent.country.get(
        ), self.parent.state.get(), self.parent.city.get()
        dateStr = self.parent.dateOfBirthEntry.get()  # "%d/%m/%Y"
        # datetimeObj
        dateObj = datetime.strptime(dateStr, "%d/%m/%Y")
        clinicAdmin = prisma.clinicadmin.create(
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
                "clinic": {
                    "create": {
                        "name": self.clinicnameVar.get(),
                        "address": self.clinicaddressVar.get(),
                        "city": self.cliniccityVar.get(),
                        "state": self.clinicStateVar.get().upper().replace(" ", "_"),
                        "zip": self.cliniczipVar.get(),
                        "clinicImg": self.getBase64Data(),
                        "phoneNum": self.cliniccontactnumberVar.get(),
                        "clinicHrs": self.clinichrsVar.get(),
                    }
                }
            },
            include={
                "clinic": True,
            }
        )
        try:
            govRegSystem = prisma.govregsystem.find_first_or_raise(
                where={
                    "state": self.state.upper().replace(" ", "_")
                }
            )
        except RecordNotFoundError:
            govRegSystem = prisma.govregsystem.create(
                data={
                    "state": self.state.upper().replace(" ", "_")
                }
            )
        clinicEnrolment = prisma.clinicenrolment.create(
            data={
                "clinic": {
                    "connect": {
                        "id": clinicAdmin.clinic.id
                    }
                },
                "govRegDocSystem": {
                    "connect": {
                        "id": govRegSystem.id
                    }
                },
                "status": "PENDING"
            }

        )
