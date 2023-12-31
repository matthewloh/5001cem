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
        self.doctorList()

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
        self.viewDoctorFrame = self.controller.frameCreator(
            x=0, y=0, classname="doctorframe", root=self, framewidth=1680, frameheight=1080
        )
        self.editDoctorFrame = self.controller.frameCreator(
            x=0, y=0, classname="editdoctorframe", root=self, framewidth=1680, frameheight=1080
        )
        self.unloadStackedFrames()

    def unloadStackedFrames(self):
        self.doctorListFrame.grid_remove()
        self.viewDoctorFrame.grid_remove()
        self.editDoctorFrame.grid_remove()

    def createElements(self):
        self.bg = self.controller.labelCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/AdminDashboard/Homepage.png",
            x=0, y=0, classname="homepage", root=self
        )
        self.imgLabels = [
            ("assets/Dashboard/ClinicAdminAssets/Add&DeleteList/DoctorList.png",
             0, 0, "listimage", self.doctorListFrame),
            ("assets/Dashboard/ClinicAdminAssets/Add&DeleteList/DoctorInfo.png",
             0, 0, "doctorimage", self.viewDoctorFrame),
            ("assets/Dashboard/ClinicAdminAssets/Add&DeleteList/EditDoctor.png",
             0, 0, "editdoctorbg", self.editDoctorFrame)
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
                self.controller.threadCreator(target=self.doctorsScrolledFrame)],
            text="Select Speciality"
        )
        self.doctorsScrolledFrame = ScrolledFrame(
            master=self, width=900, height=350, autohide=True, bootstyle="minty-bg")
        self.doctorsScrolledFrame.place(
            x=683, y=150, width=900, height=350
        )
        initialCoordinates = (20, 20)
        for doctor in self.doctors:
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
            command=lambda: [self.controller.threadCreator(target=self.statusScrolledFrame)],
            text="Select Time Schedules",
            startTime=s_time, endTime=e_time, interval=30,
            isTimeSlotFmt=True,
        )
        self.statusScrolledFrame = ScrolledFrame(
            master=self, width=900, height=350, autohide=True, bootstyle="minty-bg")
        self.statusScrolledFrame.place(
            x=683, y=670, width=900, height=350
        )
        initialCoordinates = (20, 20)
        for doctor in self.doctors:
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

    def dashboardButtons(self):
        d = {
            "adminDashboard": [
                "assets/Dashboard/ClinicAdminAssets/AdminDashboard/View&DeleteDoctor.png",
                "assets/Dashboard/ClinicAdminAssets/AdminDashboard/ReturnButton.png",
                "assets/Dashboard/ClinicAdminAssets/AdminDashboard/ReturnButton.png",
                "assets/Dashboard/ClinicAdminAssets/ScrollFrame/updatelist.png",
                "assets/Dashboard/ClinicAdminAssets/AdminDashboard/ReturnButton.png",
                "assets/Dashboard/ClinicAdminAssets/Update.png",
                "assets/Dashboard/ClinicAdminAssets/Save.png"
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
            x=60, y=60, classname="doctorreturnbutton", root=self.doctorListFrame,
            buttonFunction=lambda: [self.doctorListFrame.grid_remove()],
        )
        self.returnDoctorListbutton = self.controller.buttonCreator(
            ipath=d["adminDashboard"][2],
            x=60, y=60, classname="return_to_doctorlist", root=self.viewDoctorFrame,
            buttonFunction=lambda: [self.viewDoctorFrame.grid_remove()],
        )
        self.UpdateBtn = self.controller.buttonCreator(
            ipath=d["adminDashboard"][3],
            x=1320, y=180, classname="viewDoctorrefresh", root=self.doctorListFrame,
            buttonFunction=lambda:
                [self.controller.threadCreator(
                    target=self.doctorList)],
                isPlaced=True
        )
        self.returnDoctorInfobutton = self.controller.buttonCreator(
            ipath=d["adminDashboard"][4],
            x=60, y=60, classname="return_to_doctorinfo", root=self.editDoctorFrame,
            buttonFunction=lambda: [self.editDoctorFrame.grid_remove()],
        )
        self.updateInfobutton = self.controller.buttonCreator(
            ipath=d["adminDashboard"][5],
            x=1430, y=50, classname="update_doctorinfo", root=self.viewDoctorFrame,
            buttonFunction=lambda: [self.controller.threadCreator(
                    target=self.editDoctorInfo)],
        )
        self.editInfobutton = self.controller.buttonCreator(
            ipath=d["adminDashboard"][6],
            x=1440, y=50, classname="edit_doctorinfo", root=self.editDoctorFrame,
            buttonFunction=lambda: [self.controller.threadCreator(
                    target=self.editDoctorInfo)],
        )


    def doctorList(self):
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
        self.ListScrolledFrame.place(x=60, y=320, width=1520, height=650)
        COORDS = (20, 20)
        for doctor in doctors:
            doctor.user.fullName
            X = COORDS[0]
            Y = COORDS[1]
            R = self.ListScrolledFrame
            FONT = ("Inter", 12)
            self.controller.labelCreator(
                ipath="assets/Dashboard/ClinicAdminAssets/ScrollFrame/list.png",
                x=X, y=Y, classname=f"doctorlist{doctor.id}", root=R,
                isPlaced=True,
            )

            d = {
                "scrollButton": [
                    "assets/Dashboard/ClinicAdminAssets/ScrollFrame/edit.png",
                    "assets/Dashboard/ClinicAdminAssets/ScrollFrame/view.png",
                    "assets/Dashboard/ClinicAdminAssets/ScrollFrame/delete.png", 
                ]
            }
            self.editdoctorbutton = self.controller.buttonCreator(
                ipath=d["scrollButton"][0],
                x=X+1120, y=Y+35, classname=f"editbutton{doctor.id}", root=R,
                buttonFunction=lambda d=doctor: [self.editDoctorInfo(d)],
                isPlaced=True
            )
            self.viewdoctorbutton = self.controller.buttonCreator(
                ipath=d["scrollButton"][1],
                x=X+1240, y=Y+35, classname=f"viewbutton{doctor.id}", root=R,
                buttonFunction=lambda d=doctor: [self.manageDoctorInfo(d)],
                isPlaced=True
            )
            self.deletedoctorbutton = self.controller.buttonCreator(
                ipath=d["scrollButton"][2],
                x=X+1360, y=Y+35, classname=f"deletebutton{doctor.id}", root=R,
                buttonFunction=lambda: [self.controller.threadCreator(
                    self.deleteDoctor)],
                isPlaced=True
            )

            doctorName = self.controller.scrolledTextCreator(
                x=X+50, y=Y+40, width=200, height=80, root=R, classname=f"{doctor.id}_name",
                bg="#f1feff", hasBorder=False,
                text=doctor.user.fullName, font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            doctorSpeciality = self.controller.scrolledTextCreator(
                x=X+290, y=Y+40, width=260, height=80, root=R, classname=f"{doctor.id}_speciality",
                bg="#f1feff", hasBorder=False,
                text=doctor.speciality, font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            doctorUserID = self.controller.scrolledTextCreator(
                x=X+610, y=Y+35, width=200, height=80, root=R, classname=f"{doctor.id}_userId",
                bg="#f1feff", hasBorder=False,
                text=doctor.userId, font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            doctorClinicID = self.controller.scrolledTextCreator(
                x=X+880, y=Y+35, width=200, height=80, root=R, classname=f"{doctor.id}_clinicId",
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
                self.doctorList, cancelled=True)
        else:
            return
    
    def viewDoctorInfo(self, req: Doctor):
        prisma = self.prisma
        prisma.doctor.update(
            where={
                "clinic": {"is": {"admin": {"some": {"userId": self.user.id}}}}
            },
            include={
                "user": True,
                "clinic": True,
                "appointment": True
            }
        )
        self.controller.threadCreator(self.manageDoctorInfo, confirmed=True)
    
    def manageDoctorInfo(self, req: Doctor):
        self.controller.threadCreator(
            self.createManageDoctor, req=req)

    def createManageDoctor(self, req: Doctor):
        R = self.viewDoctorFrame
        doctorName = f"Doctor: {req.user.fullName}"
        doctorSpeciality = f"Speciality:{req.speciality}"
        educationHistory = f"EducationHistory:{req.educationHistory}"
        employmentHistory = f"EmploymentHistory:{req.employmentHistory}"
        clinic = f"Clinic:{req.clinic}"
        appointments = f"App:{req.appointments}"
        doctorApptSchedule = f"Schedule:{req.doctorApptSchedule}"
        
        self.controller.scrolledTextCreator(
            x=280, y=320, width=480, height=60, root=R, classname="manage_doctorname_gender_age",
            bg=WHITE, hasBorder=BLACK,
            text=f"{doctorName}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )
        self.controller.scrolledTextCreator(
            x=280, y=420, width=480, height=60, root=R, classname="manage_speciality",
            bg=WHITE, hasBorder=BLACK,
            text=f"{doctorSpeciality}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )
        self.controller.scrolledTextCreator(
            x=80, y=540, width=680, height=100, root=R, classname="manage_educationhistory",
            bg=WHITE, hasBorder=BLACK,
            text=f"{educationHistory}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
        )
        self.controller.scrolledTextCreator(
            x=80, y=700, width=680, height=100, root=R, classname="manage_employmenthistory",
            bg=WHITE, hasBorder=BLACK,
            text=f"{employmentHistory}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
        )
        self.controller.scrolledTextCreator(
            x=900, y=320, width=680, height=100, root=R, classname="manage_clinic",
            bg=WHITE, hasBorder=BLACK,
            text=f"{clinic}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
        )
        self.controller.scrolledTextCreator(
            x=900, y=480, width=680, height=100, root=R, classname="manage_appointments",
            bg=WHITE, hasBorder=BLACK,
            text=f"{appointments}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
        )
        self.controller.scrolledTextCreator(
            x=900, y=640, width=680, height=100, root=R, classname="manage_schedules",
            bg=WHITE, hasBorder=BLACK,
            text=f"{doctorApptSchedule}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
        )

        self.viewDoctorFrame.grid()
        self.viewDoctorFrame.tkraise()

    def resetDoctorInfo(self, req: Doctor):
        prisma = self.prisma
        prisma.doctor.update(
            where={
                "clinic": {"is": {"admin": {"some": {"userId": self.user.id}}}}
            },
            include={
                "user": True,
                "clinic": True,
                "appointment": True
            }
        )
        self.controller.threadCreator(self.editDoctorInfo, confirmed=True)

    def editDoctorInfo(self, req: Doctor):
        self.controller.threadCreator(
            self.editManageDoctor, req=req)

    def editManageDoctor(self, req: Doctor):
        R=self.editDoctorFrame
        self.seedDataBtn = self.controller.buttonCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/EditSeed.png",
            x=680, y=180, classname="doctordatabtn", root=R,
            buttonFunction=lambda d=req: self.doctorSeed_data(d)
        )
        EC= self.controller.ttkEntryCreator
        self.doctorname = EC(
            x=280, y=320, width=480, height=60, root=R, classname="edit_doctorname_gender_age",
            font=("Inter", 12), fg=BLACK,
        )
        self.doctorspeciality = EC(
            x=280, y=420, width=480, height=60, root=R, classname="edit_speciality",
            font=("Inter", 12), fg=BLACK,
        )
        self.educationhistory = EC(
            x=80, y=540, width=680, height=100, root=R, classname="edit_educationhistory",
            font=("Inter", 12), fg=BLACK,
        )
        self.employmenthistory = EC(
            x=80, y=700, width=680, height=100, root=R, classname="edit_employmenthistory",
            font=("Inter", 12), fg=BLACK,
        )
        self.clinicname = EC(
            x=900, y=320, width=680, height=100, root=R, classname="edit_clinic",
            font=("Inter", 12), fg=BLACK,
        )
        self.doctorappointment = EC(
            x=900, y=480, width=680, height=100, root=R, classname="edit_appointments",
            font=("Inter", 12), fg=BLACK,
        )
        self.appschedules = EC(
            x=900, y=640, width=680, height=100, root=R, classname="edit_schedules",
            font=("Inter", 12), fg=BLACK,
        )
        self.editDoctorFrame.grid()
        self.editDoctorFrame.tkraise()

    def doctorSeed_data(self, req:Doctor):
        self.doctorname.delete(0, END)
        self.doctorname.insert(0,f"Doctor: {req.user.fullName}")
        self.doctorspeciality.delete(0, END)
        self.doctorspeciality.insert(0,f"Speciality:{req.speciality}")
        self.educationhistory.delete(0, END)
        self.educationhistory.insert(0,f"EducationHistory:{req.educationHistory}")
        self.employmenthistory.delete(0, END)
        self.employmenthistory.insert(0,f"EmploymentHistory:{req.employmentHistory}")
        self.clinicname.delete(0, END)
        self.clinicname.insert(0,f"Clinic:{req.clinic}")
        self.doctorappointment.delete(0, END)
        self.doctorappointment.insert(0,f"App:{req.appointments}")
        self.appschedules.delete(0, END)
        self.appschedules.insert(0,f"Schedule:{req.doctorApptSchedule}")
