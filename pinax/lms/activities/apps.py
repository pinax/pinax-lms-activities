from django.apps import AppConfig as BaseAppConfig
from django.utils.translation import ugettext_lazy as _


class AppConfig(BaseAppConfig):

    name = "pinax.lms.activities"
    label = "pinax_lms_actitivies"
    verbose_name = _("Pinax LMS Activities")
