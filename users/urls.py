from django.urls import path
from users.views import (
    SignUpAPIView,
    SendVerificationCodeAPIVIew
)

urlpatterns = [
    path("send-code", SendVerificationCodeAPIVIew.as_view(), name="verification-email"),
    path("sign-up", SignUpAPIView.as_view(), name="sign-up-user"),
]
