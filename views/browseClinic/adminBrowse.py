from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.dashboard.adminDashboard import ClinicAdminDashboard
from abc import ABC, abstractmethod
import calendar
import re
import threading
from tkinter import *
from tkinter import messagebox
from views.citystatesdict import states_dict
from prisma.models import Clinic
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from ttkbootstrap.dialogs.dialogs import DatePickerDialog
from resource.basewindow import gridGenerator
from resource.static import *
from resource.basewindow import ElementCreator
from datetime import datetime, timedelta
from PIL import Image, ImageOps, ImageTk
import datetime as dt
from pendulum import timezone
import tkintermapview


class AdminBrowseClinic(Frame):
    def __init__(self, parent: ClinicAdminDashboard = None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="browseclinicpanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        self.user = self.parent.user
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()
        self.createButton()
        self.manageClinic()

    def createFrames(self):
        self.clinicInfoFrame = self.controller.frameCreator(
            x=0, y=0, classname="clinicinfo", root=self, framewidth=1680, frameheight=1080
        )
        self.unloadStackedFrames()

    def unloadStackedFrames(self):
        self.clinicInfoFrame.grid_remove()

    def createElements(self):
        self.bg = self.controller.labelCreator(
            ipath="assets/Dashboard/ClinicAdminAssets/ManageClinic/Homepage.png",
            x=0, y=0, classname="manageclinicbg", root=self
        )
        self.imgLabels = [
            ("assets/Dashboard/ClinicAdminAssets/ManageClinic/ClinicInfo.png",
             0, 0, "clinicinfobg", self.clinicInfoFrame)
        ]
        self.controller.settingsUnpacker(self.imgLabels, "label")

    def createButton(self):
        d = {
            "adminDashboard": [
                "assets/Dashboard/ClinicAdminAssets/ScrollFrame/updatelist.png",
                "assets/Dashboard/ClinicAdminAssets/AdminDashboard/ReturnButton.png",
            ]
        }
        self.UpdateListbutton = self.controller.buttonCreator(
            ipath=d["adminDashboard"][0],
            x=1300, y=160, classname="manageclinicrefresh", root=self,
            buttonFunction=lambda: [self.controller.threadCreator(
                    target=self.manageClinic)], isPlaced=True,
        )
        self.Returnbutton = self.controller.buttonCreator(
            ipath=d["adminDashboard"][1],
            x=60, y=60, classname="clinicreturnbutton", root=self.clinicInfoFrame,
            buttonFunction=lambda: [self.clinicInfoFrame.grid_remove()],
        )

    def manageClinic(self):
        prisma = self.prisma
        manageclinics = prisma.clinicenrolment.find_many(
            where={
                "AND": [{"status": "APPROVED"}, {"clinic": {"is": {"admin": {"some": {"userId": self.user.id}}}}}]
            },
            include={
                "clinic": True,
                "govRegDocSystem": True
            }
        )
        h = len(manageclinics) * 120
        if h < 640:
            h = 640
        self.manageClinicScrolledFrame = ScrolledFrame(
            master=self, width=1540, height=h, autohide=True, bootstyle="minty-bg"
        )
        self.manageClinicScrolledFrame.grid_propagate(False)
        self.manageClinicScrolledFrame.place(
            x=60, y=300, width=1540, height=640)

        COORDS = (20, 20)
        for clinics in manageclinics:
            clinicName = clinics.clinic.name
            clinicId = clinics.clinicId
            clinicContact = clinics.clinic.phoneNum
            clinicOpHrs = clinics.clinic.clinicHrs
            clinicAddress = clinics.clinic.address
            X = COORDS[0]
            Y = COORDS[1]
            R = self.manageClinicScrolledFrame
            FONT = ("Inter", 12)
            self.controller.labelCreator(
                ipath="assets/Dashboard/ClinicAdminAssets/ScrollFrame/list.png",
                x=X, y=Y, classname=f"manageClinic{clinicId}", root=R,
                isPlaced=True,
            )

            d = {
                "clinicButton": [
                    "assets/Dashboard/ClinicAdminAssets/ScrollFrame/view.png",
                    "assets/Dashboard/ClinicAdminAssets/ScrollFrame/delete.png",
                ]
            }
            self.viewClinicbutton = self.controller.buttonCreator(
                ipath=d["clinicButton"][0],
                x=X+1260, y=Y+35, classname=f"viewclinic{clinicId}", root=R,
                buttonFunction=lambda c=clinics.clinic: [
                    self.manageClinicInfo(c)],
                isPlaced=True
            )
            self.deleteClinicbutton = self.controller.buttonCreator(
                ipath=d["clinicButton"][1],
                x=X+1360, y=Y+35, classname=f"deleteclinic{clinicId}", root=R,
                buttonFunction=lambda: [self.controller.threadCreator(
                    self.deleteClinic)],
                isPlaced=True
            )
            clinicName = self.controller.scrolledTextCreator(
                x=X+40, y=Y+40, width=240, height=80, root=R, classname=f"{clinicId}_name",
                bg="#f1feff", hasBorder=False,
                text=clinics.clinic.name, font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            clinicId = self.controller.scrolledTextCreator(
                x=X+320, y=Y+35, width=200, height=80, root=R, classname=f"{clinicId}_id",
                bg="#f1feff", hasBorder=False,
                text=clinics.clinicId, font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            clinicContact = self.controller.scrolledTextCreator(
                x=X+560, y=Y+40, width=200, height=80, root=R, classname=f"{clinicId}_contact",
                bg="#f1feff", hasBorder=False,
                text=clinics.clinic.phoneNum, font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            clinicOpHrs = self.controller.scrolledTextCreator(
                x=X+800, y=Y+35, width=200, height=80, root=R, classname=f"{clinicId}_opHrs",
                bg="#f1feff", hasBorder=False,
                text=clinics.clinic.clinicHrs, font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            clinicAddress = self.controller.scrolledTextCreator(
                x=X+1040, y=Y+30, width=200, height=80, root=R, classname=f"{clinicId}_address",
                bg="#f1feff", hasBorder=False,
                text=clinics.clinic.address, font=FONT, fg=BLACK,
                isDisabled=True, isJustified="center",
                hasVbar=False
            )
            COORDS = (
                COORDS[0], COORDS[1] + 120
            )

    def deleteClinic(self):
        result = messagebox.askyesno(
            "Delete Clinic", "Are you sure you want to delete this clinic account?",
        )
        if result:
            prisma = self.prisma
            prisma.clinicenrolment.update(
                where={
                    "clinicId": self.user.id
                },
                data={
                    "clinicAdmin": {
                        "disconnect": True
                    }
                }
            )
            self.controller.threadCreator(
                self.manageClinic, cancelled=True)
        else:
            return

    def resetClinicInfo(self, req: Clinic):
        prisma = self.prisma
        prisma.clinic.update(
            where={
                "AND": [{"status": "APPROVED"}, {"clinic": {"is": {"admin": {"some": {"userId": self.user.id}}}}}]
            },
            include={
                "clinic": True,
                "govRegDocSystem": True
            }
        )
        self.controller.threadCreator(self.manageClinic, confirmed=True)

    def manageClinicInfo(self, req: Clinic):
        self.controller.threadCreator(
            self.createManageClinicInfo, req=req)

    def createManageClinicInfo(self, req: Clinic):
        R = self.clinicInfoFrame
        clinicName = f"Clinic:{req.name}"
        clinicAddress = f"Address:{req.address}"
        clinicContactNo = f"ContactNo:{req.phoneNum}"
        clinicCity = f"City:{req.city}"
        clinicState = f"State:{req.state}"
        clinicZip = f"Zip:{req.zip}"
        clinicOpHrs = f"OpHrs:{req.clinicHrs}"
        clinicImage = f"Img:{req.clinicImg}"

        self.controller.scrolledTextCreator(
            x=100, y=300, width=640, height=80, root=R, classname=f"{req.id}_name",
            bg=WHITE, hasBorder=BLACK,
            text=f"{clinicName}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )
        self.controller.scrolledTextCreator(
            x=100, y=420, width=640, height=80, root=R, classname="clinic_address",
            bg=WHITE, hasBorder=BLACK,
            text=f"{clinicAddress}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )
        self.controller.scrolledTextCreator(
            x=100, y=540, width=300, height=80, root=R, classname="clinic_contactno",
            bg=WHITE, hasBorder=BLACK,
            text=f"{clinicContactNo}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )
        self.controller.scrolledTextCreator(
            x=440, y=540, width=300, height=80, root=R, classname="clinic_city",
            bg=WHITE, hasBorder=BLACK,
            text=f"{clinicCity}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )
        self.controller.scrolledTextCreator(
            x=100, y=660, width=300, height=80, root=R, classname="clinic_state",
            bg=WHITE, hasBorder=BLACK,
            text=f"{clinicState}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )
        self.controller.scrolledTextCreator(
            x=440, y=660, width=300, height=80, root=R, classname="clinic_zip",
            bg=WHITE, hasBorder=BLACK,
            text=f"{clinicZip}", font=("Inter", 12), fg=BLACK,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )
        KL = timezone("Asia/Kuala_Lumpur")
        fmt = "%I:%M%p"
        self.controller.scrolledTextCreator(
            x=100, y=800, width=640, height=80, root=R, classname="clinic_opHours",
            bg="#463f9d", hasBorder=False,
            text=f"{clinicOpHrs}", font=("Inter", 12), fg=WHITE,
            isDisabled=True, isJustified=True, justification="left",
            hasVbar=False
        )
        img = self.controller.decodingBase64Data(req.clinicImg)
        img = ImageOps.contain(img, (520, 520), Image.Resampling.BICUBIC)
        self.clinicImage = self.controller.buttonCreator(
            x=980, y=320, classname=f"req_loadedclinic_image_{clinicImage}", root=R,
            ipath="assets/BrowseClinic/Patient/BrowseSingleClinic/ClinicImagePlaceholder.png",
            bg=WHITE,isPlaced=True,
            )
        self.controller.imageDict[f"req_loadedclinic_image_{clinicImage}"] = ImageTk.PhotoImage(
                img
            )
        newImage = self.controller.imageDict[f"req_loadedclinic_image_{clinicImage}"]
        self.clinicImage.configure(image=newImage, width=520, height=520)
        self.clinicImage.place(x=980, y=320, width=520, height=520)
        self.controller.scrolledTextCreator(
                x=1140, y=860, width=200, height=80, root=R,
                classname=f"req_loadedclinic_name_{clinicImage}",
                bg="#ecf2ff", hasBorder=False,
                text=req.name, font=("Inter", 12), fg=BLACK,
                isDisabled=True, isJustified=True,
                hasVbar=False,
            )

        self.clinicInfoFrame.grid()
        self.clinicInfoFrame.tkraise()

