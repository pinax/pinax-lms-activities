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
    user = models.OneToOneField(User)

    data = jsonfield.JSONField(default=dict)

    @classmethod
    def for_user(cls, user):
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

    user = models.ForeignKey(User)
    activity_key = models.CharField(max_length=50)

    # how many sessions have been completed by this user
    completed_count = models.IntegerField(default=0)

    data = jsonfield.JSONField(default=dict)

    class Meta:
        unique_together = [("user", "activity_key")]

    @property
    def in_progress(self):
        try:
            return ActivitySessionState.objects.get(
                user=self.user,
                activity_key=self.activity_key,
                completed=None
            )
        except ActivitySessionState.DoesNotExist:
            return None

    @property
    def latest(self):
        session, _ = ActivitySessionState.objects.get_or_create(
            user=self.user,
            activity_key=self.activity_key,
            completed=None
        )
        return session

    @property
    def last_completed(self):
        return ActivitySessionState.objects.filter(
            user=self.user,
            activity_key=self.activity_key,
            completed__isnull=False
        ).order_by("-started").first()

    @property
    def all_sessions(self):
        return ActivitySessionState.objects.filter(
            user=self.user,
            activity_key=self.activity_key,
        ).order_by("started")

    @classmethod
    def state_for_user(cls, user, activity_key):
        return cls.objects.filter(user=user, activity_key=activity_key).first()


class ActivitySessionState(models.Model):
    """
    this stores the state of a particular session of a particular user
    doing a particular activity.
    """

    user = models.ForeignKey(User)
    activity_key = models.CharField(max_length=50)

    started = models.DateTimeField(default=timezone.now)
    completed = models.DateTimeField(null=True)  # NULL means in progress

    data = jsonfield.JSONField(default=dict)

    class Meta:
        unique_together = [("user", "activity_key", "started")]

    def mark_completed(self):
        self.completed = timezone.now()
        self.save()
        activity_state = ActivityState.objects.get(
            user=self.user,
            activity_key=self.activity_key
        )
        activity_state.completed_count = models.F("completed_count") + 1
        activity_state.save()


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
