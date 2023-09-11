from prisma import Prisma
import json
from datetime import datetime, timedelta
from pendulum import timezone

prisma = Prisma(auto_register=True)
prisma.connect()


def prismaShowAll():
    prisma.userprofile.delete_many()
    # newUser = prisma.userprofile.create(
    #     data={
    #         "fullName": "John Doe",
    #         "email": "test@gmail.com",
    #         "contactNo": "1234567890",
    #         "password": "fakehash",
    #     }
    # )
    # print(newUser.json(indent=2))
    # users = prisma.userprofile.find_many()
    # for u in users:
    #     print(u.json(indent=2))


if __name__ == "__main__":
    prismaShowAll()
