from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic import View

from django.contrib.auth.models import User

from account.decorators import login_required
from account.mixins import LoginRequiredMixin

from .hooks import hookset
from .models import (
    ActivityState,
    ActivitySessionState,
    load_path_attr
)
from .signals import (
    activity_start as activity_start_signal,
    activity_play as activity_play_signal
)


class ActivityMixin(object):

    def get_activity_class(self):
        return load_path_attr(self.activity_class_path)

    def get_activity_state(self):
        return ActivityState.state_for_user(self.request.user, self.activity_key)

    def create_activity_state(self):
        self.activity_state = ActivityState.objects.create(user=self.request.user, activity_key=self.activity_key)

    def get_cancel_url(self):
        return reverse("dashboard")

    def get_completed_url(self):
        return reverse("dashboard")

    def get_activity_url(self):
        return reverse("activity", kwargs=dict(activity_key=self.activity_key))

    def get_activity(self):
        return self.activity_class(
            self.activity_state.latest if self.activity_state else None,
            self.activity_state,
            activity_url=self.get_activity_url(),
            completed_url=self.get_completed_url(),
            cancel_url=self.get_cancel_url()
        )

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.activity_key = kwargs.get("slug")
        self.activity_class_path = hookset.activity_class_path(kwargs.get("slug"))
        if self.activity_class_path is None:
            raise Http404
        self.activity_class = self.get_activity_class()
        self.activity_state = self.get_activity_state()
        return super(ActivityMixin, self).dispatch(request, *args, **kwargs)


class ActivityView(LoginRequiredMixin, ActivityMixin, View):

    def get(self, request, *args, **kwargs):
        activity = self.get_activity()
        if self.activity_state is None:  # Must mean you are just starting out
            return render(request, "pinax/lms/activities/start_activity.html", {"activity": activity})
        activity_play_signal.send(sender=ActivityView, activity_key=self.activity_key, activity_session_state=self.activity_state.latest, request=self.request)
        return activity.handle_get_request(self.request)

    def post(self, request, *args, **kwargs):
        if request.POST.get("start"):  # be explicit about starts so we are not guessing if you are starting a new or a subsequent time
            if self.activity_state is None:
                self.create_activity_state()
            activity_start_signal.send(sender=ActivityView, activity_key=self.activity_key, activity_state=self.activity_state, request=self.request)
            return redirect(self.get_activity_url())
        if self.activity_state.completed_count > 0 and not self.activity_class.repeatable:
            return redirect(self.get_completed_url())  # Error
        activity = self.get_activity()
        return activity.handle_post_request(self.request)


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
            "slug": slug,
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
