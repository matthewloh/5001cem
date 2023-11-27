from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.mainDashboard import Dashboard
from resource.basewindow import ElementCreator, gridGenerator
from resource.static import *
from tkinter import *
from prisma.models import Clinic
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame

from views.mainBrowseClinic import MainBrowseClinic
from views.mainGRDRequests import MainGRDRequestsInterface
from views.mainPatientRequests import MainPatientRequestsInterface
from views.mainViewAppointments import MainViewAppointmentsInterface
from prisma.models import Doctor
from datetime import datetime, timedelta
import datetime as dt
from tkinter import messagebox

class ClinicAdminDashboard(Frame):
    def __init__(self, parent: Dashboard = None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="primarypanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.prisma = self.controller.mainPrisma
        self.user = self.parent.user
        self.createFrames()
        self.createElements()
        self.dashboardButtons()
        self.loadClinics()
        self.createList()
        self.addAnddeleteList()

    def loadAssets(self):
        self.pfp = self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/AdminProfilePicture.png",
            x=20, y=100, classname="profilepicture", root=self.parent,
            buttonFunction=lambda: [print('hello')]
        )
        d = {
            "clinicAdmin": [
                "assets/Dashboard/ClinicAdminAssets/AdminManageClinic.png",
                "assets/Dashboard/ClinicAdminAssets/AdminViewPatientRequests.png",
                "assets/Dashboard/ClinicAdminAssets/AdminViewDoctorSchedule.png",
                "assets/Dashboard/ClinicAdminAssets/AdminGRDRequests.png"
            ]
        }
        self.browseClinic = self.controller.buttonCreator(
            ipath=d["clinicAdmin"][0],
            x=20, y=380, classname="browseclinic_chip", root=self.parent,
            buttonFunction=lambda: [self.loadBrowseClinic()],
        )
        self.viewPatients = self.controller.buttonCreator(
            ipath=d["clinicAdmin"][1],
            x=20, y=460, classname="viewpatients_chip", root=self.parent,
            buttonFunction=lambda: [self.loadViewPatients()],
        )
        self.viewDoctorSchedule = self.controller.buttonCreator(
            ipath=d["clinicAdmin"][2],
            x=20, y=540, classname="viewdoctorschedule_chip", root=self.parent,
            buttonFunction=lambda: [self.loadViewAppointments()],
        )
        self.viewGRDRequests = self.controller.buttonCreator(
            ipath=d["clinicAdmin"][3],
            x=20, y=620, classname="grdrequests_chip", root=self.parent,
            buttonFunction=lambda: [self.loadGRDRequests()],
        )

    def loadBrowseClinic(self):
        try:
            self.mainInterface.primarypanel.grid()
            self.mainInterface.primarypanel.tkraise()
        except:
            self.mainInterface = MainBrowseClinic(
                controller=self.controller, parent=self.parent)
            self.mainInterface.loadRoleAssets(clinicAdmin=True)

    def loadViewPatients(self):
        try:
            self.patientRequests.primarypanel.grid()
            self.patientRequests.primarypanel.tkraise()
        except:
            self.patientRequests = MainPatientRequestsInterface(
                controller=self.controller, parent=self.parent)
            self.patientRequests.loadRoleAssets(clinicAdmin=True)

    def loadViewAppointments(self):
        try:
            self.appointments.primarypanel.grid()
            self.appointments.primarypanel.tkraise()
        except:
            self.appointments = MainViewAppointmentsInterface(
                controller=self.controller, parent=self.parent)
            self.appointments.loadRoleAssets(clinicAdmin=True)

    def loadGRDRequests(self):
        try:
            self.grdRequests.primarypanel.grid()
            self.grdRequests.primarypanel.tkraise()
        except:
            self.grdRequests = MainGRDRequestsInterface(
                controller=self.controller, parent=self.parent)
            self.grdRequests.loadRoleAssets(clinicAdmin=True)

    def createFrames(self):
        self.doctorListFrame = self.controller.frameCreator(
            x=0, y=0, classname="listframe", root=self, framewidth=1680, frameheight=1080
        )
        self.manageDoctorFrame = self.controller.frameCreator(
            x=0, y=0, classname="doctorframe", root=self, framewidth=1680, frameheight=1080
        )
        self.unloadStackedFrames()

    def unloadStackedFrames(self):
        self.doctorListFrame.grid_remove()
        self.manageDoctorFrame.grid_remove()

    def createElements(self):
        self.bg = self.controller.labelCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/AdminDashboard/Homepage.png",
            x=0, y=0, classname="homepage", root=self
        )
        self.imgLabels = [
            ("assets/Dashboard/ClinicAdminAssets/Add&DeleteList/DoctorListManagement.png",
             0, 0, "listimage", self.doctorListFrame),
            ("assets/Dashboard/ClinicAdminAssets/Add&DeleteList/ManageDoctors.png",
             0, 0, "doctorimage", self.manageDoctorFrame)
        ]
        self.controller.settingsUnpacker(self.imgLabels, "label")

    def loadClinics(self):
        prisma = self.prisma
        self.clinics = prisma.clinic.find_many(
            where={
                "admin": {"some": {"userId": self.user.id}}
            }
        )
        self.clinic: Clinic = self.clinics[0]
        self.clinicSelected = StringVar()
        keyOptionsForMenuButton = list(
            map(lambda clinic: clinic.name, self.clinics))
        self.clinicMenuButton = self.controller.menubuttonCreator(
            x=140, y=240, classname="clinicmenubutton", root=self,
            width=400, height=80, listofvalues=keyOptionsForMenuButton,
            variable=self.clinicSelected,
            command=lambda: [
                self.setClinic(self.clinicSelected.get()),
                self.loadDoctorsByClinic(),
            ],
            text="Select Clinic"
        )
        self.clinicSelected.set(self.clinics[0].name)
        self.clinicMenuButton.configure(
            text=self.clinicSelected.get() if self.clinicSelected.get() else "Select Clinic"
        )
        self.setClinic(self.clinicSelected.get())
        self.loadDoctorsByClinic()

    def setClinic(self, option: str):
        self.clinic = list(
            filter(lambda clinic: clinic.name == option, self.clinics))[0]

    def loadDoctorsByClinic(self):
        self.loadDoctorsAndFilterByAppointment()
        self.loadDoctorsAndFilterBySpeciality()

    def loadDoctorsAndFilterBySpeciality(self):
        prisma = self.prisma
        self.doctors = prisma.doctor.find_many(
            where={
                "clinicId": self.clinic.id
            },
            include={
                "user": True,
            }
        )
        self.specialitiesAndDoctors = {}
        for doctor in self.doctors:
            if doctor.speciality not in self.specialitiesAndDoctors.keys():
                self.specialitiesAndDoctors[doctor.speciality] = []
            self.specialitiesAndDoctors[doctor.speciality].append(doctor)
        self.specialitySelected = StringVar()
        keyOptionsForMenuButton = list(self.specialitiesAndDoctors.keys())
        self.specialityMenuButton = self.controller.menubuttonCreator(
            x=140, y=440, classname="specialitymenubutton", root=self,
            width=400, height=80, listofvalues=keyOptionsForMenuButton,
            variable=self.specialitySelected,
            command=lambda: [
                self.loadDoctorsBySpeciality(self.specialitySelected.get())],
            text="Select Speciality"
        )

    def loadDoctorsAndFilterByAppointment(self):
        prisma = self.prisma
        self.doctors = prisma.doctor.find_many(
            where={
                "clinic": {"is": {"admin": {"some": {"userId": self.user.id}}}}
            },
            include={
                "user": True,
            }
        )
        self.appointmentsAndDoctors = {}
        for doctor in self.doctors:
            if doctor.doctorApptSchedule not in self.appointmentsAndDoctors.keys():
                self.appointmentsAndDoctors[doctor.doctorApptSchedule] = []
            self.appointmentsAndDoctors[doctor.doctorApptSchedule].append(
                doctor)
        self.timeSlotSelected = StringVar()
        s_time = self.clinic.clinicHrs.split(" - ")[0]
        e_time = self.clinic.clinicHrs.split(" - ")[1]
        self.doctorApptScheduleMenuButton = self.controller.timeMenuButtonCreator(
            x=140, y=840, classname="doctorApptSchedulemenubutton", root=self,
            width=400, height=80,
            variable=self.timeSlotSelected,
            command=lambda: [self.loadAvailableDoctorsByTimeSlot(
                self.timeSlotSelected.get())],
            text="Select Time Schedules",
            startTime=s_time, endTime=e_time, interval=30,
            isTimeSlotFmt=True,
        )

    def loadAvailableDoctorsByTimeSlot(self, option: str):
        doctors = self.appointmentsAndDoctors[option]
        h = len(doctors) * 100
        if h < 350:
            h = 350
        self.statusScrolledFrame = ScrolledFrame(
            master=self, width=900, height=h, autohide=True, bootstyle="minty-bg")
        self.statusScrolledFrame.place(
            x=680, y=670, width=900, height=350
        )
        initialCoordinates = (20, 20)
        for doctor in doctors:
            x = initialCoordinates[0]
            y = initialCoordinates[1]
            self.controller.textElement(
                ipath="assets/Dashboard/ClinicAdminAssets/ScrollFrame/scrolldashboardbutton.png",
                x=x, y=y, classname=f"doctorstatusbg{doctor.id}", root=self.statusScrolledFrame,
                text=f"{doctor.user.fullName}", size=30, font=INTER,
                isPlaced=True,
                buttonFunction=lambda d=doctor: [print(d)]
            )
            initialCoordinates = (
                initialCoordinates[0], initialCoordinates[1] + 100
            )

    def loadDoctorsBySpeciality(self, option):
        doctors = self.specialitiesAndDoctors[option]
        h = len(doctors) * 100
        if h < 350:
            h = 350
        self.doctorsScrolledFrame = ScrolledFrame(
            master=self, width=900, height=h, autohide=True, bootstyle="minty-bg")
        self.doctorsScrolledFrame.place(
            x=680, y=150, width=900, height=350
        )
        initialCoordinates = (20, 20)
        for doctor in doctors:
            x = initialCoordinates[0]
            y = initialCoordinates[1]
            self.controller.textElement(
                ipath="assets/Dashboard/ClinicAdminAssets/ScrollFrame/scrolldashboardbutton.png",
                x=x, y=y, classname=f"doctorlistbg{doctor.id}", root=self.doctorsScrolledFrame,
                text=f"{doctor.user.fullName}", size=30, font=INTER,
                isPlaced=True,
                buttonFunction=lambda d=doctor: [print(d)]
            )
            initialCoordinates = (
                initialCoordinates[0], initialCoordinates[1] + 100
            )

    def dashboardButtons(self):
        d = {
            "adminDashboard": [
                "assets/Dashboard/ClinicAdminAssets/AdminDashboard/Add&DeleteDoctor.png",
                "assets/Appointments/ReturnButton.png",
                "assets/Appointments/ReturnButton.png",
            ]
        }
        self.Listbutton = self.controller.buttonCreator(
            ipath=d["adminDashboard"][0],
            x=140, y=640, classname="listbutton", root=self,
            buttonFunction=lambda: [
                self.doctorListFrame.grid(), self.doctorListFrame.tkraise()],
        )
        self.Returnbutton = self.controller.buttonCreator(
            ipath=d["adminDashboard"][1],
            x=60, y=40, classname="doctorreturnbutton", root=self.doctorListFrame,
            buttonFunction=lambda: [self.doctorListFrame.grid_remove()],
        )
        self.returnDoctorListbutton = self.controller.buttonCreator(
            ipath=d["adminDashboard"][2],
            x=20, y=40, classname="return_to_doctorlist", root=self.manageDoctorFrame,
            buttonFunction=lambda: [self.manageDoctorFrame.grid_remove()],
        )

    def createList(self):
        prisma = self.prisma
        doctors = prisma.doctor.find_many(
            where={
                "clinic": {"is": {"admin": {"some": {"userId": self.user.id}}}}
            },
            include={
                "user": True,
            }
        )
        h = len(doctors) * 100
        if h < 375:
            h = 375

        self.doctorsScrolledFrame = ScrolledFrame(
            master=self, width=920, height=h, autohide=True, bootstyle="minty-bg")
        self.doctorsScrolledFrame.place(
            x=685, y=150, width=900, height=350
        )
        initialCoordinates = (20, 20)
        for doctor in doctors:
            X = initialCoordinates[0]
            Y = initialCoordinates[1]
            self.controller.textElement(
                ipath="assets/Dashboard/ClinicAdminAssets/ScrollFrame/scrolldashboardbutton.png",
                x=X, y=Y, classname=f"doctorlistbg{doctor.id}", root=self.doctorsScrolledFrame,
                text=f"{doctor.user.fullName}", size=30, font=INTER,
                isPlaced=True,
                buttonFunction=lambda: [print(doctor)]
            )
            initialCoordinates = (
                initialCoordinates[0], initialCoordinates[1] + 100
            )

    def addAnddeleteList(self):
        prisma = self.prisma
        doctors = prisma.doctor.find_many(
            where={
                "clinic": {"is": {"admin": {"some": {"userId": self.user.id}}}}
            },
            include={
                "user": True,
            }
        )
        h = len(doctors) * 120
        if h < 650:
            h = 650
        self.ListScrolledFrame = ScrolledFrame(
            master=self.doctorListFrame, width=1500, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.ListScrolledFrame.grid_propagate(False)
        self.ListScrolledFrame.place(x=60, y=280, width=1520, height=650)
        COORDS = (20, 20)
        for doctor in doctors:
            doctor.user.fullName
            X = COORDS[0]
            Y = COORDS[1]
            R = self.ListScrolledFrame
            FONT = ("Inter", 12)
            self.controller.labelCreator(
                ipath="assets/Dashboard/ClinicAdminAssets/ScrollFrame/scrollbutton.png",
                x=X, y=Y, classname=f"doctorlist{doctor.id}", root=R,
                isPlaced=True,
            )

            d = {
                "scrollButton": [
                    "assets/Dashboard/ClinicAdminAssets/ScrollFrame/view.png",
                    "assets/Dashboard/ClinicAdminAssets/ScrollFrame/delete.png",
                ]
            }
            self.viewdoctorbutton = self.controller.buttonCreator(
                ipath=d["scrollButton"][0],
                x=X+1280, y=Y+30, classname=f"viewbutton{doctor.id}", root=R,
                buttonFunction=lambda: [self.manageDoctorFrame.grid(),self.manageDoctorFrame.tkraise()],
                isPlaced=True
            )
            self.deletedoctorbutton = self.controller.buttonCreator(
                ipath=d["scrollButton"][1],
                x=X+1360, y=Y+30, classname=f"deletebutton{doctor.id}", root=R,
                buttonFunction=lambda: [self.controller.threadCreator(
                    self.deleteDoctor)],
                isPlaced=True
            )

            doctorName = self.controller.scrolledTextCreator(
                x=X+50, y=Y+30, width=200, height=60, root=R, classname=f"{doctor.id}_name",
                bg="#f1feff", hasBorder=False,
                text=doctor.user.fullName, font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            doctorSpeciality = self.controller.scrolledTextCreator(
                x=X+290, y=Y+30, width=260, height=60, root=R, classname=f"{doctor.id}_speciality",
                bg="#f1feff", hasBorder=False,
                text=doctor.speciality, font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            doctorUserID = self.controller.scrolledTextCreator(
                x=X+610, y=Y+25, width=200, height=65, root=R, classname=f"{doctor.id}_userId",
                bg="#f1feff", hasBorder=False,
                text=doctor.userId, font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            doctorClinicID = self.controller.scrolledTextCreator(
                x=X+880, y=Y+25, width=200, height=65, root=R, classname=f"{doctor.id}_clinicId",
                bg="#f1feff", hasBorder=False,
                text=doctor.clinicId, font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            COORDS = (
                COORDS[0], COORDS[1] + 120
            )

    def deleteDoctor(self):
        result = messagebox.askyesno(
            "Delete Doctor", "Are you sure you want to delete this doctor account?",
        )
        if result:
            prisma = self.prisma
            prisma.doctor.update(
                where={
                "userId":self.user.id
                },
                data={
                    "clinic":{
                        "disconnect": True
                    }
                }
            )
            self.controller.threadCreator(
                self.addAnddeleteList, cancelled=True)
        else:
            return
    
    def createManageDoctor(self, req: Doctor):
        age = dt.datetime.now().year - req.user.dateOfBirth.year
        nameGenderAge = f"Doctor: {req.user.fullName}\n{req.user.gender}, {age} years old"
        doctorSpeciality = f"Speciality:{req.speciality}"
        educationHistory = f"EducationHistory:{req.educationHistory}"
        employmentHistory = f"EmploymentHistory:{req.employmentHistory}"
        self.controller.scrolledTextCreator(
            x=260, y=260, width=540, height=60, root=self.manageDoctorFrame, classname="manage_doctorname_gender_age",
            bg=WHITE, hasBorder=BLACK,
            text=f"{nameGenderAge}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )
        self.controller.scrolledTextCreator(
            x=260, y=360, width=540, height=60, root=self.manageDoctorFrame, classname="manage_speciality",
            bg=WHITE, hasBorder=BLACK,
            text=f"{doctorSpeciality}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )
        self.controller.scrolledTextCreator(
            x=40, y=500, width=760, height=160, root=self.manageDoctorFrame, classname="manage_educationhistory",
            bg=WHITE, hasBorder=BLACK,
            text=f"{educationHistory}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
        )
        self.controller.scrolledTextCreator(
            x=40, y=740, width=760, height=160, root=self.manageDoctorFrame, classname="manage_employmenthistory",
            bg=WHITE, hasBorder=BLACK,
            text=f"{employmentHistory}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
        )