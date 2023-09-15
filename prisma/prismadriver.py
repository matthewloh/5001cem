import json
from datetime import datetime, timedelta

from dotenv import load_dotenv
from pendulum import timezone

from prisma import Prisma

load_dotenv()


prisma = Prisma(auto_register=True)
prisma.connect()


def prismaCreateClinicAdmin():
    prisma.clinicadmin.delete_many()
    prisma.user.delete_many()
    prisma.clinic.delete_many()
    admin = prisma.clinicadmin.create(
        data={
            "user": {
                "create": {
                    "fullName": "Clinic Admin",
                    "email": "idk@test.com",
                    "password": "12345678",
                    "contactNo": "12345678",
                }
            },
            "clinic": {
                "create": {
                    "address": "123, Jalan ABC",
                    "name": "ABC Clinic",
                    "phoneNum": "12345678",
                    "city": "Kuala Lumpur",
                    "state": "Kuala Lumpur",
                    "zip": "12345",
                }
            },
        },
        include={"user": True, "clinic": True},
    )
    # admin = prisma.clinicadmin.find_first()
    print(admin.json(indent=2))
    print(admin.user.json(indent=4))
    print(admin.clinic.json(indent=6))


""" 
-- Backend Process Flow --
1. Create Clinic Admin
2. Create the Clinic
3. Apply for Government Registered Doctor
4. Create the Government Official
5. Approve the Clinic
6. Create Doctor
7. Doctor get in clinic
8. Create Patient
9. Patient browse Doctor
10. Patient browse Clinic
11. Patient Make Appointment
12. Doctor Approve Appointment
13. Patient Get Prescription
14. Patient Complete Appointment
15. Patient Rate Doctor
"""

if __name__ == "__main__":
    prismaCreateClinicAdmin()
