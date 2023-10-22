from __future__ import annotations
import io
from tkinter import filedialog

from typing import TYPE_CHECKING

from prisma import Base64

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
        self.clinicstateVar = StringVar()
        self.cliniczipVar = StringVar()
        self.cliniccontactnumberVar = StringVar()

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
                self.clinicstateVar, self.cliniczipVar, self.cliniccontactnumberVar
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
            "clinicstate": {
                X: 40,
                Y: 480,
                W: 300,
                H: 80,
                CN: "clinicstateentry",
                R: frame,
                PH: "Clinic State"
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

    def loadClinicInformationInput(self):
        WD = self.controller.widgetsDict
        WD["clinicnameentry"].delete(0, END)
        WD["clinicaddressentry"].delete(0, END)
        WD["cliniccontactnumberentry"].delete(0, END)
        WD["cliniccityentry"].delete(0, END)
        WD["clinicstateentry"].delete(0, END)
        WD["cliniczipentry"].delete(0, END)
        WD["clinicnameentry"].insert(0, self.clinicnameVar.get())
        WD["clinicaddressentry"].insert(0, self.clinicaddressVar.get())
        WD["cliniccontactnumberentry"].insert(
            0, self.cliniccontactnumberVar.get())
        WD["cliniccityentry"].insert(0, self.cliniccityVar.get())
        WD["clinicstateentry"].insert(0, self.clinicstateVar.get())
        WD["cliniczipentry"].insert(0, self.cliniczipVar.get())

    def saveClinicInformation(self):
        WD = self.controller.widgetsDict
        self.clinicnameVar.set(
            WD["clinicnameentry"].get())
        self.clinicaddressVar.set(
            WD["clinicaddressentry"].get())
        self.cliniccontactnumberVar.set(
            WD["cliniccontactnumberentry"].get())
        self.cliniccityVar.set(
            WD["cliniccityentry"].get())
        self.clinicstateVar.set(
            WD["clinicstateentry"].get())
        self.cliniczipVar.set(
            WD["cliniczipentry"].get())
        msg = f"""
        Clinic Information Saved!
        Name: {self.clinicnameVar.get()}
        Address: {self.clinicaddressVar.get()}
        Contact Number: {self.cliniccontactnumberVar.get()}
        City: {self.cliniccityVar.get()}
        State: {self.clinicstateVar.get()}
        Zip: {self.cliniczipVar.get()} 
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
        self.inputframe.grid()
        self.inputframe.tkraise()
        infolabel = self.controller.textElement(
            ipath="assets/Registration/InputFormTextBG.png", x=0, y=0,
            classname="inputformtext", root=frame, text=f"{option}",
            size=30, font=INTER
        )
        bg = self.controller.labelCreator(
            ipath="assets/Registration/Admin/UploadClinicImage.png", x=0, y=80,
            classname="clinicinfobg", root=frame
        )
        bg.tk.call("lower", bg._w)
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
        clinicAdmin = prisma.clinicadmin.create(
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
                "clinic": {
                    "create": {
                        "name": self.clinicnameVar.get(),
                        "address": self.clinicaddressVar.get(),
                        "city": self.cliniccityVar.get(),
                        "state": self.clinicstateVar.get(),
                        "zip": self.cliniczipVar.get(),
                        "clinicImg": self.getBase64Data(),
                        "phoneNum": self.cliniccontactnumberVar.get(),
                    }
                }
            }
        )
