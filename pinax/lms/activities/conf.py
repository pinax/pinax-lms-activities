from django.conf import settings  # noqa

from appconf import AppConf


class PinaxLmsActivitiesAppConf(AppConf):

    ACTIVITIES = {}

    class Meta:
        prefix = "pinax_lms_activities"
