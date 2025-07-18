from django.urls import path
from users.views import (
    SignUpAPIView,
    SendVerificationCodeAPIVIew,
    CheckVerificationCodeAPIView
)

urlpatterns = [
    path("send-code", SendVerificationCodeAPIVIew.as_view(), name="verification-email"),
    path("verify-code", CheckVerificationCodeAPIView.as_view(), name="verify-code"),
    path("sign-up", SignUpAPIView.as_view(), name="sign-up-user"),
]
