from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import View

from django.contrib.auth.models import User

from account.decorators import login_required

from .hooks import hookset
from .proxies import ActivityState
from .models import ActivitySessionState
# from .signals import (
#     activity_start as activity_start_signal,
#     activity_play as activity_play_signal
# )
from .utils import load_path_attr


class ActivityMixin(object):

    def get_activity_state(self):
        return ActivityState(
            self.request,
            activity_key=self.activity_key,
            activity_class_path=self.activity_class_path,
        )

    def get_activity(self):
        activity_class = self.get_activity_class()
        return activity_class(
            self.activity_state,
            **self.get_activity_kwargs()
        )

    def get_extra_context(self, **kwargs):
        kwargs.update({
            "base_template": self.base_template_name,
            "activity_url": self.get_activity_url(),
        })
        return kwargs

    def get_activity_kwargs(self, **kwargs):
        kwargs.setdefault("parameters", {})
        kwargs.update({
            "extra_context": self.get_extra_context()
        })
        return kwargs

    def setup(self, *args, **kwargs):
        if not hasattr(self, "activity_key"):
            self.activity_key = kwargs.get("key")
        self.activity_class_path = hookset.activity_class_path(*args, **kwargs)
        if self.activity_class_path is None:
            raise Http404
        self.activity_state = self.get_activity_state()
        self.activity = self.get_activity()


class ActivityView(ActivityMixin, View):
    template_name = "pinax/lms/activities/activity.html"
    base_template_name = "pinax/lms/activities/base.html"

    def get_activity_class(self):
        return load_path_attr(self.activity_class_path)

    # @@@ this is overridden in module case but we'll need it for non-module case
    # @@@ when we get back to working on it
    def get_activity_url(self):
        return reverse("activity", kwargs=dict(activity_key=self.activity_key))

    # @@@ this is overridden in module case but we'll need it for non-module case
    # @@@ when we get back to working on it
    def get_session_url(self):
        pass  # to implement

    def dispatch(self, request, *args, **kwargs):
        self.setup(*args, **kwargs)
        return super(ActivityView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.activity.singleton:
            return self.post(request, *args, **kwargs)
        else:
            ctx = {"activity": self.activity}
            ctx.update(self.get_extra_context())
            return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        if self.activity_state.progression == "completed":
            return redirect(self.get_activity_url())
        else:
            self.activity_state.ensure_exists()
            session = self.activity_state.latest
            return redirect(self.get_session_url(session))


class ActivitySessionView(ActivityMixin, View):

    base_template_name = "pinax/lms/activities/base.html"

    def dispatch(self, request, *args, **kwargs):
        self.session = get_object_or_404(ActivitySessionState, activity_state__user=request.user, pk=kwargs["session_pk"])
        self.setup(*args, **kwargs)
        return super(ActivitySessionView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.activity.handle_get_request(request, self.session, self.get_session_url(self.session))

    def post(self, request, *args, **kwargs):
        return self.activity.handle_post_request(request, self.session, self.get_session_url(self.session))


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
