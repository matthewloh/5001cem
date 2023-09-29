

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

from views.clinicRequests.adminGRDRequests import AdminGRDRequest
from views.clinicRequests.officerGRDRequests import OfficerGRDRequests


class MainGRDRequestsInterface:
    def __init__(self, controller: ElementCreator = None, parent=None):
        self.controller = controller
        self.parent = parent
        self.prisma = self.controller.mainPrisma

    def loadRoleAssets(self, govofficer: bool = False, clinicAdmin: bool = False):
        if govofficer:
            self.primarypanel = OfficerGRDRequests(
                parent=self.parent, controller=self.controller)
        elif clinicAdmin:
            self.primarypanel = AdminGRDRequest(
                parent=self.parent, controller=self.controller)
        else:
            return
