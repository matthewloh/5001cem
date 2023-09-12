import json
from datetime import datetime, timedelta

from dotenv import load_dotenv
from pendulum import timezone

from prisma import Prisma

load_dotenv()


prisma = Prisma(auto_register=True)
prisma.connect()


def prismaShowAll():
    prisma.user.delete_many()
    # newUser = prisma.user.create(
    #     data={
    #         "fullName": "John Doe",
    #         "email": "test@gmail.com",
    #         "contactNo": "1234567890",
    #         "password": "fakehash",
    #     }
    # )
    # print(newUser.json(indent=2))
    # users = prisma.user.find_many()
    # for u in users:
    #     print(u.json(indent=2))


if __name__ == "__main__":
    prismaShowAll()
