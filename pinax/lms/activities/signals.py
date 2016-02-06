import django.dispatch


activity_start = django.dispatch.Signal(providing_args=["activity_key", "activity_state", "request"])
activity_play = django.dispatch.Signal(providing_args=["activity_key", "activity_session_state", "request"])
activity_completed = django.dispatch.Signal(providing_args=["activity_key", "activity_session_state", "request"])
