

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
from views.patientRequests.adminManageRequests import AdminManagePatientRequests
from views.patientRequests.doctorViewRequests import DoctorViewPatientRequests
from views.patientRequests.patientCreateRequests import PatientCreateRequests


class MainPatientRequestsInterface:
    def __init__(self, controller: ElementCreator = None, parent=None):
        self.controller = controller
        self.parent = parent
        self.prisma = self.controller.mainPrisma

    def loadRoleAssets(self, patient: bool = False, doctor: bool = False, clinicAdmin: bool = False, govofficer: bool = False):
        if patient:
            self.primarypanel = PatientCreateRequests(
                parent=self.parent, controller=self.controller)
        elif doctor:
            self.primarypanel = DoctorViewPatientRequests(
                parent=self.parent, controller=self.controller)
        elif clinicAdmin:
            self.primarypanel = AdminManagePatientRequests(
                parent=self.parent, controller=self.controller)
        else:
            return
