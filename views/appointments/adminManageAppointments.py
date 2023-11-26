from __future__ import annotations
from typing import TYPE_CHECKING

from views.mainPatientRequests import MainPatientRequestsInterface
if TYPE_CHECKING:
    from views.mainDashboard import Dashboard
from tkinter import *
from tkinter import messagebox
from prisma.models import AppointmentRequest, Doctor
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.dialogs import Querybox
from ttkbootstrap.dialogs.dialogs import DatePickerDialog
from resource.basewindow import gridGenerator
from resource.static import *
from resource.basewindow import ElementCreator
import datetime as dt
from prisma.models import AppointmentRequest
from pendulum import timezone


class AdminManageAppointments(Frame):
    def __init__(self, parent: Dashboard = None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="appointmentspanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.user = self.parent.user
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.appointmentImgLabels()
        self.appointmentButtons()
        self.appointmentList()

    def createFrames(self):
        self.createAppointmentsFrame = self.controller.frameCreator(
            x=0, y=0, classname="createframe", root=self, framewidth=1680, frameheight=1080
        )
        self.manageAppointmentsFrame = self.controller.frameCreator(
            x=0, y=0, classname="manageframe", root=self, framewidth=1680, frameheight=1080
        )
        self.unloadStackedFrames()

    def unloadStackedFrames(self):
        self.createAppointmentsFrame.grid_remove()
        self.manageAppointmentsFrame.grid_remove()

    def appointmentImgLabels(self):
        self.bg = self.controller.labelCreator(
            ipath="assets/Appointments/Homepage/AppointmentViewBg.png",
            x=0, y=0, classname="appointmenthomepage", root=self
        )
        self.imgLabels = [
            ("assets/Appointments/Creation/CreationBg.png",
             0, 0, "creationimage", self.createAppointmentsFrame),
            ("assets/Appointments/Management/ManagementBg.png",
             0, 0, "manageimage", self.manageAppointmentsFrame)
        ]
        self.controller.settingsUnpacker(self.imgLabels, "label")

    def appointmentButtons(self):
        d = {
            "appointmentButtons": [
                "assets/Appointments/Homepage/CreateAppointments.png",
                "assets/Appointments/Homepage/ManageAppointments.png",
                "assets/Dashboard/ClinicAdminAssets/ScrollFrame/scrollrefreshbutton.png",
                "assets/Appointments/ReturnButton.png",
                "assets/Appointments/Creation/BookAppointment.png",
                "assets/Appointments/ReturnButton.png",
            ]
        }
        # Appointment Dashboard
        self.creationButton = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][0],
            x=620, y=800, classname="createbutton", root=self,
            buttonFunction=lambda: [self.loadAppointmentCreation()],
        )
        self.managementButton = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][1],
            x=1140, y=800, classname="managebutton", root=self,
            buttonFunction=lambda: [
                self.manageAppointmentsFrame.grid,self.manageAppointmentsFrame.tkraise],
        )
        self.refreshBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][2],
            x=1450, y=120, classname="viewAppointmentrefresh", root=self,
            buttonFunction=lambda:
                [self.controller.threadCreator(
                    target=self.appointmentList)],
                isPlaced=True
        )
        # Appointment Creation
        self.returncreationBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][3],
            x=20, y=60, classname="returncreation", root=self.createAppointmentsFrame,
            buttonFunction=lambda: [
                self.createAppointmentsFrame.grid_remove()],
        )
        self.bookAppointmentBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][4],
            x=820, y=720, classname="bookappointment", root=self.createAppointmentsFrame,
            buttonFunction=lambda: [print('book')],
        )
        # Appointment Management
        self.returnmanagementBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][5],
            x=20, y=60, classname="returnmanagement", root=self.manageAppointmentsFrame,
            buttonFunction=lambda: [
                self.manageAppointmentsFrame.grid_remove()],
        )

    def appointmentList(self):
        prisma = self.prisma
        app = prisma.appointment.find_many(
            where={
                "appRequest": {"is": {"clinic": {"is": {"admin": {"some": {"userId": self.user.id}}}}}}
            },
            include={
                "doctor": {"include": {"user": True}},
                "appRequest": {"include": {"clinic": True, "patient": {"include": {"user": True, "healthRecord": True}}, "appointments": True}},
                "prescription": True,

            }
        )
        h = len(app) * 120
        if h < 420:
            h = 420
        self.viewAppointmentScrolledFrame = ScrolledFrame(
            master=self, width=1500, height=h, autohide=True, bootstyle="minty-bg"
        )
        self.viewAppointmentScrolledFrame.grid_propagate(False)
        self.viewAppointmentScrolledFrame.place(
            x=80, y=260, width=1500, height=420)
        COORDS = (20, 0)
        for appointment in app:
            createdAt = appointment.createdAt
            X = COORDS[0]
            Y = COORDS[1]
            R = self.viewAppointmentScrolledFrame
            FONT = ("Inter", 12)
            self.controller.labelCreator(
                ipath="assets/Appointments/Homepage/AppItemBg.png",
                x=X, y=Y, classname=f"appointmentlist{appointment.id}", root=R,
                isPlaced=True,
            )

            self.controller.scrolledTextCreator(
                x=X+20, y=Y, width=220, height=100, root=R, classname=f"{appointment.id}_patient_name",
                bg="#f1feff", hasBorder=False,
                text=f"{appointment.appRequest.patient.user.fullName}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            self.controller.scrolledTextCreator(
                x=X+240, y=Y, width=240, height=100, root=R, classname=f"{appointment.id}_doctor_name",
                bg="#f1feff", hasBorder=False,
                text=f"{appointment.doctor.user.fullName}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            KL = timezone("Asia/Kuala_Lumpur")
            # "DD/MM/YYYY HH:MM"
            fmt = "%d/%m/%Y %H:%M"
            startTime = KL.convert(appointment.startTime).strftime(fmt)
            endTime = KL.convert(appointment.endTime).strftime(fmt)
            formatted = f"Start: {startTime}\nEnd: {endTime}"
            self.controller.scrolledTextCreator(
                x=X+480, y=Y, width=240, height=100, root=R, classname=f"{appointment.id}_dateandtime_time",
                bg="#f1feff", hasBorder=False,
                text=formatted, font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            self.controller.scrolledTextCreator(
                x=X+720, y=Y, width=140, height=100, root=R, classname=f"{appointment.id}_doctor_accept",
                bg="#f1feff", hasBorder=False,
                text=f"{appointment.docAccepted}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            self.controller.scrolledTextCreator(
                x=X+860, y=Y, width=140, height=100, root=R, classname=f"{appointment.id}_patient_accept",
                bg="#f1feff", hasBorder=False,
                text=f"{appointment.patientAccepted}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            self.controller.buttonCreator(
                ipath="assets/Appointments/Homepage/ViewAppRequest.png",
                x=X+1040, y=Y+20, classname=f"viewbutton{appointment.id}", root=R,
                buttonFunction=lambda a=appointment.appRequest: [
                    self.controller.threadCreator(
                        target=self.loadViewPatientRequest, appReq=a
                    )
                ],
                isPlaced=True
            )
            self.controller.buttonCreator(
                ipath="assets/Dashboard/ClinicAdminAssets/ScrollFrame/delete.png",
                x=X+1360, y=Y+20, classname=f"deletebutton{appointment.id}", root=self.viewAppointmentScrolledFrame,
                buttonFunction=lambda: [print('delete')],
                isPlaced=True
            )
            self.controller.scrolledTextCreator(
                x=X+1140, y=Y, width=160, height=100, root=R, classname=f"{appointment.id}_status",
                bg="#f1feff", hasBorder=False,
                text=f"{appointment.status}", font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            COORDS = (
                COORDS[0], COORDS[1] + 120
            )

    def loadViewPatientRequest(self, appReq: AppointmentRequest):
        self.parent.patientRequests = MainPatientRequestsInterface(
            controller=self.controller, parent=self.parent)
        self.parent.patientRequests.loadRoleAssets(clinicAdmin=True)
        self.parent.patientRequests.primarypanel.createManagePatientRequest(
            req=appReq)

    def loadAppointmentCreation(self):
        self.createAppointmentsFrame.grid()
        self.createAppointmentsFrame.tkraise()
        self.create_app_load_menubuttons()

    def create_app_load_menubuttons(self):
        self.create_app_load_request_menu()
        self.create_app_load_timeslots()
        self.create_app_load_doctor_menu()
        self.create_app_load_datepicker()

    def create_app_load_doctor_menu(self):
        prisma = self.prisma
        R = self.createAppointmentsFrame
        self.doctors = prisma.doctor.find_many(
            where={
                "clinicId": self.parent.primarypanel.clinic.id
            },
            include={
                "user": True,
            }
        )
        self.doctor: Doctor = self.doctors[0]
        self.currDoc = StringVar()
        self.doctor_menu = self.controller.menubuttonCreator(
            x=140, y=600, width=400, height=80, root=R, classname="create_app_doctor_menu",
            listofvalues=[
                f"{doctor.user.fullName} - {doctor.speciality}" for doctor in self.doctors],
            variable=self.currDoc,
            command=lambda: [
                self.create_app_set_doctor(self.currDoc.get())
            ],
            text="Select Doctor",
        )
        self.currDoc.set(
            f"{self.doctor.user.fullName} - {self.doctor.speciality}")
        self.doctor_menu.configure(
            text=f"{self.doctor.user.fullName} - {self.doctor.speciality}"
        )
        self.create_app_set_doctor(self.currDoc.get())

    def create_app_set_doctor(self, option: str):
        self.doctor = list(
            filter(
                lambda doctor: f"{doctor.user.fullName} - {doctor.speciality}" == option,
                self.doctors
            )
        )[0]
    
    def create_app_load_datepicker(self):
        entry, button = self.controller.entrywithDatePickerCreator(
            x=140, y=780, width=320, height=80, root=self.createAppointmentsFrame, classname="create_app_datepicker",
        )

    def create_app_load_request_menu(self):
        prisma = self.prisma
        R = self.createAppointmentsFrame
        self.patientReqs = prisma.appointmentrequest.find_many(
            where={
                "clinicId": self.parent.primarypanel.clinic.id
            },
            include={
                "patient": {
                    "include": {
                        "user": True,
                    }
                }
            }
        )
        self.patientReq: AppointmentRequest = self.patientReqs[0]
        self.currReq = StringVar()
        self.patient_requests = self.controller.menubuttonCreator(
            x=140, y=240, width=720, height=80, root=R, classname="create_app_patient_requests",
            listofvalues=[
                f"{req.patient.user.fullName} - I.D: {req.id} - {req.specialityWanted}" for req in self.patientReqs],
            variable=self.currReq,
            command=lambda: [
                self.create_app_set_request(self.currReq.get()),
                print(self.patientReq.preferredDate,
                      self.patientReq.preferredTime)
            ],
            text="Select Clinic",
        )
        self.currReq.set(
            f"{self.patientReq.patient.user.fullName} - I.D: {self.patientReq.id} - {self.patientReq.specialityWanted}")
        self.patient_requests.configure(
            text=f"{self.patientReq.patient.user.fullName} - I.D: {self.patientReq.id} - {self.patientReq.specialityWanted}"
        )
        self.create_app_set_request(self.currReq.get())

    def create_app_set_request(self, option: str):
        self.patientReq = list(
            filter(
                lambda req: f"{req.patient.user.fullName} - I.D: {req.id} - {req.specialityWanted}" == option,
                self.patientReqs
            )
        )[0]

    def create_app_load_timeslots(self):
        R = self.createAppointmentsFrame
        self.time_slot = StringVar()
        self.custom_start_time = StringVar()
        self.custom_end_time = StringVar()
        self.time_interval = IntVar()
        self.time_interval.set(30)

        self.create_app_set_time_interval_button = self.controller.buttonCreator(
            ipath="assets/Appointments/Creation/SetTimeSlot.png",
            x=280, y=360, classname="create_app_set_time_interval_button", root=R,
            buttonFunction=lambda: [
                self.create_app_set_time_interval()
            ],
        )
        self.time_type = IntVar()
        self.time_type.set(1)
        self.setUseDefaultTime = ttk.Checkbutton(
            master=R, bootstyle="info-toolbutton",
            onvalue=1, offvalue=0, variable=self.time_type,
            text="Use Default Time", cursor="hand2",
            command=lambda: [
                self.time_type.set(1),
                self.create_app_load_time_menu()
            ]
        )
        self.setUseDefaultTime.place(x=460, y=360, width=120, height=60)
        self.useCustomTime = ttk.Checkbutton(
            master=R, bootstyle="primary-toolbutton",
            onvalue=2, offvalue=0, variable=self.time_type,
            text="Use Custom Time", cursor="hand2",
            command=lambda: [
                self.time_type.set(2),
                self.create_app_load_time_menu()
            ]
        )
        self.useCustomTime.place(x=600, y=360, width=120, height=60)
        self.setOwnTime = ttk.Checkbutton(
            master=R, bootstyle="secondary-toolbutton",
            onvalue=3, offvalue=0, variable=self.time_type,
            text="Set Own Time", cursor="hand2",
            command=lambda: [
                self.time_type.set(3),
                self.create_app_load_time_menu()
            ]
        )
        self.setOwnTime.place(x=740, y=360, width=120, height=60)
        self.create_app_load_time_menu()

    def create_app_load_time_menu(self):
        R = self.createAppointmentsFrame
        DEFAULTTIME = "create_app_timeslot_menu"
        CUSTOMSTART = "create_app_custom_start_time"
        CUSTOMEND = "create_app_custom_end_time"
        s_time = self.parent.primarypanel.clinic.clinicHrs.split(" - ")[0]
        e_time = self.parent.primarypanel.clinic.clinicHrs.split(" - ")[1]
        if self.time_type.get() == 1:
            self.create_app_timeslot_menu = self.controller.timeMenuButtonCreator(
                x=140, y=420, width=720, height=80, root=R, classname=DEFAULTTIME,
                variable=self.time_slot,
                command=lambda: [
                    None
                ],
                text="Select Time",
                startTime=s_time, endTime=e_time,
                interval=self.time_interval.get(),
                isTimeSlotFmt=True
            )
            try:
                self.controller.widgetsDict[f"{CUSTOMSTART}hostfr"].grid_remove(
                )
                self.controller.widgetsDict[f"{CUSTOMEND}hostfr"].grid_remove()
                self.controller.widgetsDict[f"{DEFAULTTIME}hostfr"].grid()
                self.controller.widgetsDict[f"{DEFAULTTIME}hostfr"].tkraise()
            except:
                pass
        elif self.time_type.get() == 2:
            self.load_custom_start_time_end_time(
                R, CUSTOMSTART, CUSTOMEND, s_time, e_time)
            try:
                self.controller.widgetsDict[f"{DEFAULTTIME}hostfr"].grid_remove(
                )
                self.controller.widgetsDict[f"{CUSTOMSTART}hostfr"].grid()
                self.controller.widgetsDict[f"{CUSTOMSTART}hostfr"].tkraise()
                self.controller.widgetsDict[f"{CUSTOMEND}hostfr"].grid()
                self.controller.widgetsDict[f"{CUSTOMEND}hostfr"].tkraise()
            except:
                pass
        elif self.time_type.get() == 3:
            start_time_end_time = Querybox.get_string(
                title="Entering Custom Time",
                prompt="Please enter the start and end time in the format of 12:00PM - 08:00PM",
                initialvalue=f"{s_time} - {e_time}",
                parent=self.create_app_set_time_interval_button
            )
            while True:
                if start_time_end_time is None:
                    break
                try:
                    start_time, end_time = start_time_end_time.split(" - ")
                    start_time = dt.datetime.strptime(
                        start_time, "%I:%M%p").time()
                    end_time = dt.datetime.strptime(
                        end_time, "%I:%M%p").time()
                    if start_time >= end_time:
                        raise ValueError(
                            "Start time cannot be later than end time")
                    self.load_custom_start_time_end_time(
                        R, CUSTOMSTART, CUSTOMEND, s_time, e_time)
                    self.create_app_custom_start_time.configure(
                        text=start_time.strftime("%I:%M%p")
                    )
                    self.create_app_custom_end_time.configure(
                        text=end_time.strftime("%I:%M%p")
                    )
                    self.custom_start_time.set(start_time)
                    self.custom_end_time.set(end_time)
                    try:
                        self.controller.widgetsDict[f"{DEFAULTTIME}hostfr"].grid_remove(
                        )
                        self.controller.widgetsDict[f"{CUSTOMSTART}hostfr"].grid(
                        )
                        self.controller.widgetsDict[f"{CUSTOMSTART}hostfr"].tkraise(
                        )
                        self.controller.widgetsDict[f"{CUSTOMEND}hostfr"].grid(
                        )
                        self.controller.widgetsDict[f"{CUSTOMEND}hostfr"].tkraise(
                        )
                    except:
                        pass
                    break
                except ValueError as e:
                    messagebox.showerror(
                        title="Aborting...", message="Invalid time format")
                    start_time_end_time = Querybox.get_string(
                        title="Entering Custom Time",
                        prompt="Please enter the start and end time in the format of 12:00PM - 08:00PM",
                        initialvalue=f"{s_time} - {e_time}",
                        parent=self.create_app_set_time_interval_button
                    )

    def load_custom_start_time_end_time(self, R, CUSTOMSTART, CUSTOMEND, s_time, e_time):
        self.create_app_custom_start_time = self.controller.timeMenuButtonCreator(
            x=140, y=420, width=340, height=80, root=R, classname=CUSTOMSTART,
            variable=self.custom_start_time,
            command=lambda: [
                None
            ],
            text="Select Start Time",
            startTime=s_time, endTime=e_time,
            interval=self.time_interval.get(),
            isTimeSlotFmt=False
        )
        self.create_app_custom_end_time = self.controller.timeMenuButtonCreator(
            x=520, y=420, width=340, height=80, root=R, classname=CUSTOMEND,
            variable=self.custom_end_time,
            command=lambda: [
                None
            ],
            text="Select End Time",
            startTime=s_time, endTime=e_time,
            interval=self.time_interval.get(),
            isTimeSlotFmt=False
        )

    def create_app_set_time_interval(self):
        try:
            self.time_interval.set(int(Querybox.get_integer(
                title="Set Time Interval",
                prompt="Set Time Interval (in whole minutes):",
                initialvalue=30,
                minvalue=30,
                maxvalue=1440,
                parent=self.create_app_set_time_interval_button
            )))
        except:
            messagebox.showerror(
                title="Aborting...", message="Invalid time interval value")
        self.create_app_load_time_menu()

    