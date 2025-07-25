from django.urls import path
from users.views import (
    SignUpAPIView,
    SendVerificationCodeAPIVIew,
    CheckVerificationCodeAPIView,
    LoginAPIView,
    LogoutAPIView,
    CustomTokenRefreshView,
)

urlpatterns = [
    path("send-code", SendVerificationCodeAPIVIew.as_view(), name="verification-email"),
    path("verify-code", CheckVerificationCodeAPIView.as_view(), name="verify-code"),
    path("sign-up", SignUpAPIView.as_view(), name="sign-up-user"),
    path("login", LoginAPIView.as_view(), name="login-user"),
    path("logout", LogoutAPIView.as_view(), name="logout-user"),
    path("reissue-token", CustomTokenRefreshView.as_view(), name="reissue-token"),
]
