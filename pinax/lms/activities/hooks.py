from .conf import settings


class ActivitiesDefaultHookSet(object):

    def activity_class_path(self, slug):
        return settings.PINAX_LMS_ACTIVITIES_ACTIVITIES.get(slug)

    def all_activities(self):
        return settings.PINAX_LMS_ACTIVITIES_ACTIVITIES.items()


class HookProxy(object):

    def __getattr__(self, attr):
        return getattr(settings.PINAX_LMS_ACTIVITIES_HOOKSET, attr)


hookset = HookProxy()
