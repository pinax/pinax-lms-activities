from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User

import jsonfield

from .hooks import hookset
from .utils import load_path_attr


class UserState(models.Model):
    """
    this stores the overall state of a particular user.
    """
    user = models.OneToOneField(User, null=True)

    data = jsonfield.JSONField(default=dict, blank=True)

    @classmethod
    def for_user(cls, user):
        assert user.is_authenticated(), "user must be authenticated"
        user_state, _ = cls.objects.get_or_create(user=user)
        return user_state

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value
        self.save()


class ActivityState(models.Model):
    """
    this stores the overall state of a particular user doing a particular
    activity across all sessions of that activity.
    """

    user = models.ForeignKey(User, null=True)
    activity_key = models.CharField(max_length=300)
    activity_class_path = models.CharField(max_length=300)

    # how many sessions have been completed by this user
    completed_count = models.IntegerField(default=0)

    data = jsonfield.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = [("user", "activity_key")]

    @property
    def activity_class(self):
        return load_path_attr(self.activity_class_path)

    @property
    def in_progress(self):
        return next(iter(self.sessions.filter(completed=None)), None)

    @property
    def latest(self):
        session, _ = self.sessions.get_or_create(completed=None)
        return session

    @property
    def last_completed(self):
        return self.sessions.filter(completed__isnull=False).order_by("-started").first()

    @property
    def all_sessions(self):
        return self.sessions.order_by("started")

    @classmethod
    def state_for_user(cls, user, activity_key):
        assert user.is_authenticated(), "user must be authenticated"
        return cls.objects.filter(user=user, activity_key=activity_key).first()

    @property
    def progression(self):
        if self.in_progress:
            return "continue"
        elif self.activity_class.repeatable:
            return "repeat"
        else:
            return "completed"


class ActivitySessionState(models.Model):
    """
    this stores the state of a particular session of a particular user
    doing a particular activity.
    """

    activity_state = models.ForeignKey(ActivityState, related_name="sessions")

    started = models.DateTimeField(default=timezone.now)
    completed = models.DateTimeField(null=True)  # NULL means in progress

    data = jsonfield.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = [("activity_state", "started")]

    def mark_completed(self):
        self.completed = timezone.now()
        self.save()
        self.activity_state.completed_count = models.F("completed_count") + 1
        self.activity_state.save()


def activities_for_user(user):

    activities = {
        "available": [],
        "inprogress": [],
        "completed": [],
        "repeatable": []
    }

    for key, activity_class_path in hookset.all_activities():
        activity = load_path_attr(activity_class_path)
        state = ActivityState.state_for_user(user, key)
        user_num_completions = ActivitySessionState.objects.filter(
            user=user,
            activity_key=key,
            completed__isnull=False
        ).count()
        activity_entry = {
            "activity_key": key,
            "title": activity.title,
            "description": activity.description,
            "state": state,
            "user_num_completions": user_num_completions,
            "repeatable": activity.repeatable,
        }
        if state:
            if state.in_progress:
                activities["inprogress"].append(activity_entry)
            elif activity.repeatable:
                activities["repeatable"].append(activity_entry)
            else:
                activities["completed"].append(activity_entry)
        else:
            activities["available"].append(activity_entry)
    return activities
