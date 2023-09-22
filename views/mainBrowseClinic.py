import calendar
import datetime as dt
import re
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from resource.basewindow import ElementCreator, gridGenerator
from resource.static import *
from tkinter import *
from tkinter import messagebox

import tkintermapview
from pendulum import timezone
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from ttkbootstrap.dialogs.dialogs import DatePickerDialog
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.toast import ToastNotification

from views.browseClinic.adminBrowse import AdminBrowseClinic
from views.browseClinic.doctorBrowse import DoctorBrowseClinic
from views.browseClinic.officerBrowse import OfficerBrowseClinic
from views.browseClinic.patientBrowse import PatientBrowseClinic


class MainBrowseClinic:
    def __init__(self, controller: ElementCreator = None):
        self.controller = controller
        self.prisma = self.controller.mainPrisma

    def loadRoleAssets(self, patient: bool = False, doctor: bool = False, clinicAdmin: bool = False, govofficer: bool = False):
        if patient:
            self.primarypanel = PatientBrowseClinic(
                parent=self, controller=self.controller)
            self.primarypanel.grid(
                row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        elif doctor:
            self.primarypanel = DoctorBrowseClinic(
                parent=self, controller=self.controller)
            self.primarypanel.grid(
                row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        elif clinicAdmin:
            self.primarypanel = AdminBrowseClinic(
                parent=self, controller=self.controller)
            self.primarypanel.grid(
                row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        elif govofficer:
            self.primarypanel = OfficerBrowseClinic(
                parent=self, controller=self.controller)
            self.primarypanel.grid(
                row=0, column=12, columnspan=84, rowspan=54, sticky=NSEW)
        else:
            return
