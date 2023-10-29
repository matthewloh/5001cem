import random
import re
import string
import threading
from tkinter import *
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
        super().__init__(parent, width=1, height=1, bg="#344557", name=name)
        self.controller = controller
        self.parent = parent
        self.name = name
        gridGenerator(self, 96, 54, LIGHTYELLOW)
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
            (420, 220, 340, 60, self.frameref, "regnric"),
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
            x=40, y=120, width=720, height=60, root=self.frameref, classname="regfullname"
        )
        self.email = EC(
            x=40, y=220, width=340, height=60, root=self.frameref, classname="regemail", validation="isEmail"
        )
        self.nric_passno = EC(
            x=420, y=220, width=340, height=60, root=self.frameref, classname="regnric"
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

    def createRoleButtons(self):
        self.patientFormBtn = self.controller.buttonCreator(
            ipath="assets/Registration/PatientFormButton.png",
            x=1420, y=460, classname="patientformbtn", root=self,
            buttonFunction=lambda: self.loadRoleAssets(patient=True)
        )
        self.doctorFormBtn = self.controller.buttonCreator(
            ipath="assets/Registration/DoctorFormButton.png",
            x=1420, y=600, classname="doctorformbtn", root=self,
            buttonFunction=lambda: self.loadRoleAssets(doctor=True)
        )
        self.adminFormBtn = self.controller.buttonCreator(
            ipath="assets/Registration/AdminFormButton.png",
            x=1420, y=740, classname="adminformbtn", root=self,
            buttonFunction=lambda: self.loadRoleAssets(clinicAdmin=True)
        )
        self.officerFormBtn = self.controller.buttonCreator(
            ipath="assets/Registration/OfficerFormButton.png",
            x=1420, y=880, classname="officerformbtn", root=self,
            buttonFunction=lambda: self.loadRoleAssets(govofficer=True)
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
        self.password.insert(0, "password")
        self.confirmpassword.delete(0, END)
        self.confirmpassword.insert(0, "password")
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

    def loadRegThread(self, role):
        t = threading.Thread(target=self.loadReg, args=(role,))
        t.daemon = True
        t.start()

    def loadReg(self, role):
        toast = ToastNotification(
            title="Please be patient", message="We are loading the Registration Form for you", bootstyle=INFO)
        toast.show_toast()
        # Create a structure to split institutions and their schools
        # an Institution has many Schools
        # A school has many Programmes
        # A programme has many modules
        # I.E IICP -> SOC -> BCSCU -> INT4004CEM
        self.instDict = {}
        self.fullInfo = self.loadAllDetailsForRegistration()
        toast.hide_toast()
        successtoast = ToastNotification(
            title="Success!", message="You can now register.", bootstyle=SUCCESS, duration=1000)
        successtoast.show_toast()
        for inst in self.fullInfo:
            schoolsDict = {}
            if inst.school == []:
                self.instDict[f"{inst.institutionCode}"] = {
                    "schools": schoolsDict,
                }
                continue
            for school in inst.school:
                progDict = {}
                if school.programme == []:
                    schoolsDict[f"{school.schoolCode}"] = {
                        "programmes": progDict,
                    }
                    continue
                for programme in school.programme:
                    modList = []
                    if programme.modules == []:
                        progDict[f"{programme.programmeCode}"] = {
                            "modules": modList,
                        }
                        continue
                    for module in programme.modules:
                        modList.append(module.moduleTitle)
                    progDict[f"{programme.programmeCode}"] = {
                        "modules": modList,
                    }
                schoolsDict[f"{school.schoolCode}"] = {
                    "programmes": progDict,
                }
            self.instDict[f"{inst.institutionCode}"] = {
                "schools": schoolsDict,
            }
        institutionlist = list(self.instDict.keys())
        lists = {
            "institution": institutionlist,
        }
        self.institution = StringVar()
        self.school = StringVar()
        self.tenure = StringVar()
        self.programme = StringVar()
        self.course1 = StringVar()
        self.course2 = StringVar()
        self.course3 = StringVar()
        self.course4 = StringVar()
        if role == "teacher":
            self.tenure = StringVar()
        elif role == "student":
            self.session = StringVar()
        vars = {
            "institution": self.institution,
            "tenure": self.tenure,
        } if role == "teacher" else {
            "institution": self.institution,
            "session": self.session,
        }
        positions = {
            "institution": {"x": 160, "y": 660, "width": 240, "height": 40},
            "tenure": {"x": 520, "y": 660, "width": 240, "height": 40},
        } if role == "teacher" else {
            "institution": {"x": 160, "y": 660, "width": 240, "height": 40},
            "session": {"x": 520, "y": 660, "width": 240, "height": 40},
        }

        for name, values in lists.items():
            self.controller.menubuttonCreator(
                xpos=positions[name]["x"], ypos=positions[name]["y"], width=positions[name]["width"], height=positions[name]["height"],
                root=self.frameref, classname=name, text=f"Select {name}", listofvalues=values,
                variable=vars[name], font=("Helvetica", 10),
                command=lambda name=name: [
                    self.loadSchoolMenubuttons(vars[name].get())]
            )
        # tenure menu button
        if role == "teacher":
            tenurelist = ["FULLTIME", "PARTTIME"]
            positionKey = positions["tenure"]
            classname = "tenure"
            varKey = vars["tenure"]
        elif role == "student":
            sessionlist = ["APR2023", "AUG2023", "JAN2024"]
            positionKey = positions["session"]
            classname = "session"
            varKey = vars["session"]

        self.controller.menubuttonCreator(
            xpos=positionKey["x"], ypos=positionKey["y"], width=positionKey["width"], height=positionKey["height"],
            root=self.frameref, classname=classname, text=f"Select {classname.title()}", listofvalues=tenurelist if role == "teacher" else sessionlist,
            variable=varKey, font=("Helvetica", 10),
            command=lambda: [print(f"{vars[f'{classname}'].get()}")]
        )
        entries = {
            "fullname": self.controller.widgetsDict[f"{self.name}fullname"],
            "email": self.controller.widgetsDict[f"{self.name}email"],
            "password": self.controller.widgetsDict[f"{self.name}passent"],
            "confirmpassword": self.controller.widgetsDict[f"{self.name}confpassent"],
            "contactnumber": self.controller.widgetsDict[f"{self.name}contactnumber"],
            "captcha": self.controller.widgetsDict[f"{self.name}captcha"]
        }

        def checkCaptchaCorrect():
            if self.validate_captcha(entries["captcha"].get()):
                toast = ToastNotification(
                    title="Captcha Correct",
                    message="Captcha is correct",
                    duration=3000,
                    bootstyle="success"
                )
                toast.show_toast()
            else:
                pass

        self.controller.buttonCreator(r"Assets/Login Page with Captcha/ValidateInfoButton.png", 600, 560, classname="validateinfobtn", root=self.frameref,
                                      buttonFunction=lambda: [
                                          checkCaptchaCorrect()])
        self.controller.buttonCreator(r"Assets/Login Page with Captcha/regeneratecaptcha.png", 680, 420,
                                      classname="regeneratecaptcha", root=self.frameref,
                                      buttonFunction=lambda: self.generateCaptchaChallenge())
        if role == "teacher":
            self.controller.buttonCreator(
                r"Assets/Login Page with Captcha/CompleteRegSignIn.png", 1240, 980,
                classname="completeregbutton", buttonFunction=lambda: self.send_data(
                    data={
                        "fullName": entries["fullname"].get(),
                        "email": entries["email"].get(),
                        "password": self.encryptPassword(entries["password"].get()),
                        "confirmPassword": self.encryptPassword(entries["confirmpassword"].get()),
                        "contactNo": entries["contactnumber"].get(),
                        "currentCourses": [self.course1.get(), self.course2.get(), self.course3.get(), self.course4.get()],
                        "institution": self.institution.get(),
                        "school":  self.school.get(),
                        "tenure": self.tenure.get(),
                        "programme": self.programme.get(),
                        "role": "LECTURER"
                    }
                ),
                root=self.parent
            )
            self.controller.widgetsDict["skipbutton"].grid()
        elif role == "student":
            self.controller.buttonCreator(
                r"Assets/Login Page with Captcha/CompleteRegSignIn.png", 1240, 980,
                classname=f"completeregbutton", buttonFunction=lambda: self.send_data(
                    data={
                        "fullName": entries["fullname"].get(),
                        "email": entries["email"].get(),
                        "password": self.encryptPassword(entries["password"].get()),
                        "confirmPassword": self.encryptPassword(entries["confirmpassword"].get()),
                        "contactNo": entries["contactnumber"].get(),
                        "currentCourses": [self.course1.get(), self.course2.get(), self.course3.get(), self.course4.get()],
                        "institution": self.institution.get(),
                        "school":  self.school.get(),
                        "session": self.session.get(),
                        "programme": self.programme.get(),
                        "role": "STUDENT"
                    }
                ),
                root=self.parent
            )
            self.controller.widgetsDict["skipbutton"].grid()

    # def generateCaptchaChallenge(self):
    #     # fonts=[r"Fonts/AvenirNext-Regular.ttf", r"Fonts/SF-Pro.ttf"]
    #     image = ImageCaptcha(width=260, height=80, )
    #     # random alphanumeric string of length 6
    #     captcha_text = ''.join(random.choices(
    #         string.ascii_uppercase + string.digits, k=6))
    #     data = image.generate(captcha_text)
    #     image.write(captcha_text, r"Assets/Login Page with Captcha/captcha.png")
    #     self.captchavar.set(captcha_text)
    #     self.controller.labelCreator(
    #         imagepath=r"Assets/Login Page with Captcha/captcha.png",
    #         xpos=420, ypos=420, classname="imagecaptchachallenge",
    #         root=self.frameref
    #     )

    def checkDuplicateModules(self, courseNum, course, originalModules):
        vars = {
            "course1": self.course1,
            "course2": self.course2,
            "course3": self.course3,
            "course4": self.course4,
        }
        positions = {
            "course1": {"x": 160, "y": 800, "width": 280, "height": 40},
            "course2": {"x": 160, "y": 860, "width": 280, "height": 40},
            "course3": {"x": 480, "y": 800, "width": 280, "height": 40},
            "course4": {"x": 480, "y": 860, "width": 280, "height": 40},
        }
        modules = originalModules.copy()
        checkedcourseNum = courseNum
        checkedcourse = course
        selectedCourses = [self.course1.get(), self.course2.get(
        ), self.course3.get(), self.course4.get()]
        # print("The selected courses are,", selectedCourses)
        # Check for duplicates
        if selectedCourses.count(checkedcourse) > 1:
            # Will be overriding the one before the current one
            for i, x in enumerate(selectedCourses, 1):
                if x == checkedcourse and i != int(checkedcourseNum[-1]):
                    # print("Removing", (i, x))
                    vars[f"course{i}"].set("")
                    self.controller.menubuttonCreator(
                        xpos=positions[f"course{i}"]["x"], ypos=positions[f"course{i}"]["y"], width=positions[
                            f"course{i}"]["width"], height=positions[f"course{i}"]["height"],
                        root=self.frameref, classname=f"course{i}", text=f"Select Module {i}", listofvalues=modules,
                        variable=vars[f"course{i}"], font=("Helvetica", 10),
                        command=lambda c=f"course{i}": [
                            self.checkDuplicateModules(c, vars[c].get(), modules)]
                    )

    def encryptPassword(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def validatePassword(self, password: str, encrypted: str) -> str:
        return bcrypt.checkpw(password.encode("utf-8"), encrypted.encode("utf-8"))

    def prismaFormSubmit(self,  data: dict):
        # LECTURER OR STUDENT
        prisma = self.controller.mainPrisma
        emailCheck = prisma.userprofile.find_first(
            where={
                "email": data["email"]
            }
        )
        if emailCheck:
            toast = ToastNotification(
                title="Error",
                message="Email already exists, please use another email address",
                bootstyle="danger",
                duration=5000,
            )
            toast.show_toast()
            self.gif.grid_forget()
            return
        try:
            if data["role"] == "STUDENT":
                school = prisma.school.find_first(
                    where={
                        "schoolCode": data["school"]
                    }
                )
                student = prisma.student.create(
                    data={
                        "userProfile": {
                            "create": {
                                "fullName": data["fullName"],
                                "email": data["email"],
                                "password": data["password"],
                                "contactNo": data["contactNo"],
                            }
                        },
                        "school": {
                            "connect": {
                                "id": school.id
                            }
                        },
                        "session": data["session"],
                    }
                )
                modulestoenroll = []
                for module in data["currentCourses"]:
                    module = prisma.module.find_first(
                        where={
                            "moduleTitle": module
                        }
                    )
                    modulestoenroll.append(module.id)
                for i in range(len(modulestoenroll)):
                    student = prisma.student.find_first(
                        where={
                            "userProfile": {
                                "is": {
                                    "email": data["email"]
                                }
                            }
                        }
                    )
                    update = prisma.student.update(
                        where={
                            "id": student.id
                        },
                        data={
                            "modules": {
                                "create": {
                                    "enrollmentGrade": 0,
                                    "moduleId": modulestoenroll[i]
                                }
                            }
                        },
                        include={
                            "userProfile": True,
                            "modules": True,
                        }
                    )
                welcomemessage = f"Welcome, {update.userProfile.fullName}!"
                toast = ToastNotification(
                    title="Success",
                    message=welcomemessage,
                    duration=3000,
                    bootstyle=SUCCESS
                )
                toast.show_toast()
                self.gif.grid_forget()
            elif data["role"] == "LECTURER":
                school = prisma.school.find_first(
                    where={
                        "schoolCode": data["school"]
                    }
                )
                lecturer = prisma.lecturer.create(
                    data={
                        "userProfile": {
                            "create": {
                                "fullName": data["fullName"],
                                "email": data["email"],
                                "password": data["password"],
                                "contactNo": data["contactNo"],
                                "isAdmin": True,
                            }
                        },
                        "school": {
                            "connect": {
                                "id": school.id
                            }
                        },
                        "tenure": data["tenure"],
                    },
                    include={
                        "userProfile": True,
                    }
                )
                for modules in data["currentCourses"]:
                    if modules == "":
                        continue
                    module = prisma.module.find_first(
                        where={
                            "moduleTitle": modules
                        }
                    )
                    newmodule = prisma.module.update(
                        where={
                            "id": module.id
                        },
                        data={
                            "lecturer": {
                                "connect": {
                                    "id": lecturer.id
                                }
                            }
                        },
                        include={
                            "lecturer": {
                                "include": {
                                    "userProfile": True
                                }
                            },
                            "moduleEnrollments": {
                                "include": {
                                    "student": {
                                        "include": {
                                            "userProfile": {
                                                "include": {
                                                    "student": True
                                                }
                                            }
                                        }
                                    },
                                }
                            },
                        }
                    )
                toast = ToastNotification(
                    title="Success",
                    message=f"Welcome, {lecturer.userProfile.fullName}!",
                    duration=3000,
                    bootstyle=SUCCESS
                )
                toast.show_toast()
                self.gif.grid_forget()
        except Exception as e:
            self.gif.grid_forget()
            toast = ToastNotification(
                title="Error",
                message=f"There was an error creating your account. Please try again. {e}",
                duration=3000
            )
            toast.show_toast()
            return
        self.controller.loadSignIn()

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

    def send_data(self, data: dict):
        if self.validateData(data) == False:
            return
        t = threading.Thread(target=self.prismaFormSubmit, args=(data,))
        self.gif = AnimatedGif(
            parent=self, controller=self.controller,
            xpos=0, ypos=0, bg="#344557",
            framewidth=800, frameheight=920, classname="loadingspinner",
            imagepath=r"Assets/spinners.gif", imagexpos=200, imageypos=300)
        self.controller.labelCreator(
            r"Assets/signinguplabel.png", 140, 620, "signinguplabel", self.gif)
        t.daemon = True
        t.start()

    def loadSignIn(self):
        self.grid_remove()

    def loadRoleAssets(self, patient: bool = False, doctor: bool = False, clinicAdmin: bool = False, govofficer: bool = False):
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
