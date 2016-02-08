from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic import View

from django.contrib.auth.models import User

from account.decorators import login_required

from .hooks import hookset
from .proxies import ActivityState
from .models import ActivitySessionState
from .signals import (
    activity_start as activity_start_signal,
    activity_play as activity_play_signal
)
from .utils import load_path_attr


class ActivityMixin(object):

    activity_key = None
    base_template_name = "pinax/lms/activities/base.html"

    def get_activity_class(self):
        return load_path_attr(self.activity_class_path)

    def get_activity_state(self):
        return ActivityState(
            self.request,
            activity_key=self.activity_key,
            activity_class_path=self.activity_class_path,
        )

    def get_cancel_url(self):
        return reverse("dashboard")

    def get_completed_url(self):
        return reverse("dashboard")

    def get_activity_url(self):
        return reverse("activity", kwargs=dict(activity_key=self.activity_key))

    def get_activity(self):
        return self.activity_class(
            self.activity_state.latest,
            self.activity_state,
            **self.get_activity_kwargs()
        )

    def get_extra_context(self, **kwargs):
        kwargs.update({
            "base_template": self.base_template_name
        })
        return kwargs

    def get_activity_kwargs(self, **kwargs):
        kwargs.setdefault("parameters", {})
        kwargs.update({
            "activity_url": self.get_activity_url(),
            "completed_url": self.get_completed_url(),
            "cancel_url": self.get_cancel_url(),
            "extra_context": self.get_extra_context()
        })
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        if self.activity_key is None:
            self.activity_key = kwargs.get("key")
        self.activity_class_path = hookset.activity_class_path(*args, **kwargs)
        if self.activity_class_path is None:
            raise Http404
        self.activity_class = self.get_activity_class()
        self.activity_state = self.get_activity_state()
        return super(ActivityMixin, self).dispatch(request, *args, **kwargs)


class ActivityView(ActivityMixin, View):

    def get(self, request, *args, **kwargs):
        activity = self.get_activity()
        if self.activity_state.progression == "start":  # Must mean you are just starting out
            return render(request, "pinax/lms/activities/start_activity.html", {"activity": activity})
        activity_play_signal.send(sender=ActivityView, activity_key=self.activity_key, activity_session_state=self.activity_state.latest, request=self.request)
        return activity.handle_get_request(self.request)

    def post(self, request, *args, **kwargs):
        return getattr(self, "_{}".format(self.activity_state.progression))()

    def _continue(self):
        activity = self.get_activity()
        return activity.handle_post_request(self.request)

    def _start(self):
        self.activity_state.ensure_exists()
        activity_start_signal.send(sender=ActivityView, activity_key=self.activity_key, activity_state=self.activity_state, request=self.request)
        return redirect(self.get_activity_url())

    def _repeat(self):
        activity_start_signal.send(sender=ActivityView, activity_key=self.activity_key, activity_state=self.activity_state, request=self.request)
        return redirect(self.get_activity_url())

    def _completed(self):
        return redirect(self.get_completed_url())


@login_required
def staff_dashboard(request):

    if not request.user.is_staff:
        raise Http404

    activities = []

    for key, activity_class_path in hookset.all_activities():
        activity = load_path_attr(activity_class_path)
        activity_states = ActivityState.objects.filter(activity_key=key)
        completed_activity_states = activity_states.exclude(completed_count=0)
        activity_session_states = ActivitySessionState.objects.filter(activity_key=key)
        completed_activity_session_states = activity_session_states.filter(completed__isnull=False)

        activities.append({
            "activity_key": key,
            "title": activity.title,
            "activity_states": activity_states,
            "completed_activity_states": completed_activity_states,
            "activity_session_states": activity_session_states,
            "completed_activity_session_states": completed_activity_session_states,
        })
    return render(request, "staff_dashboard.html", {
        "users": User.objects.all(),
        "activity_states": ActivityState.objects.all(),
        "activity_session_states": ActivitySessionState.objects.all(),
        "activities": activities,
    })


@login_required
def staff_activity_detail(request, activity_key):

    if not request.user.is_staff:
        raise Http404

    activity_states = ActivityState.objects.filter(activity_key=activity_key)
    activity_session_states = ActivitySessionState.objects.filter(activity_key=activity_key)

    return render(request, "staff_activity_detail.html", {
        "activity_states": activity_states,
        "activity_session_states": activity_session_states,
    })
