# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def forwards(apps, schema_editor):
    if not schema_editor.connection.alias == "default":
        return
    ActivityState = apps.get_model("pinax_lms_activities", "ActivityState")
    ActivitySessionState = apps.get_model("pinax_lms_activities", "ActivitySessionState")
    for activity_session_state in ActivitySessionState.objects.all():
        activity_state = ActivityState.objects.get(
            user=activity_session_state.user,
            activity_key=activity_session_state.activity_key,
        )
        activity_session_state.activity_state = activity_state
        activity_session_state.save()


class Migration(migrations.Migration):

    dependencies = [
        ("pinax_lms_activities", "0006_auto_20160206_2029"),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
