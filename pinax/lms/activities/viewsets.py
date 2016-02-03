import functools

from django.conf import settings
from django.conf.urls import url
from django.http import Http404
from django.views.generic import View

from pinax.eventlog.models import log

from .models import (
    ActivityState,
    load_path_attr,
    get_activity_state,
)
from .signals import (
    activity_start as activity_start_signal,
    activity_play as activity_play_signal,
    activity_completed as activity_completed_signal
)


class ActivityViewSet(View):

    @classmethod
    def as_view(cls, **initkwargs):
        phase = initkwargs.pop("phase")
        view = super(ActivityViewSet, cls).as_view(**initkwargs)

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            mapping = {
                "start": ["post"],
                "play": ["get", "post"],
                "completed": ["get"],
            }
            for method in mapping[phase]:
                setattr(self, method, getattr(self, phase))
            self.args = args
            self.kwargs = kwargs
            self.request = request
            return self.dispatch(request, *args, **kwargs)

        functools.update_wrapper(view, cls, updated=())
        functools.update_wrapper(view, cls.dispatch, assigned=())
        return view

    @classmethod
    def as_urls(cls):
        urls = [
            url(r"(?P<slug>[\w\-]+)/start/$", cls.as_view("start"), name="activity_start"),
            url(r"(?P<slug>[\w\-]+)/play/$", cls.as_view("play"), name="activity_play"),
            url(r"(?P<slug>[\w\-]+)/completed/$", cls.as_view("completed"), name="activity_completed"),
        ]
        return urls

    def get_activity_class(self):
        activity_class_path = settings.ACTIVITIES.get(self.kwargs["slug"])
        if activity_class_path is None:
            raise Http404()
        return load_path_attr(activity_class_path)

    def start(self):
        Activity = self.get_activity_class()
        activity_state, _ = (
            ActivityState.objects.get_or_create(
                user=self.request.user,
                activity_slug=self.kwargs["slug"],
            )
        )
        if activity_state.completed_count > 0 and not Activity.repeatable:
            self.log_not_repeatable()
            return self.not_repeatable()
        activity = Activity(activity_state.latest, activity_state)
        activity_start_signal.send(
            sender=self.request.user,
            slug=self.kwargs["slug"],
            activity_state=activity_state,
            request=self.request
        )
        return activity.start(self.request, **self.kwargs)

    def play(self):
        Activity = self.get_activity_class()
        activity_state = get_activity_state(self.request.user, self.kwargs["slug"])
        if activity_state is None:
            self.log_not_started()
            return self.not_started()
        activity = Activity(activity_state.latest, activity_state)
        activity_play_signal.send(
            sender=self.request.user,
            slug=self.kwargs["slug"],
            activity_occurrence_state=activity_state.latest,
            request=self.request,
        )
        return activity.play(self.request)

    def completed(self):
        Activity = self.get_activity_class()
        activity_state = get_activity_state(self.request.user, self.kwargs["slug"])
        if activity_state is None:
            self.log_not_started()
            return self.not_started()
        last_completed = activity_state.last_completed
        if last_completed is None:
            self.log_not_completed()
            return self.not_completed()
        activity = Activity(last_completed, activity_state)
        activity_completed_signal.send(
            sender=self.request.user,
            slug=self.kwargs["slug"],
            activity_occurrence_state=last_completed,
            request=self.request,
        )
        return activity.completed(self.request)

    def log_not_repeatable(self):
        log(
            user=self.request.user,
            action="ACTIVITY_ERROR",
            extra={
                "error": "not repeatable",
                "slug": self.kwargs["slug"],
            }
        )

    def log_not_started(self):
        log(
            user=self.request.user,
            action="ACTIVITY_ERROR",
            extra={
                "error": "not started",
                "slug": self.kwargs["slug"],
            }
        )

    def log_not_completed(self):
        log(
            user=self.request.user,
            action="ACTIVITY_ERROR",
            extra={
                "error": "not completed",
                "slug": self.kwargs["slug"],
            }
        )
