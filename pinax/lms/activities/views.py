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
        return ActivityState.state_for_user(self.request.user, self.activity_slug)

    def create_activity_state(self):
        self.activity_state = ActivityState.objects.create(user=self.request.user, activity_slug=self.activity_slug)

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.activity_slug = kwargs.get("slug")
        self.activity_class_path = hookset.activity_class_path(kwargs.get("slug"))
        if self.activity_class_path is None:
            raise Http404
        self.activity_class = self.get_activity()
        self.activity_state = self.get_activity_state()
        return super(ActivityMixin, self).dispatch(request, *args, **kwargs)


class ActivityView(LoginRequiredMixin, ActivityMixin, View):

    def get(self, request, *args, **kwargs):
        if self.activity_state is None:  # Must mean you are just starting out
            return render("start_activity.html")
        activity = self.activity_class(self.activity_state.latest, self.activity_state)
        activity_play_signal.send(sender=ActivityView, slug=self.activity_slug, activity_occurrence_state=self.activity_state.latest, request=self.request)
        return activity.handle_get_request(self.request)

    def post(self, request, *args, **kwargs):
        if self.activity_state is None:  # @@@ does this depend on if we are starting, resuming or have already finished?
            self.create_activity_state()
        if self.activity_state.completed_count == 0:
            activity_start_signal.send(sender=ActivityView, slug=self.activity_slug, activity_state=self.activity_state, request=self.request)
            return redirect("activity", slug=self.activity_slug)
        activity = self.activity_class(self.activity_state.latest, self.activity_state)
        return activity.handle_post_request(self.request)


@login_required
def staff_dashboard(request):

    if not request.user.is_staff:
        raise Http404

    activities = []

    for slug, activity_class_path in hookset.all_activities():
        activity = load_path_attr(activity_class_path)
        activity_states = ActivityState.objects.filter(activity_slug=slug)
        completed_activity_states = activity_states.exclude(completed_count=0)
        activity_occurrence_states = ActivitySessionState.objects.filter(activity_slug=slug)
        completed_activity_occurrence_states = activity_occurrence_states.filter(completed__isnull=False)

        activities.append({
            "slug": slug,
            "title": activity.title,
            "activity_states": activity_states,
            "completed_activity_states": completed_activity_states,
            "activity_occurrence_states": activity_occurrence_states,
            "completed_activity_occurrence_states": completed_activity_occurrence_states,
        })
    return render(request, "staff_dashboard.html", {
        "users": User.objects.all(),
        "activity_states": ActivityState.objects.all(),
        "activity_occurrence_states": ActivitySessionState.objects.all(),
        "activities": activities,
    })


@login_required
def staff_activity_detail(request, slug):

    if not request.user.is_staff:
        raise Http404

    activity_states = ActivityState.objects.filter(activity_slug=slug)
    activity_occurrence_states = ActivitySessionState.objects.filter(activity_slug=slug)

    return render(request, "staff_activity_detail.html", {
        "activity_states": activity_states,
        "activity_occurrence_states": activity_occurrence_states,
    })
