# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("pinax_lms_activities", "0007_migrate"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="activitysessionstate",
            unique_together=set([("activity_state", "started")]),
        ),
        migrations.RemoveField(
            model_name="activitysessionstate",
            name="activity_key",
        ),
        migrations.RemoveField(
            model_name="activitysessionstate",
            name="user",
        ),
        migrations.AlterField(
            model_name="activitysessionstate",
            name="activity_state",
            field=models.ForeignKey(null=False, on_delete=django.db.models.deletion.CASCADE, related_name="sessions", to="pinax_lms_activities.ActivityState"),
        ),
    ]
