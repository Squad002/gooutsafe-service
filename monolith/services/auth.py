from flask import session, redirect
from flask_login import current_user
from monolith import login_manager
from monolith.models import User, HealthAuthority, Operator, LoginUser
from monolith import api
from functools import wraps


def operator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session["role"] != "operator":
            return login_manager.unauthorized()
            # need to implement logic for logout maybe? or templated error page
            pass
        return f(*args, **kwargs)

    return decorated_function


def authority_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authenticated = current_user.is_authenticated
        if not authenticated:
            return redirect("/login/authority")
        elif session["role"] != "authority":
            return login_manager.unauthorized()
            # need to implement logic for logout maybe? or templated error page
            pass
        return f(*args, **kwargs)

    return decorated_function


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session["role"] != "user":
            return login_manager.unauthorized()
        return f(*args, **kwargs)

    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    user_data = None

    if session["role"] == "user":
        user_data = api.get_user_by_id(user_id)
    elif session["role"] == "operator":
        user_data = api.get_operator_by_id(user_id)
    elif session["role"] == "authority":
        user_data = api.get_authority_by_id(user_id)

    user = LoginUser(user_data)
    user.is_authenticated = True
    user.is_anonymous = False

    return user
