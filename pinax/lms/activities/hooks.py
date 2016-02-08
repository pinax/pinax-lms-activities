from django.contrib import messages


class ActivitiesDefaultHookSet(object):

    def activity_class_path(self, *args, **kwargs):
        from .conf import settings
        return settings.PINAX_LMS_ACTIVITIES_ACTIVITIES.get(kwargs.get("slug"))

    def all_activities(self):
        from .conf import settings
        return settings.PINAX_LMS_ACTIVITIES_ACTIVITIES.items()

    def success_message(self, request, activity):
        if activity.repeatable:
            messages.success(request, "{} activity completed. You may repeat it again at any time.".format(activity.title))
        else:
            messages.success(request, "{} activity completed.".format(activity.title))

    def already_completed_message(self, request, activity):
        messages.info(request, "{} activity already completed.".format(activity.title))


class HookProxy(object):

    def __getattr__(self, attr):
        from .conf import settings
        return getattr(settings.PINAX_LMS_ACTIVITIES_HOOKSET, attr)


hookset = HookProxy()
