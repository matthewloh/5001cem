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




class OfficerBrowseClinic(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None):
        super().__init__(parent, width=1, height=1, bg="#dee8e0", name="browseclinicpanel")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 84, 54, "#dee8e0")
        self.grid(row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        
        self.prisma = self.controller.mainPrisma
        self.createFrames()
        self.createElements()

    def createFrames(self):
        pass

    def createElements(self):
        self.controller.labelCreator(
            ipath=r"assets/Dashboard/OfficerAssets/OfficerPrimaryPanelBG.png",
            x=0, y=0, classname="browseclinicbg", root=self
        )

        exampleList = []
        [exampleList.append("Thing " + str(i))
         for i in range(30) if i % 2 == 0]
        h = len(exampleList) * 120
        if h < 600:
            h = 600
        self.exampleScrolledFrame = ScrolledFrame(
            master=self, width=1500, height=h, autohide=True, bootstyle="officer-bg"
        )
        self.exampleScrolledFrame.grid_propagate(False)
        self.exampleScrolledFrame.place(x=80, y=280, width=1500, height=620)
        initialcoordinates = (20, 20)
        for thing in exampleList:
            x = initialcoordinates[0]
            y = initialcoordinates[1]
            self.controller.textElement(
                ipath="assets/Dashboard/clinicdetailsbg.png", x=x, y=y,
                classname=f"thing{thing}", root=self.exampleScrolledFrame,
                text=thing, size=30, font=INTER,
                isPlaced=True,
            )
            self.controller.buttonCreator(
                ipath="assets/Dashboard/OfficerAssets/hideindicator.png",
                classname=f"hideindicator{thing}", root=self.exampleScrolledFrame,
                x=1300, y=y+20, buttonFunction=lambda t = thing: [print(f"hide {t}")],
                isPlaced=True,
            )
            self.controller.buttonCreator(
                ipath="assets/Dashboard/OfficerAssets/dustbin.png",
                classname=f"dustbin{thing}", root=self.exampleScrolledFrame,
                x=1380, y=y+20, buttonFunction=lambda t = thing: [print(f"delete {t}")],
                isPlaced=True
            )
            initialcoordinates = (
                initialcoordinates[0], initialcoordinates[1] + 120
            )

    

    # def loadClinicsRequests(self):
    #     pass

    # def loadViewDoctorSchedule(self):
    #     pass
