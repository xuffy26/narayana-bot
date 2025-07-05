from django.urls import path
from .views import CheckPatientChat

urlpatterns = [
    path('chat-conversation', CheckPatientChat.as_view()),
]
