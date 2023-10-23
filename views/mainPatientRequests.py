from resource.basewindow import ElementCreator
from resource.static import *
from tkinter import *

from ttkbootstrap.constants import *

from views.patientRequests.adminManageRequests import \
    AdminManagePatientRequests
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
