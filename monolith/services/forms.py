from wtforms.fields.html5 import DateField, EmailField, IntegerField
from wtforms import widgets, validators, SubmitField, SelectMultipleField
from flask_wtf import FlaskForm
import wtforms as f
from wtforms.validators import DataRequired, Length, NumberRange, Email
from datetime import date
from wtforms.fields import FormField, FieldList


class LoginForm(FlaskForm):
    email = f.StringField("Email", validators=[DataRequired()])
    password = f.PasswordField("Password", validators=[DataRequired()])
    display = ["email", "password"]


class UserForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    firstname = f.StringField(
        "First name", validators=[DataRequired()], render_kw={"placeholder": "Mario"}
    )
    lastname = f.StringField(
        "Last name", validators=[DataRequired()], render_kw={"placeholder": "Rossi"}
    )
    password = f.PasswordField("Password", validators=[DataRequired()])
    dateofbirth = DateField("Date of birth", validators=[DataRequired()])
    phonenumber = f.IntegerField("Phone", validators=[DataRequired()])
    fiscalcode = f.StringField("Fiscal Code", validators=[DataRequired()])
    display = [
        "email",
        "firstname",
        "lastname",
        "password",
        "dateofbirth",
        "phonenumber",
        "fiscalcode",
    ]


# TODO Validators are missing?
class OperatorForm(UserForm):
    # TODO validate fiscal code in a good proper way
    display = [
        "email",
        "firstname",
        "lastname",
        "password",
        "dateofbirth",
        "phonenumber",
        "fiscalcode",
    ]


class AuthorityForm(FlaskForm):
    email = f.StringField("Email", validators=[DataRequired()])
    name = f.StringField("Name", validators=[DataRequired()])
    password = f.PasswordField("Password", validators=[DataRequired()])
    phonenumber = f.IntegerField("Phone", validators=[DataRequired()])
    country = f.StringField("Country", validators=[DataRequired()])
    state = f.StringField("State", validators=[DataRequired()])
    city = f.StringField("City", validators=[DataRequired()])
    # TODO adding validators here causes two fails in the tests
    lat = f.DecimalField("Latitude", validators=[DataRequired()])
    lon = f.DecimalField("Longitude", validators=[DataRequired()])

    display = [
        "email",
        "name",
        "password",
        "country",
        "state",
        "city",
        "lat",
        "lon",
        "phonenumber",
    ]


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class CreateRestaurantForm(FlaskForm):
    name = f.StringField("Name", validators=[DataRequired()])
    lat = f.FloatField(
        "Latitude",
        validators=[
            DataRequired(),
            NumberRange(-90, 90, "Latitude must be between -90 and 90"),
        ],
    )
    lon = f.FloatField(
        "Longitude",
        validators=[
            DataRequired(),
            NumberRange(-180, 180, "Longitude must be between -180 and 180"),
        ],
    )
    phonenumber = f.IntegerField("Phone", validators=[DataRequired()])
    time_of_stay = f.RadioField(
        "Time of stay",
        choices=[(30, "30 minutes"), (90, "1:30 hour"), (180, "3 hours")],
        validators=[DataRequired()],
    )
    opening_hours = f.IntegerField(
        "Opening hours",
        validators=[DataRequired(), NumberRange(0, 24, "Not a valid hour")],
    )
    closing_hours = f.IntegerField(
        "Closing hours",
        validators=[DataRequired(), NumberRange(0, 24, "Not a valid hour")],
    )
    cuisine_type = f.SelectField(
        "Cuisine type",
        choices=[("ETHNIC", "Ethnic"), ("FAST_FOOD", "Fast Food"), ("PUB", "Pub")],
        validators=[DataRequired()],
    )

    precautions = [
        ("Amuchina", "Amuchina"),
        ("Social distancing", "Social distancing"),
        ("Disposable menu", "Disposable menu"),
        (
            "Personnel required to wash hands regularly",
            "Personnel required to wash hands regularly",
        ),
        (
            "Obligatory masks for staff in public areas",
            "Obligatory masks for staff in public areas",
        ),
        (
            "Tables sanitized at the end of each meal",
            "Tables sanitized at the end of each meal",
        ),
    ]
    prec_measures = MultiCheckboxField("Precautions", choices=precautions)

    display = [
        "name",
        "lat",
        "lon",
        "phonenumber",
        "opening_hours",
        "closing_hours",
        "cuisine_type",
        "time_of_stay",
        "prec_measures",
    ]


class CreateTableForm(FlaskForm):
    name = f.StringField("Name", validators=[DataRequired()])
    seats = f.IntegerField(
        "Seats",
        validators=[
            DataRequired(),
            NumberRange(
                0, 20, "The number of seats for each table must be between 0 and 20"
            ),
        ],
    )
    display = ["name", "seats"]


class AuthorityIdentifyForm(FlaskForm):
    duration = IntegerField(
        "Duration",
        validators=[
            DataRequired(message="This field must be a number."),
            NumberRange(
                min=1, max=60, message="The duration must be between 1 and 60."
            ),
        ],
    )
    identifier = f.StringField(
        "Identifier",
        validators=[DataRequired()],
        render_kw={"placeholder": "Use SSN, email or phone number"},
    )
    display = ["duration", "identifier"]


class ReviewForm(FlaskForm):
    rating = f.SelectField(
        "Your rating",
        coerce=int,
        choices=[
            (5, "5 - Awesome!"),
            (4, "4 - Very good"),
            (3, "3 - Average"),
            (2, "2 - Poor"),
            (1, "1 - Never again"),
        ],
    )
    message = f.TextAreaField(
        "Your review",
        validators=[
            Length(min=30, message="The review should be at least of 30 characters.")
        ],
    )
    message = f.TextAreaField(
        "Your review",
        validators=[
            Length(min=30, message="The review should be at least of 30 characters.")
        ],
    )
    display = ["rating", "message"]


class CreateBookingDateHourForm(FlaskForm):
    booking_date = DateField("Booking Date", default=date.today())
    submit = SubmitField("Submit")

    def validate(self):
        if self.booking_date.data < date.today():
            return False
        else:
            return True


def ConfirmBookingForm(size):
    class ConfirmBookingForm(FlaskForm):
        email = EmailField("Email", validators=[DataRequired(), Email()])
        firstname = f.StringField("Firstname", validators=[DataRequired()])
        lastname = f.StringField("Lastname", validators=[DataRequired()])
        fiscalcode = f.StringField(
            "Fiscal code", validators=[DataRequired(), Length(min=16, max=16)]
        )

    class ConfirmBookingForm(FlaskForm):
        people = FieldList(FormField(ConfirmBookingForm), min_entries=1)
        submit = SubmitField("Submit")

        def validate(self):
            for field in self.people.data:
                if (
                    field["email"] == ""
                    or field["firstname"] == ""
                    or field["lastname"] == ""
                    or field["fiscalcode"] == ""
                ):
                    return False
            return True

    fields = []
    for i in range(int(size)):
        fields.append(
            {
                "email": "",
                "firstname": "",
                "lastname": "",
                "fiscalcode": "",
            }
        )

    form = ConfirmBookingForm(people=fields)

    return form


class ChangePasswordForm(FlaskForm):
    new_password = f.PasswordField(
        label="New password",
        validators=[
            DataRequired(),
            validators.EqualTo("password_confirm", message="Passwords must match"),
        ],
    )
    password_confirm = f.PasswordField(
        label="Confirm new password", validators=[DataRequired()]
    )
    old_password = f.PasswordField(
        label="Type your old password here", validators=[DataRequired()]
    )
    display = ["new_password", "password_confirm", "old_password"]


class ChangeAnagraphicForm(FlaskForm):
    firstname = f.StringField("Firstname", validators=[DataRequired()])
    lastname = f.StringField("Lastname", validators=[DataRequired()])
    fiscalcode = f.StringField(
        "Fiscal code", validators=[DataRequired(), Length(min=16, max=16)]
    )
    dateofbirth = DateField("Date of birth", validators=[DataRequired()])
    password = f.PasswordField(
        label="Type your password here to confirm", validators=[DataRequired()]
    )
    display = ["firstname", "lastname", "fiscalcode", "dateofbirth", "password"]


class ChangeContactForm(FlaskForm):
    email = f.StringField("Email", validators=[DataRequired(), Email()])
    phonenumber = f.IntegerField("Phone", validators=[DataRequired()])
    password = f.PasswordField(
        label="Type your password here to confirm", validators=[DataRequired()]
    )
    display = ["email", "phonenumber", "password"]


class ChooseReservationData(FlaskForm):
    date = DateField("Date", default=date.today())
    submit = SubmitField("Submit")

    def validate(self):
        return True
