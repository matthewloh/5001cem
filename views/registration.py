import random
import re
import string
import threading
from tkinter import *
from tkinter import messagebox
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.toast import ToastNotification
from resource.static import *
from resource.basewindow import ElementCreator, gridGenerator
from views.citystatesdict import states_dict
from ttkbootstrap.dialogs import DatePickerDialog, Querybox
from datetime import datetime as dt
# from components.animatedgif import AnimatedGif
# from captcha.image import ImageCaptcha
# from components.animatedgif import AnimatedGif
import bcrypt
from views.registrationForms.adminForm import AdminRegistrationForm
from views.registrationForms.doctorForm import DoctorRegistrationForm
from views.registrationForms.officerForm import OfficerRegistrationForm

from views.registrationForms.patientForm import PatientRegistrationForm


class RegistrationPage(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None, name="registration"):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name=name)
        self.controller = controller
        self.parent = parent
        self.name = name
        gridGenerator(self, 96, 54, "#dee8e0")
        self.createFrames()
        self.createElements()
        self.prisma = self.controller.mainPrisma
        self.frameref.tkraise()

    def createFrames(self):
        self.frameref = self.controller.frameCreator(
            x=560, y=80, framewidth=800, frameheight=920,
            root=self, classname=f"registrationformframe",
        )

    def createElements(self):
        """
        (imagepath, x, y, classname, root)
        """
        self.staticImgLabels = [
            ("assets/Registration/RegistrationBG.png", 0, 0, "registrationbg", self),
            ("assets/Registration/SignUpForm.png",
             0, 0, f"formframebg", self.frameref),

        ]
        self.staticBtns = [
            ("assets/Registration/RedirectLoginButton.png",
             60, 80, "redirectloginbutton", self,
             lambda: self.loadSignIn()),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.controller.settingsUnpacker(self.staticBtns, "button")
        self.loadFormEntries()
        self.createCountryMenuBtns()
        self.createRoleButtons()

    def loadFormEntries(self):
        self.userRegEntries = [
            (40, 120, 720, 60, self.frameref, "regfullname"),
            (40, 220, 340, 60, self.frameref, "regemail", "isEmail"),
            (420, 220, 340, 60, self.frameref, "regnric", "isNRIC"),
            (40, 320, 260, 60, self.frameref, "regbirthdate"),
            (420, 320, 340, 60, self.frameref, "regcontactnumber", "isContactNo"),
            (40, 420, 340, 60, self.frameref, "regpassent", "isPassword"),
            (420, 420, 340, 60, self.frameref, "regconfpassent", "isConfPass"),
            (40, 520, 340, 60, self.frameref, "countryoforigin"),
            (40, 660, 340, 60, self.frameref, "regaddressline1"),
            (420, 660, 340, 60, self.frameref, "regaddressline2"),
            (160, 740, 220, 60, self.frameref, "regpostcode", "isPostcode"),
        ]
        for i in self.userRegEntries:
            self.controller.ttkEntryCreator(**self.tupleToDict(i))
        EC = self.controller.ttkEntryCreator
        self.fullname = EC(
            x=40, y=120, width=720, height=60, root=self.frameref, classname="regfullname", validation="isFullName"
        )
        self.email = EC(
            x=40, y=220, width=340, height=60, root=self.frameref, classname="regemail", validation="isEmail"
        )
        self.nric_passno = EC(
            x=420, y=220, width=340, height=60, root=self.frameref, classname="regnric", validation="isNRIC"
        )
        self.dateOfBirthEntry = self.controller.ttkEntryCreator(
            x=40, y=320, width=260, height=60, root=self.frameref, classname="regbirthdate"
        )
        self.initDatePicker()
        self.contactnumber = EC(
            x=420, y=320, width=340, height=60, root=self.frameref, classname="regcontactnumber", validation="isContactNo"
        )
        self.password = EC(
            x=40, y=420, width=340, height=60, root=self.frameref, classname="regpassent", validation="isPassword"
        )
        self.confirmpassword = EC(
            x=420, y=420, width=340, height=60, root=self.frameref, classname="regconfpassent", validation="isConfPass"
        )
        self.countryoforigin = EC(
            x=40, y=520, width=340, height=60, root=self.frameref, classname="countryoforigin"
        )
        self.addressline1 = EC(
            x=40, y=660, width=340, height=60, root=self.frameref, classname="regaddressline1"
        )
        self.addressline2 = EC(
            x=420, y=660, width=340, height=60, root=self.frameref, classname="regaddressline2"
        )
        self.postcode = EC(
            x=160, y=740, width=220, height=60, root=self.frameref, classname="regpostcode", validation="isPostcode"
        )
        self.race, self.gender, self.country, self.state, self.city = StringVar(
        ), StringVar(), StringVar(), StringVar(), StringVar()

        # Race and Gender Menubuttons
        self.races = ["Malay", "Chinese", "Indian", "Others"]
        self.genders = ["Male", "Female", "Other", "Prefer not to say"]
        self.raceMenuBtn = self.controller.menubuttonCreator(
            x=420, y=520, width=160, height=60,
            root=self.frameref, classname="reg_race",
            text="Race", listofvalues=self.races,
            variable=self.race, font=("Helvetica", 12),
            command=lambda:
                ToastNotification(title="Success", bootstyle="success", duration=3000,
                                  message=f"Race Selected: {self.race.get()}").show_toast()
        )
        self.genderMenuBtn = self.controller.menubuttonCreator(
            x=600, y=520, width=160, height=60,
            root=self.frameref, classname="reg_gender",
            text="Gender", listofvalues=self.genders,
            variable=self.gender, font=("Helvetica", 12),
            command=lambda:
                ToastNotification(title="Success", bootstyle="success", duration=3000,
                                  message=f"Gender Selected: {self.gender.get()}").show_toast()
        )
        self.seedDataBtn = self.controller.buttonCreator(
            ipath="assets/Registration/Seed.png",
            x=720, y=20, classname="seeddatabtn", root=self.frameref,
            buttonFunction=lambda: self.seed_data()
        )

    def initDatePicker(self):
        self.datePicker = self.controller.buttonCreator(
            ipath="assets/Registration/DatePicker.png",
            x=320, y=320, classname="datepicker", root=self.frameref,
            buttonFunction=lambda: self.selectDate(self.datePicker)
        )
        self.dobMsg = "Select Date of Birth"
        self.dateOfBirthEntry.insert(0, self.dobMsg)
        self.dateOfBirthEntry.config(state=READONLY)

    def createCountryMenuBtns(self):
        list = {
            "reg_country": {
                "pos": {"x": 540, "y": 740, "width": 220, "height": 60},
                "listofvalues": ["Malaysia", "Others"],
                "variable": self.country,
            }
        }
        for name, v in list.items():
            self.controller.menubuttonCreator(
                x=v["pos"]["x"], y=v["pos"]["y"], width=v["pos"]["width"], height=v["pos"]["height"],
                root=self.frameref, classname=name, text=f"Please Select Country", listofvalues=v["listofvalues"],
                variable=v["variable"], font=("Helvetica", 12),
                command=lambda: [self.loadStateMenubuttons(self.country.get())]
            )
    
    def validateRegInfo(self):
        if self.fullname.get() == "" or self.fullname.validate() == False:
            messagebox.showerror(title="Error", message="Please enter a valid full name.")
            return False
        elif self.email.get() == "" or self.email.validate() == False:
            messagebox.showerror(title="Error", message="Please enter a valid email address.")
            return False
        elif self.nric_passno.get() == "" or self.nric_passno.validate() == False:
            messagebox.showerror(title="Error", message="Please enter a valid NRIC or Passport Number.")
            return False
        elif self.dateOfBirthEntry.get() == "Select Date of Birth":
            messagebox.showerror(title="Error", message="Please select a date of birth.")
            return False
        elif self.contactnumber.get() == "" or self.contactnumber.validate() == False:
            messagebox.showerror(title="Error", message="Please enter a valid contact number.")
            return False
        elif self.password.get() == "" or self.password.validate() == False:
            messagebox.showerror(title="Error", message="Please enter a valid password.\nPassword must contain at least 1 uppercase, 1 number, 1 special character and must be at least 8 characters long.")
            return False
        elif self.confirmpassword.get() == "" or self.confirmpassword.validate() == False:
            messagebox.showerror(title="Error", message="Please enter a valid confirmation password.")
            return False
        elif self.countryoforigin.get() == "":
            messagebox.showerror(title="Error", message="Please enter country of origin.")
            return False
        elif self.addressline1.get() == "":
            messagebox.showerror(title="Error", message="Please enter an address.")
            return False
        elif self.postcode.get() == "" or self.postcode.validate() == False:
            messagebox.showerror(title="Error", message="Please enter a valid postcode.")
            return False
        elif self.gender.get() =="" or self.gender.get() == "Gender":
            messagebox.showerror(title="Error", message="Please select a gender.")
            return False
        elif self.race.get() =="" or self.race.get() == "Race":
            messagebox.showerror(title="Error", message="Please select a race.")
            return False
        elif self.country.get() == "" or self.country.get() == "Please Select Country":
            messagebox.showerror(title="Error", message="Please select a country.")
            return False
        elif self.state.get() == "" or self.state.get() == "Please Select State":
            messagebox.showerror(title="Error", message="Please select a state.")
            return False
        elif self.city.get() == "" or self.city.get() == "Please Select City":
            messagebox.showerror(title="Error", message="Please select a city.")
            return False
        
        else:
            return True
                

    def createRoleButtons(self):
        self.patientFormBtn = self.controller.buttonCreator(
            ipath="assets/Registration/PatientFormButton.png",
            x=1420, y=460, classname="patientformbtn", root=self,
            buttonFunction=lambda: self.loadRoleAssets(patient=True) if self.validateRegInfo() else None
        )
        self.doctorFormBtn = self.controller.buttonCreator(
            ipath="assets/Registration/DoctorFormButton.png",
            x=1420, y=600, classname="doctorformbtn", root=self,
            buttonFunction=lambda: self.loadRoleAssets(doctor=True) if self.validateRegInfo() else None
        )
        self.adminFormBtn = self.controller.buttonCreator(
            ipath="assets/Registration/AdminFormButton.png",
            x=1420, y=740, classname="adminformbtn", root=self,
            buttonFunction=lambda: self.loadRoleAssets(clinicAdmin=True) if self.validateRegInfo() else None
        )
        self.officerFormBtn = self.controller.buttonCreator(
            ipath="assets/Registration/OfficerFormButton.png",
            x=1420, y=880, classname="officerformbtn", root=self,
            buttonFunction=lambda: self.loadRoleAssets(govofficer=True) if self.validateRegInfo() else None
        )

    def selectDate(self, btn):
        self.dateOfBirthEntry.configure(foreground="black")
        year = Querybox.get_integer(
            parent=btn, title="Enter Year", minvalue=1900, maxvalue=2023, initialvalue=2023,
            prompt="Please enter birth year, to aid in adjustment, left-click the arrow to move the calendar by one month. Right-click the arrow to move the calendar by one year or right-click the title to reset the calendar to the start date."
        )
        if year is None:
            self.dateOfBirthEntry.configure(foreground="red")
            return
        dateTimeYear = dt.strptime(f"{year}", "%Y")
        dialog = DatePickerDialog(
            parent=btn, title="Select Date", firstweekday=0, startdate=dateTimeYear
        )
        if dialog.date_selected is None:
            print('test')
            return
        if dialog.date_selected.year > dt.now().year or dialog.date_selected.year < 1900:
            toast = ToastNotification(
                title="Error",
                message="Please select a valid date of birth between 1900 and the current year",
                duration=3000,
                bootstyle="danger"
            )
            toast.show_toast()
            return
        if dialog.date_selected.year > dt.now().year - 18:
            toast = ToastNotification(
                title="Error",
                message="You must be at least 18 years old to use this system",
                duration=3000,
                bootstyle="danger"
            )
            toast.show_toast()
            return
        self.dateTimeDOB = dialog.date_selected
        date = dialog.date_selected.strftime("%d/%m/%Y")
        self.dateOfBirthEntry.configure(state=NORMAL)
        self.dateOfBirthEntry.delete(0, END)
        self.dateOfBirthEntry.insert(0, date)
        self.dateOfBirthEntry.configure(state=READONLY)

    def loadStateMenubuttons(self, name):
        # remove all widgets and refresh options
        if name == "Others":
            toast = ToastNotification(
                title="The system is not fully supported for your country yet",
                message="You may proceed to register but some features may not be available yet",
                bootstyle="warning",
                duration=5000,
            )
            self.country.set("Others")
            self.state.set("Others")
            toast.show_toast()
        for widgetname, widget in self.frameref.children.items():
            if not widgetname.startswith("!la"):
                if widgetname in ["statehostfr", "cityhostfr"]:
                    widget.grid_remove()
        # reset variables
        for var in [self.state, self.city]:
            var.set("")
        positions = {
            "state": {"x": 160, "y": 820, "width": 220, "height": 60},
        }
        if not self.country.get() == "Malaysia":
            return
        statelist = list(states_dict.keys())
        self.stateMenuButton = self.controller.menubuttonCreator(
            x=positions["state"]["x"], y=positions["state"]["y"], width=positions[
                "state"]["width"], height=positions["state"]["height"],
            root=self.frameref, classname="state", text=f"Please Select State", listofvalues=statelist,
            variable=self.state, font=("Helvetica", 12),
            command=lambda: [self.loadCityMButtons(self.state.get())]
        )

    def loadCityMButtons(self, state):
        # remove all widgets and refresh options
        for widgetname, widget in self.frameref.children.items():
            if not widgetname.startswith("!la"):
                if widgetname in ["cityhostfr"]:
                    widget.grid_remove()
        # reset variables
        for var in [self.city]:
            var.set("")
        positions = {
            "city": {"x": 540, "y": 820, "width": 220, "height": 60},
        }
        citieslist = list(states_dict[f"{state}"])
        self.cityMenuButton = self.controller.menubuttonCreator(
            x=positions["city"]["x"], y=positions["city"]["y"], width=positions[
                "city"]["width"], height=positions["city"]["height"],
            root=self.frameref, classname="city", text=f"Please Select City", listofvalues=citieslist,
            variable=self.city, font=("Helvetica", 12),
            command=lambda: [None]
        )

    def tupleToDict(self, tup):
        if len(tup) == 6:
            return dict(zip(["x", "y", "width", "height", "root", "classname"], tup))
        elif len(tup) == 7:
            return dict(zip(["x", "y", "width", "height", "root", "classname", "validation"], tup))
        elif len(tup) == 8:
            return dict(zip(["x", "y", "width", "height", "root", "classname", "validation", "captchavar"], tup))
                

    def seed_data(self):
        WD = self.controller.widgetsDict
        self.fullname.delete(0, END)
        self.fullname.insert(0, "John Doe")
        self.email.delete(0, END)
        self.email.insert(0, f"johndoe{random.randint(0, 1000)}@gmail.com")
        self.nric_passno.delete(0, END)
        # 4 random digits
        randomId = random.randint(1000, 9999)
        self.nric_passno.insert(0, f"03020107{randomId}")
        self.dateOfBirthEntry.configure(state=NORMAL)
        self.dateOfBirthEntry.delete(0, END)
        self.dateOfBirthEntry.insert(0, "01/01/2000")
        self.dateOfBirthEntry.configure(state=READONLY)
        self.contactnumber.delete(0, END)
        self.contactnumber.insert(0, "0123456789")
        self.password.delete(0, END)
        self.password.insert(0, "Password_1")
        self.confirmpassword.delete(0, END)
        self.confirmpassword.insert(0, "Password_1")
        self.countryoforigin.delete(0, END)
        self.countryoforigin.insert(0, "Malaysia")
        self.addressline1.delete(0, END)
        self.addressline1.insert(0, "123, Jalan ABC")
        self.addressline2.delete(0, END)
        self.addressline2.insert(0, "Taman ABC")
        self.postcode.delete(0, END)
        self.postcode.insert(0, "12345")
        self.raceMenuBtn.configure(text="Malay")
        self.race.set("Malay")
        self.genderMenuBtn.configure(text="Male")
        self.gender.set("Male")
        WD["reg_country"].configure(text="Malaysia")
        self.country.set("Malaysia")
        self.loadStateMenubuttons("Malaysia")
        self.loadCityMButtons("Pulau Pinang")
        self.stateMenuButton.configure(text="Pulau Pinang")
        self.state.set("Pulau Pinang")
        self.cityMenuButton.configure(text="Georgetown")
        self.city.set("Georgetown")

    def loadAllDetailsForRegistration(self):
        prisma = self.prisma
        clinics = prisma.clinic.find_many(
            include={
                "admin": True,
                "clinicRegistration": True,
                "doctor": True,
                "govRegDocSystem": True,
            }
        )
        return clinics

    def encryptPassword(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def validatePassword(self, password: str, encrypted: str) -> str:
        return bcrypt.checkpw(password.encode("utf-8"), encrypted.encode("utf-8"))

    def validate_captcha(self, captcha: str):
        captchaToast = ToastNotification(
            title="Error",
            message="",
            duration=3000,
            bootstyle=DANGER
        )
        if captcha != self.captchavar.get():
            captchaToast.message = "Captcha is incorrect."
            captchaToast.show_toast()
            return False
        return True

    def validate_password(self, password: str, confirmpassword: str):
        pwToast = ToastNotification(
            title="Error",
            message="",
            duration=3000,
            bootstyle=DANGER
        )
        symbols = "!@#$%^&*()_+"
        if password != confirmpassword:
            pwToast.message = "Passwords do not match."
            pwToast.show_toast()
            return False
        elif not any(char.isdigit() for char in password):
            msg = "Password should have at least one numeral."
        elif not any(char.isupper() for char in password):
            msg = "Password should have at least one uppercase letter."
        elif not any(char.islower() for char in password):
            msg = "Password should have at least one lowercase letter."
        elif not any(char in symbols for char in password):
            msg = "Password should have at least one of the symbols !@#$%^&*()_+"
        elif len(password) < 8:
            msg = "Password should be at least 8 characters."
        else:
            return True
        pwToast.message = msg
        pwToast.show_toast()
        return False

    def validate_email(self, email: str, role: str):
        emailToast = ToastNotification(
            title="Error",
            message="",
            duration=3000,
            bootstyle=DANGER
        )
        if role.startswith("student"):
            regex = re.compile(r"^[a-zA-Z0-9_.+-]+@student.newinti.edu.my$")
            addressedAs = "student"
        elif role.startswith("teacher"):
            regex = re.compile(r"^[a-zA-Z0-9_.+-]+@newinti.edu.my$")
            addressedAs = "lecturer"
        if re.match(regex, email):
            return True
        else:
            emailToast.message = f"Please enter a valid {addressedAs} email."
            emailToast.show_toast()
            return False

    def validate_contactNo(self, contactNo: str):
        contactToast = ToastNotification(
            title="Error",
            message="",
            duration=3000,
            bootstyle=DANGER
        )
        phoneregex = re.compile(
            r"^(/+?6?01)[02-46-9]-*[0-9]{7}$|^(/+?6?01)[1]-*[0-9]{8}$")
        if re.match(phoneregex, contactNo):
            return True
        else:
            contactToast.message = "Please enter a valid contact number."
            contactToast.show_toast()
            return False

    def validateData(self, data: dict):
        fullname = data["fullName"]
        email = data["email"]
        contactNo = data["contactNo"]
        password = self.controller.widgetsDict[f"{self.name}passent"].get()
        confirmpassword = self.controller.widgetsDict[f"{self.name}confpassent"].get(
        )
        captcha = self.controller.widgetsDict[f"{self.name}captcha"].get()
        entries = [fullname, email, contactNo, password, confirmpassword]
        mainToast = ToastNotification(
            title="Error",
            message="",
            duration=3000,
            bootstyle=DANGER
        )
        field_names = ["Full Name", "Email",
                       "Contact Number", "Password", "Confirm Password"]
        for i, info in enumerate(entries):
            if info == "":
                field_name = field_names[i]
                toast = ToastNotification(
                    title="Error",
                    message=f"The {field_name} field is empty. Please fill it in.",
                    duration=3000,
                    bootstyle=DANGER
                )
                toast.show_toast()
                return False
        if any(char in string.punctuation for char in fullname):
            errMsg = "Your name cannot contain any special characters."
            mainToast.message = errMsg
            mainToast.show_toast()
            return False
        if not self.validate_email(email, self.name):
            return False
        if not self.validate_password(password, confirmpassword):
            return False
        if not self.validate_contactNo(contactNo):
            return False
        if captcha != self.captchavar.get():
            mainToast.message = "Please enter the correct captcha."
            mainToast.show_toast()
            return False
        for var in [self.course1, self.course2, self.course3, self.course4]:
            blankCourses = 0
            if var.get() == "":
                blankCourses += 1
        if blankCourses >= 3:
            toast = ToastNotification(
                title="Error",
                message=f"Please select at least 1 course.",
                duration=3000
            )
            toast.show_toast()
            return False
        return True

    def loadSignIn(self):
        self.grid_remove()

    def loadRoleAssets(self, patient: bool = False, doctor: bool = False, clinicAdmin: bool = False, govofficer: bool = False):
        self.validateRegInfo()
        self.btns = [self.patientFormBtn, self.doctorFormBtn,
                     self.adminFormBtn, self.officerFormBtn]
        for btn in self.btns:
            btn.grid_remove()
        self.returnToPersonalDetails = self.controller.buttonCreator(
            ipath="assets/Registration/ReturnToPersonalInfoBtn.png",
            x=60, y=760, classname="returntopersonaldetails", root=self,
            buttonFunction=lambda: self.reloadPersonalDetails()
        )
        if patient:
            self.primaryForm = PatientRegistrationForm(
                parent=self, controller=self.controller)
        elif doctor:
            self.primaryForm = DoctorRegistrationForm(
                parent=self, controller=self.controller)
        elif clinicAdmin:
            self.primaryForm = AdminRegistrationForm(
                parent=self, controller=self.controller)
        elif govofficer:
            self.primaryForm = OfficerRegistrationForm(
                parent=self, controller=self.controller)
        else:
            return

    def reloadPersonalDetails(self):
        self.primaryForm.roleImg.grid_remove()
        self.frameref.tkraise()
        for btn in self.btns:
            btn.grid()
        self.primaryForm.completeRegBtn.grid_remove()
        self.returnToPersonalDetails.grid_remove()
