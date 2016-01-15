from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"(?P<slug>[\w\-]+)/start/$", views.activity_start, name="activity_start"),
    url(r"(?P<slug>[\w\-]+)/play/$", views.activity_play, name="activity_play"),
    url(r"(?P<slug>[\w\-]+)/completed/$", views.activity_completed, name="activity_completed"),

    url(r"^staff/$", views.staff_dashboard, name="staff_dashboard"),
    url(r"^staff/activity/([^/]+)/$", views.staff_activity_detail, name="staff_activity_detail"),
]
