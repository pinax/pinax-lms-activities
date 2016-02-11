from . import models


class BaseProxy(object):

    model = None

    def __init__(self):
        self.obj = self.get()

    @property
    def obj(self):
        return getattr(self, "_obj", None)

    @obj.setter
    def obj(self, value):
        self.exists = value is not None
        self._obj = value

    def get_session_key(self, extra=None):
        if extra is None:
            extra = []
        key = [self.model._meta.object_name.lower()]
        key.extend(extra)
        return "proxy_{}".format("-".join(key))

    def get(self):
        return self.lookup(self.request.session.get(self.get_session_key()))

    def ensure_exists(self):
        if not self.exists:
            identifier, self.obj = self.create()
            self.request.session[self.get_session_key()] = identifier

    def lookup(self):
        raise NotImplementedError()

    def create(self):
        raise NotImplementedError()


class ActivityState(BaseProxy):

    model = models.ActivityState

    def __init__(self, request, activity_key, activity_class_path):
        self.request = request
        self.user = request.user
        self.activity_key = activity_key
        self.activity_class_path = activity_class_path
        super(ActivityState, self).__init__()

    def get_session_key(self):
        extra = [self.activity_key]
        return super(ActivityState, self).get_session_key(extra)

    def lookup(self, identifier):
        if identifier is not None:
            return next(iter(self.model.objects.filter(pk=identifier)), None)
        if self.request.user.is_authenticated():
            return next(iter(self.model.objects.filter(user=self.user, activity_key=self.activity_key)), None)

    def create(self):
        kwargs = {
            "activity_key": self.activity_key,
            "activity_class_path": self.activity_class_path,
        }
        if self.user.is_authenticated():
            kwargs["user"] = self.user
        obj = self.model.objects.create(**kwargs)
        return obj.pk, obj

    @property
    def completed_count(self):
        if self.exists:
            return self.obj.completed_count
        return 0

    @property
    def data(self):
        if self.exists:
            return self.obj.data
        return {}

    @property
    def in_progress(self):
        if self.exists:
            return self.obj.in_progress
        return None

    @property
    def latest(self):
        if self.exists:
            return self.obj.latest
        return None

    @property
    def last_completed(self):
        if self.exists:
            return self.obj.last_completed
        return None

    @property
    def all_sessions(self):
        if self.exists:
            return self.obj.all_sessions
        return models.ActivitySessionState.objects.none()

    @property
    def progression(self):
        if self.exists:
            return self.obj.progression
        return "start"
