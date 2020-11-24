from datetime import date
from werkzeug.datastructures import MultiDict


user = dict(
    email="mariobrown@gmail.com",
    firstname="mario",
    lastname="brown",
    password="1234",
    dateofbirth=date(1995, 12, 31),
    fiscalcode="RSSMRA95T31H501R",
    phonenumber="+39331303313094",
)

user2 = dict(
    email="mariobrown@gmail.com",
    firstname="mario",
    lastname="brown",
    password="1234",
    dateofbirth="1995-12-31",
    fiscalcode="RSSMRA95T31H501R",
    phonenumber="+39331303313094",
)


user3 = dict(
    email="giovanniyellow@gmail.com",
    firstname="giovanni",
    lastname="yellow",
    password="5678",
    dateofbirth="1994-05-04",
    fiscalcode="RSSGVA95T31J591K",
    phonenumber="+39334334683094",
)

operator = dict(
    email="giuseppebrown@lalocanda.com",
    firstname="giuseppe",
    lastname="yellow",
    password="5678",
    dateofbirth="01/01/1963",
    fiscalcode="YLLGPP63A01B519O",
    phonenumber="+39331303313094",
)

operator2 = dict(
    email="giuseppebrown@lalocanda.com",
    firstname="giuseppe",
    lastname="yellow",
    password="5678",
    dateofbirth="1963-01-01",
    fiscalcode="YLLGPP63A01B519O",
    phonenumber="+39331303313094",
)

health_authority = dict(
    email="canicatti@asl.it",
    name="ASL Canicattì",
    password="cani123",
    phonenumber="0808403849",
    country="Italy",
    state="AG",
    city="Canicattì",
    lat=37.36,
    lon=13.84,
)

health_authority2 = dict(
    email="roma@asl.it",
    name="ASL Roma",
    password="romasqpr",
    phonenumber=" 0639741322",
    country="Italy",
    state="RM",
    city="Roma",
    lat=41.89,
    lon=12.49,
)

restaurant = dict(
    name="Trattoria da Fabio",
    phonenumber=555123456,
    lat=40.720586,
    lon=10.10,
    time_of_stay=30,
    operator_id=1,
)

precaution1 = dict(name="Amuchina")
precaution2 = dict(name="Social distancing")
precaution3 = dict(name="Disposable menu")
precaution4 = dict(name="Personnel required to wash hands regularly")
precaution5 = dict(name="Obligatory masks for staff in public areas")
precaution6 = dict(name="Tables sanitized at the end of each meal")
precautions = [
    precaution1,
    precaution2,
    precaution3,
    precaution4,
    precaution5,
    precaution6,
]

table = dict(name="A10", seats=10, restaurant_id=1)
table2 = dict(name="B5", seats=10, restaurant_id=1)

booking1 = dict(
    number_persons=1,
    booking_hour="8:00 - 8:30",
    booking_date=date.today(),
)
booking2 = dict(
    number_persons=4,
    booking_hour="8:00 - 8:30",
    booking_date=date.today(),
)
booking = [booking1, booking2]

booking_people = {
    "people-0-email": "tommaso@tommaso.com",
    "people-0-firstname": "tommaso",
    "people-0-lastname": "tommaso",
    "people-0-fiscalcode": "123",
    "people-1-email": "simone@simone.com",
    "people-1-firstname": "simone",
    "people-1-lastname": "simone",
    "people-1-fiscalcode": "456",
    "people-2-email": "alessandro@alessandro.com",
    "people-2-firstname": "alessandro",
    "people-2-lastname": "alessandro",
    "people-2-fiscalcode": "789",
}

booking_people_double_fiscal_code = {
    "people-0-email": "tommaso@tommaso.com",
    "people-0-firstname": "tommaso",
    "people-0-lastname": "tommaso",
    "people-0-fiscalcode": "123",
    "people-1-email": "simone@simone.com",
    "people-1-firstname": "simone",
    "people-1-lastname": "simone",
    "people-1-fiscalcode": "456",
    "people-2-email": "tommaso@tommaso.com",
    "people-2-firstname": "tommaso",
    "people-2-lastname": "tommaso",
    "people-2-fiscalcode": "123",
}

booking_people_double_email = {
    "people-0-email": "tommaso@tommaso.com",
    "people-0-firstname": "tommaso",
    "people-0-lastname": "tommaso",
    "people-0-fiscalcode": "123",
    "people-1-email": "simone@simone.com",
    "people-1-firstname": "simone",
    "people-1-lastname": "simone",
    "people-1-fiscalcode": "456",
    "people-2-email": "tommaso@tommaso.com",
    "people-2-firstname": "alessandro",
    "people-2-lastname": "alessandro",
    "people-2-fiscalcode": "789",
}


checkin_people = {"people": "1"}


checkin_multiple_people = MultiDict(
    [
        ("people", "1"),
        ("people", "2"),
        ("people", "3"),
        ("people", "4"),
    ]
)

checkin_multiple_people2 = MultiDict(
    [
        ("people", "2"),
        ("people", "3"),
        ("people", "4"),
        ("people", "5"),
    ]
)
