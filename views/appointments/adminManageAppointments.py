from abc import ABC, abstractmethod
import calendar
import re
import threading
from tkinter import *
from tkinter import messagebox
from prisma.models import Appointment
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
from pendulum import timezone
import tkintermapview
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime


class AdminManageAppointments(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="appointmentspanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)

        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.appointmentImgLabels()
        self.appointmentButtons()
        self.creationFrame.grid_remove()
        self.viewFrame.grid_remove()
        self.KL = timezone("Asia/Kuala_Lumpur")
        self.UTC = timezone("UTC")

    def createFrames(self):
        self.timeSlotFrame = self.controller.frameCreator(
            x=0, y=0, classname="timeslotframe", root=self, framewidth=1680, frameheight=1080
        )
        self.manageAppointmentsFrame = self.controller.frameCreator(
            x=0, y=0, classname="manageframe", root=self, framewidth=1680, frameheight=1080
        )
        self.unloadStackedFrames()

    def unloadStackedFrames(self):
        self.timeSlotFrame.grid_remove()
        self.manageAppointmentsFrame.grid_remove()

    def appointmentImgLabels(self):
        self.bg = self.controller.labelCreator(
            ipath="assets/Appointments/Homepage/AppointmentDashboard.png",
            x=0, y=0, classname="appointmenthomepage", root=self
        )
        self.imgLabels = [
            ("assets/Appointments/Creation/TimeSlotBg.png",
             0, 0, "creationimage", self.timeSlotFrame),
            ("assets/Appointments/Management/AppointmentManagement.png",
             0, 0, "manageimage", self.manageAppointmentsFrame)
        ]
        self.controller.settingsUnpacker(self.imgLabels, "label")

    def appointmentButtons(self):
        d = {
            "appointmentButtons": [
                "assets/Appointments/Homepage/CreateAppointments.png",
                "assets/Appointments/Homepage/ManageAppointments.png",
                "assets/Appointments/Creation/ReturnCreationButton.png",
                "assets/Appointments/Creation/ReturnManagementButton.png"
            ]
        }
        self.creationButton = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][0],
            x=60, y=680, classname="createbutton", root=self,
            buttonFunction=lambda: [
                self.timeSlotFrame.grid(), self.timeSlotFrame.tkraise()],
        )
        self.managementButton = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][1],
            x=600, y=680, classname="managebutton", root=self,
            buttonFunction=lambda: [
                self.manageAppointmentsFrame.grid(), self.manageAppointmentsFrame.tkraise()],
        )
        self.returncreationBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][2],
            x=40, y=80, classname="returncreation", root=self.timeSlotFrame,
            buttonFunction=lambda: [self.timeSlotFrame.grid_remove()],
        )
        self.returnmanagementBtn = self.controller.buttonCreator(
            ipath=d["appointmentButtons"][3],
            x=40, y=60, classname="returnmanagement", root=self.manageAppointmentsFrame,
            buttonFunction=lambda: [self.manageAppointmentsFrame.grid_remove()],
        )

        self.scrolledframe = ScrolledFrame(
        self, width=460, height=660, name="appointmentscrolledframe", autohide=True,
        bootstyle="dark-rounded"
        )
        self.scrolledframe.place(
            x=1180, y=340, width=460, height=620
        )
        self.mainDateEntry = self.controller.ttkEntryCreator(
            root=self, xpos=1420, ypos=180, width=360, height=40, classname="maindateentry",
            font=("Inter", 16), fg=BLACK,
        )
        self.mainDateEntry.insert(0, datetime.now().strftime('%A, %d %B %Y'))
        self.mainDateEntry.configure(state=READONLY)
    
    def selectingDate(self, btn: Button, entry: Entry):
        # the pairs of variables
        textvar1 = self.startDateString
        dialog = DatePickerDialog(
            parent=btn, title="Select Date", firstweekday=0,
        )
        entry.configure(state=NORMAL)
        entry.delete(0, END)
        date = dialog.date_selected.strftime('%A, %d %B %Y')
        entry.insert(0, date)
        entry.configure(state=READONLY)
        dayOfTextVar1 = datetime.strptime(
            textvar1.get(), '%A, %d %B %Y').strftime('%A')
        # check the day of the textvar1 and compare it with the self.dayString.get()
        print(dayOfTextVar1)
        if datetime.strptime(textvar1.get(), '%A, %d %B %Y') <= datetime.now():
            # revert textvar1 to the original date
            textvar1.set(self.formatString)
            ToastNotification(
                title="Invalid Date",
                message=f"The timeslot you have selected falls before the current time. Please select a date which is after the current time.",
                duration=5000,
                bootstyle=DANGER
            ).show_toast()
        elif self.dayString.get() == dayOfTextVar1.upper():
            print("same day")
        # if the dayOfTextVar1 is before the current time, then revert the textvar1 to the original date
        else:
            # revert textvar1 to the original date
            ToastNotification(
                title="Invalid Date",
                message=f"The day of the date you have selected, {dayOfTextVar1.upper()} is invalid. Please select a date which is on a {self.dayString.get()}.",
                duration=5000,
                bootstyle=DANGER
            ).show_toast()
            textvar1.set(self.formatString)
    
    def postLogin(self, data: dict = None):
        self.prisma = self.controller.mainPrisma
        self.userId = data["id"]
        self.role = data["role"]
        self.loadAllDetailsForCreation()

    def loadForDoctor(self):
        prisma = self.prisma
        doctor = prisma.doctor.find_first(
            where={
                "userProfile": {
                    "is": {
                        "id": self.userId
                    }
                }
            },
            include={
                "apptSettings": True,
                "userProfile": True,
            }
        )
        return doctor

    def loadForDoctor(self):
        prisma = self.prisma
        doctors = prisma.doctor.find_many(
            where={
                "student": {
                    "is": {
                        "userId": self.userId
                    }
                }
            },
            include={
                "module": {
                    "include": {
                        "lecturer": {
                            "include": {
                                "userProfile": True,
                                "apptSettings": True
                            }
                        }
                    }
                }
            }
        )
        return modules
    def refreshAppCreationStudent(self):
        self.loadAllDetailsForCreation()
    def loadAllDetailsForCreation(self):
        # MODULE -> LECTURER -> TIMESLOT
        for widgetname, widget in self.creationFrame.children.items():
            if not widgetname.startswith("!la"):
                if widgetname in ["moduleshostfr", "lecturersaptmenuhostfr", "timeslotmenuhostfr"]:
                    widget.grid_remove()
        self.moduleDict = {}
        if self.role == "lecturer":
            self.lecturerList = self.loadForLecturer()
            self.loadAsLecturer()
        elif self.role == "student":
            self.fullinfo = self.loadForStudent()
            self.loadAsStudent()

    # loadaslecturer will be using self.lecAddTimeslotFrame
    # there will be a location ttkEntryCreator
    # a select day menubuttonCreator
    # similar to start and end time
    # will require the ID of the lecaptsettingfield
    # id, lecturerid, day, starttime, endtime, location

    #----------------------- ------------------ START of Time Slot Creation -------------------------------------
    def loadAsLecturer(self):
        KL = timezone("Asia/Kuala_Lumpur")
        humanreadable = r"%I:%M%p"
        self.LECAPTDAYS = [
            "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"
        ]
        start_time = datetime.strptime("08:00AM", "%I:%M%p")
        end_time = datetime.strptime("06:00PM", "%I:%M%p")
        time_slots = [start_time + timedelta(minutes=30*i) for i in range(21)]
        time_slots_str = [ts.strftime("%I:%M%p") for ts in time_slots]

        pos = {
            "aptstglocationent": {"x": 140, "y": 340, "width": 240, "height": 60},
            "aptstgdaymb": {"x": 140, "y": 420, "width": 240, "height": 60},
            "aptstgstarttimemb": {"x": 140, "y": 500, "width": 240, "height": 60},
            "aptstgendtimemb": {"x": 140, "y": 580, "width": 240, "height": 60},
        }

        lists = {
            "aptstgdaymb": self.LECAPTDAYS,
            "aptstgstarttimemb": time_slots_str,
            "aptstgendtimemb": time_slots_str
        }

        ENAME = "aptstglocationent"
        self.aptstglocationEnt = self.controller.ttkEntryCreator(
            root=self.timeSlotFrame, xpos=pos[ENAME]["x"], ypos=pos[ENAME]["y"],
            width=pos[ENAME]["width"], height=pos[ENAME]["height"], classname=ENAME,
            font=("Urbanist", 20), fg=BLACK,
        )

        self.aptstgdaymbvar = StringVar()
        self.aptstgstarttimembvar = StringVar()
        self.aptstgendtimembvar = StringVar()

        vars = {
            "aptstgdaymb": self.aptstgdaymbvar,
            "aptstgstarttimemb": self.aptstgstarttimembvar,
            "aptstgendtimemb": self.aptstgendtimembvar
        }

        for name, values in lists.items():
            self.controller.menubuttonCreator(
                root=self.timeSlotFrame, xpos=pos[name]["x"], ypos=pos[name]["y"],
                width=pos[name]["width"], height=pos[name]["height"],
                classname=name,
                listofvalues=values, variable=vars[name],
                font=("Urbanist", 20), text="",
                command=lambda name=name: [
                    self.validateDateVars(name, vars[name].get()),
                ]
            )

        # set the default values
        self.aptstgdaymbvar.set(self.LECAPTDAYS[0])
        self.aptstgstarttimembvar.set(time_slots_str[0])
        self.aptstgendtimembvar.set(time_slots_str[-1])

        WD = self.controller.widgetsDict
        WD["aptstgdaymb"].configure(
            text=self.aptstgdaymbvar.get())
        WD["aptstgstarttimemb"].configure(
            text=self.aptstgstarttimembvar.get())
        WD["aptstgendtimemb"].configure(
            text=self.aptstgendtimembvar.get())

        fullTimeslots = []

        for i in self.lecturerList.apptSettings:
            stgId = i.id
            day = i.day
            location = i.location
            starttime = KL.convert(i.startTime).strftime(humanreadable)
            endtime = KL.convert(i.endTime).strftime(humanreadable)
            formattedTime = f"{day}, {starttime} - {endtime} at {location}"
            fullTimeslots.append(
                (stgId, formattedTime, day, starttime, endtime, location)
            )

        self.timeScrolledFrame = ScrolledFrame(
            self.timeSlotFrame, width=820, height=300, autohide=True, bootstyle="warning-rounded"
        )
        self.timeScrolledFrame.place(
            x=420, y=340, width=820, height=300
        )

        h = (len(fullTimeslots)) * 100 + 20
        if h < 300:
            h = 300
        self.timeScrolledFrame.config(height=h)
        coords = (20, 20)
        IMAGEPATH = r"Assets\AppointmentsView\LecturerTimeslots\timeslottextbg.png"
        for id, timeslot, day, starttime, endtime, location in fullTimeslots:
            t = self.controller.textElement(
                imagepath=IMAGEPATH, xpos=coords[0], ypos=coords[1],
                classname=f"{id}timeslottext", root=self.timeScrolledFrame,
                text=timeslot, font=URBANIST, size=30, isPlaced=True
            )
            edit = self.controller.buttonCreator(
                imagepath=r"Assets\AppointmentsView\LecturerTimeslots\editbtn.png",
                xpos=coords[0] + 660, ypos=coords[1] + 20,
                root=self.timeScrolledFrame, classname=f"{id}timesloteditbtn",
                buttonFunction=lambda id=(id, day, starttime, endtime, location): self.editTimeslot(
                    id[0], id[1], id[2], id[3], id[4]),
                isPlaced=True
            )
            delete = self.controller.buttonCreator(
                imagepath=r"Assets\AppointmentsView\LecturerTimeslots\deletebtn.png",
                xpos=coords[0] + 720, ypos=coords[1] + 20,
                root=self.timeScrolledFrame, classname=f"{id}timeslotdeletebtn",
                buttonFunction=lambda id=id: self.deleteTimeslot(id),
                isPlaced=True
            )
            coords = (coords[0], coords[1] + 100)

    def deleteTimeslot(self, id):
        askConfirmation = messagebox.askyesno(
            title="Delete Timeslot", message="Are you sure you want to delete this timeslot?")
        if not askConfirmation:
            return
        self.prisma.lecapptsetting.delete(
            where={
                "id": id
            }
        )
        t = threading.Thread(target=self.loadAllDetailsForCreation, args=())
        t.daemon = True
        t.start()

    def editTimeslot(self, id, day, starttime, endtime, location):
        parentWidget = self.controller.widgetsDict[f"{id}timesloteditbtn"]
        KL = timezone("Asia/Kuala_Lumpur")
        UTC = timezone("UTC")
        humanreadable = "%I:%M%p"
        # Regex patterns for Location, Time, and Day Inputs for Dialog Validation
        # Location pattern allows only alphanumeric characters, spaces and no more.
        locationPattern = r"^[a-zA-Z0-9 ]+$"
        # Time pattern allows only 12-hour time format with AM/PM
        # I.E: 12:00PM, do not allow 12:00 PM or 12:00 pm or 12:00 Pm or 12:00 pM or 12:00pm
        timePattern = r"^(0[1-9]|1[0-2]):[0-5][0-9](AM|PM)$"
        # compile the regex patterns
        locationRegex = re.compile(locationPattern)
        timeRegex = re.compile(timePattern)

        buttonsList = ["Edit Location:success",
                       "Edit Time:secondary", "Edit Day:info", "Cancel:danger"]
        timeOptions = ["Edit Start Time:primary",
                       "Edit End Time:secondary", "Cancel:danger"]
        dayOptions = ["MONDAY:primary", "TUESDAY:secondary", "WEDNESDAY:success",
                      "THURSDAY:info", "FRIDAY:warning", "Cancel:danger"]

        askOption = MessageDialog(
            parent=parentWidget,
            title="Edit Timeslot",
            message="What do you want to do with the timeslot?",
            buttons=buttonsList,
        )
        askOption.show()
        if askOption.result == "Edit Location":
            while True:
                newLocation = Querybox.get_string(
                    parent=parentWidget,
                    title="Edit Location",
                    prompt="Enter new location",
                    initialvalue=location
                )
                if not locationRegex.match(newLocation):
                    Messagebox.show_error(
                        parent=parentWidget,
                        title="Error",
                        message="Please enter a valid input for location, it must be alphanumeric and spaces only",
                    )
                    continue
                elif newLocation == location:
                    Messagebox.show_error(
                        parent=parentWidget,
                        title="Error",
                        message=f"Please enter a location different from the current one, {location}",
                    )
                    continue
                else:
                    break
            if newLocation is not None:
                self.prisma.lecapptsetting.update(
                    where={
                        "id": id
                    },
                    data={
                        "location": newLocation
                    }
                )
                t = threading.Thread(
                    target=self.loadAllDetailsForCreation, args=())
                t.daemon = True
                t.start()
            else:
                return
        elif askOption.result == "Edit Time":
            askTimeEdit = MessageDialog(
                parent=parentWidget,
                title="Options to Edit Time",
                message="What do you want to edit?",
                buttons=timeOptions,
            )
            askTimeEdit.show()
            if askTimeEdit.result == "Edit Start Time":
                while True:  # Infinitely loop until user cancels or enters a valid input
                    newStartTime = Querybox.get_string(
                        parent=parentWidget,
                        title="Edit Start Time",
                        prompt=f"Enter new start time, originally {starttime} - {endtime}",
                        initialvalue=starttime
                    )
                    # check if newStartTime is None, if so, return
                    if newStartTime is None:
                        return
                    # check newStartTime string matches regex pattern
                    if not timeRegex.match(newStartTime):
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message="Please enter a start time, following the format HH:MMAM/PM",
                        )
                        continue
                    # check if newStartTime is the same as the original start time
                    if newStartTime == starttime:
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message="Please enter a different start time or cancel",
                        )
                        continue
                    # check if newStartTime is before 8:00AM
                    elif datetime.strptime(newStartTime, humanreadable) < datetime.strptime("8:00AM", humanreadable):
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message=f"Please enter a start time that is not before 8:00AM",
                        )
                        continue
                    # check if newStartTime is after the original end time
                    elif datetime.strptime(newStartTime, humanreadable) >= datetime.strptime(endtime, humanreadable):
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message=f"Please enter a start time that is before the end time, {newStartTime} is not before {endtime}",
                        )
                        continue
                    else:  # Valid input, break out of the loop
                        break
                if newStartTime is not None:
                    startObj = datetime.strptime(newStartTime, humanreadable)
                    startObj = UTC.convert(KL.convert(startObj))
                    self.prisma.lecapptsetting.update(
                        where={
                            "id": id
                        },
                        data={
                            "startTime": startObj
                        }
                    )
                    t = threading.Thread(
                        target=self.loadAllDetailsForCreation, args=())
                    t.daemon = True
                    t.start()
            elif askTimeEdit.result == "Edit End Time":
                while True:
                    newEndTime = Querybox.get_string(
                        parent=parentWidget,
                        title="Edit End Time",
                        prompt=f"Enter new end time, originally {starttime} - {endtime}",
                        initialvalue=endtime
                    )
                    # check newEndTime string matches regex pattern
                    if not timeRegex.match(newEndTime):
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message="Please enter an end time, following the format HH:MMAM/PM",
                        )
                        continue
                    # check if newEndTime is the same as the original end time
                    if newEndTime == endtime:
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message="Please enter a different end time or cancel",
                        )
                        continue
                    # check if newEndTime is after 6:00PM
                    elif datetime.strptime(newEndTime, humanreadable) > datetime.strptime("06:00PM", humanreadable):
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message=f"Please enter an end time that is not after 6:00PM",
                        )
                        continue
                    # check if newEndTime is before the original start time
                    elif datetime.strptime(newEndTime, humanreadable) <= datetime.strptime(starttime, humanreadable):
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message=f"Please enter an end time that is after the start time, {newEndTime} is not after {starttime}",
                        )
                        continue
                    elif newEndTime is None:
                        return
                    else:
                        break
                if newEndTime is not None:
                    endObj = datetime.strptime(newEndTime, humanreadable)
                    endObj = UTC.convert(KL.convert(endObj))
                    self.prisma.lecapptsetting.update(
                        where={
                            "id": id
                        },
                        data={
                            "endTime": endObj
                        }
                    )
                    t = threading.Thread(
                        target=self.loadAllDetailsForCreation, args=())
                    t.daemon = True
                    t.start()
            else:
                return
        elif askOption.result == "Edit Day":
            askDay = MessageDialog(
                parent=parentWidget,
                title=f"Changing the day from {day}",
                message="Select a New Day",
                buttons=dayOptions
            )
            askDay.show()
            newDay = askDay.result
            if newDay is not None:
                self.prisma.lecapptsetting.update(
                    where={
                        "id": id
                    },
                    data={
                        "day": newDay.upper().strip()
                    }
                )
                t = threading.Thread(
                    target=self.loadAllDetailsForCreation, args=())
                t.daemon = True
                t.start()
            else:
                return

    def validateDateVars(self, name, value):
        if name == "aptstgdaymb":
            print(value)
        elif name == "aptstgstarttimemb":
            startTime = self.aptstgstarttimembvar.get()
            endTime = self.aptstgendtimembvar.get()
            start = datetime.strptime(startTime, "%I:%M%p")
            end = datetime.strptime(endTime, "%I:%M%p")
            diff = timedelta(hours=end.hour, minutes=end.minute) - \
                timedelta(hours=start.hour, minutes=start.minute)
            # do not accept diff < 30 minutes
            try:
                errToast.hide_toast()
            except:
                pass
            errToast = ToastNotification(
                title="Error",
                message="Start time must be earlier than end time",
                duration=2000,
                bootstyle=DANGER
            )
            if diff < timedelta(minutes=30):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(endTime, "%I:%M%p") -
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"Start time must be at least 30 minutes earlier than end time\nResetting {startTime} to {newTime}"
                self.aptstgstarttimembvar.set(newTime)
                errToast.show_toast()
            # if diff is negative
            elif diff < timedelta(hours=0):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(endTime, "%I:%M%p") -
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"Start time cannot be later than end time\nResetting {startTime} to {newTime}"
                self.aptstgstarttimembvar.set(newTime)
                errToast.show_toast()
        elif name == "aptstgendtimemb":
            startTime = self.aptstgstarttimembvar.get()
            endTime = self.aptstgendtimembvar.get()
            start = datetime.strptime(startTime, "%I:%M%p")
            end = datetime.strptime(endTime, "%I:%M%p")
            diff = timedelta(hours=end.hour, minutes=end.minute) - \
                timedelta(hours=start.hour, minutes=start.minute)
            try:
                errToast.hide_toast()
            except:
                pass
            errToast = ToastNotification(
                title="Error",
                message="Start time must be earlier than end time",
                duration=2000,
                bootstyle=DANGER
            )
            # do not accept diff < 30 minutes
            if diff < timedelta(minutes=30):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(startTime, "%I:%M%p") +
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"End time must be at least 30 minutes later than start time\nResetting {endTime} to {newTime}"
                self.aptstgendtimembvar.set(newTime)
                errToast.show_toast()
            # if diff is negative
            elif diff < timedelta(hours=0):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(startTime, "%I:%M%p") +
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"End time cannot be earlier than start time\nResetting {endTime} to {newTime}"
                self.aptstgendtimembvar.set(newTime)
                errToast.show_toast()
        elif name == "appstarttimemb":
            startTime = self.appStartTimeVar.get()
            endTime = self.appEndTimeVar.get()
            print(f"The lecturer selected is {self.lecturer.get()}")
            print(f"The location string is {self.locationString.get()}")
            print(f"The timeslot selected is {self.timeslot.get()}")
            start = datetime.strptime(startTime, "%I:%M%p")
            end = datetime.strptime(endTime, "%I:%M%p")
            diff = timedelta(hours=end.hour, minutes=end.minute) - \
                timedelta(hours=start.hour, minutes=start.minute)
            try:
                errToast.hide_toast()
            except:
                pass
            errToast = ToastNotification(
                title="Error",
                message="Start time must be earlier than end time",
                duration=2000,
                bootstyle=DANGER
            )
            # do not accept diff < 30 minutes
            if diff < timedelta(minutes=30):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(endTime, "%I:%M%p") -
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"Start time must be at least 30 minutes earlier than end time\nResetting {startTime} to {newTime}"
                self.appStartTimeVar.set(newTime)
                errToast.show_toast()
            # if diff is negative
            elif diff < timedelta(hours=0):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(endTime, "%I:%M%p") -
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"Start time cannot be later than end time\nResetting {startTime} to {newTime}"
                self.appStartTimeVar.set(newTime)
                errToast.show_toast()
        elif name == "appendtimemb":
            startTime = self.appStartTimeVar.get()
            endTime = self.appEndTimeVar.get()
            print(f"The lecturer selected is {self.lecturer.get()}")
            print(f"The location string is {self.locationString.get()}")
            print(f"The timeslot selected is {self.timeslot.get()}")
            start = datetime.strptime(startTime, "%I:%M%p")
            end = datetime.strptime(endTime, "%I:%M%p")
            diff = timedelta(hours=end.hour, minutes=end.minute) - \
                timedelta(hours=start.hour, minutes=start.minute)
            try:
                errToast.hide_toast()
            except:
                pass
            errToast = ToastNotification(
                title="Error",
                message="Start time must be earlier than end time",
                duration=2000,
                bootstyle=DANGER
            )
            # do not accept diff < 30 minutes
            if diff < timedelta(minutes=30):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(startTime, "%I:%M%p") +
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"End time must be at least 30 minutes later than start time\nResetting {endTime} to {newTime}"
                self.appEndTimeVar.set(newTime)
                errToast.show_toast()
            # if diff is negative
            elif diff < timedelta(hours=0):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(startTime, "%I:%M%p") +
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"End time cannot be earlier than start time\nResetting {endTime} to {newTime}"
                self.appEndTimeVar.set(newTime)
                errToast.show_toast()
        else:
            print("error")

    def uploadApptSetting(self):
        prisma = self.prisma
        KL = timezone("Asia/Kuala_Lumpur")
        UTC = timezone("UTC")
        lecturer = prisma.lecturer.find_first(
            where={
                "userId": self.userId
            },
            include={
                "apptSettings": True
            }
        )
        startTime = self.aptstgstarttimembvar.get()
        endTime = self.aptstgendtimembvar.get()
        # Convert to UTC
        startObj = datetime.strptime(startTime, "%I:%M%p")
        endObj = datetime.strptime(endTime, "%I:%M%p")
        startObj = UTC.convert(KL.convert(startObj))
        endObj = UTC.convert(KL.convert(endObj))
        if lecturer is not None:
            prisma.lecapptsetting.create(
                data={
                    "day": self.aptstgdaymbvar.get().upper().strip(),
                    "location": self.aptstglocationEnt.get().strip(),
                    "startTime": startObj,
                    "endTime": endObj,
                    "lecturer": {
                        "connect": {
                            "id": lecturer.id
                        }
                    }
                }
            )
            t = threading.Thread(
                target=self.loadAllDetailsForCreation, args=())
            t.daemon = True
            t.start()
        else:
            return
    #------------------------------------------ END of Time Slot Creation -------------------------------------