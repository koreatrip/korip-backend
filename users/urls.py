from django.urls import path
from users.views.email_verification import (
    SendVerificationCodeAPIVIew, CheckVerificationCodeAPIView
)
from users.views.signup import SignUpAPIView
from users.views.auth.login import LoginAPIView
from users.views.auth.logout import LogoutAPIView
from users.views.auth.token import CustomTokenRefreshView
from users.views.account import ChangePasswordAPIView

urlpatterns = [
    path("send-code", SendVerificationCodeAPIVIew.as_view(), name="verification-email"),
    path("verify-code", CheckVerificationCodeAPIView.as_view(), name="verify-code"),
    path("sign-up", SignUpAPIView.as_view(), name="sign-up-user"),
    path("login", LoginAPIView.as_view(), name="login-user"),
    path("logout", LogoutAPIView.as_view(), name="logout-user"),
    path("reissue-token", CustomTokenRefreshView.as_view(), name="reissue-token"),
    path("change-pwd", ChangePasswordAPIView.as_view(), name="change-pwd"),
]
