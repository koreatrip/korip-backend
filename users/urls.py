from django.urls import path
from users.views.email_verification import (
    SendVerificationCodeAPIView, CheckVerificationCodeAPIView
)
from users.views.signup import SignUpAPIView
from users.views.auth.login import LoginAPIView
from users.views.auth.logout import LogoutAPIView
from users.views.auth.social_login import SocialLoginAPIView
from users.views.auth.token import CustomTokenRefreshView
from users.views.account import (
    ChangePasswordAPIView,
    FindAccountAPIView,
    FindPasswordAPIView,
    UserInfoAPIView
)
from users.views.create_preferences import CreatePreferenceAPIView


urlpatterns = [
    path("send-code", SendVerificationCodeAPIView.as_view(), name="verification-email"),
    path("verify-code", CheckVerificationCodeAPIView.as_view(), name="verify-code"),
    path("sign-up", SignUpAPIView.as_view(), name="sign-up-user"),
    path("login", LoginAPIView.as_view(), name="login-user"),
    path("social-login", SocialLoginAPIView.as_view(), name="social-login-user"),
    path("logout", LogoutAPIView.as_view(), name="logout-user"),
    path("reissue-token", CustomTokenRefreshView.as_view(), name="reissue-token"),
    path("change-pwd", ChangePasswordAPIView.as_view(), name="change-pwd"),
    path("find-account", FindAccountAPIView.as_view(), name="find-account"),
    path("find-pwd", FindPasswordAPIView.as_view(), name="find-pwd"),
    path("<int:user_id>/preferences", CreatePreferenceAPIView.as_view(), name="create-preferences"),
    path("info", UserInfoAPIView.as_view(), name="user-info"),
]
