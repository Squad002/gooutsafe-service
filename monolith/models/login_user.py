class LoginUser(object):
    def __init__(self, *args, **kwargs):
        for dictionary in args:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

        self.is_authenticated = False
        self.is_active = True
        self.is_anonymous = True

    def get_id(self):
        return self.id
