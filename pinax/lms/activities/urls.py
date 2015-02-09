from django.conf.urls import patterns, url


urlpatterns = patterns(
    "pinax.lms.activities.views",
    url(r"(?P<slug>[\w\-]+)/start/$", "activity_start", name="activity_start"),
    url(r"(?P<slug>[\w\-]+)/play/$", "activity_play", name="activity_play"),
    url(r"(?P<slug>[\w\-]+)/completed/$", "activity_completed", name="activity_completed"),

    url(r"^staff/$", "staff_dashboard", name="staff_dashboard"),
    url(r"^staff/activity/([^/]+)/$", "staff_activity_detail", name="staff_activity_detail"),
)
