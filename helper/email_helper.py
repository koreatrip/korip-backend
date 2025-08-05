from django.core.mail import send_mail
from django.conf import settings
from helper.redis_helper import RedisHelper

import secrets
import string
import logging

logger = logging.getLogger(__name__)
redis_helper = RedisHelper()

class EmailHelper:

    @staticmethod
    def generate_verification_code():
        """이메일 인증 코드 생성"""
        return secrets.randbelow(900000) + 100000
        
    @staticmethod
    def generate_temporary_password(length=20):
        """특수문자, 대소문자, 숫자를 반드시 포함하는 임시 비밀번호 생성"""
        if length < 4:
            raise ValueError("비밀번호 길이는 최소 4자 이상이어야 합니다.")
        
        # 반드시 포함시킬 문자들
        required = [
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.digits),
            secrets.choice(string.punctuation),
        ]

        # 나머지 랜덤 문자 채우기
        remaining = [
            secrets.choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(length - 4)
        ]

        # 전체 섞기
        password_list = required + remaining
        secrets.SystemRandom().shuffle(password_list)
        return ''.join(password_list)

    @staticmethod
    def send_temporary_password(email):
        """임시 비밀번호 이메일 전송"""

        subject = "Korip 임시 비밀번호 안내"
        temp_password = EmailHelper.generate_temporary_password()

        # 텍스트 메시지
        message = f"""안녕하세요!\n\n요청하신 임시 비밀번호는 아래와 같습니다.\n\n임시 비밀번호: {temp_password}\n\n로그인 후 반드시 비밀번호를 변경해 주세요.\n\n감사합니다."""

        # HTML 메시지
        html_message = f"""<html><body>
                        <h2>🔐 Korip 임시 비밀번호 안내</h2>
                        <p>안녕하세요!</p>
                        <p>요청하신 임시 비밀번호는 아래와 같습니다.</p>
                        <h3 style="color: #dc3545;">임시 비밀번호: {temp_password}</h3>
                        <p>로그인 후 반드시 비밀번호를 변경해 주세요.</p>
                        <p>감사합니다.</p>
                        </body></html>"""

        try:
            logger.info(f"임시 비밀번호 이메일 발송 시도: {email}")
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"임시 비밀번호 이메일 발송 성공: {email}")
            return temp_password
        except Exception as e:
            logger.error(f"임시 비밀번호 이메일 발송 실패 - 이메일: {email}, 에러: {e}")
            return None

    @staticmethod
    def send_verification_email(email):
        """이메일 인증 코드 발송"""
        
        subject = "Korip 회원가입 이메일 인증 코드"
        verification_code = EmailHelper.generate_verification_code()
        
        # 간단한 텍스트 메시지
        message = f"안녕하세요!\n\n이메일 인증을 위한 인증 코드입니다.\n\n인증 코드: {verification_code}\n\n이 코드는 1분 후 만료됩니다.\n\n감사합니다."
        
        # HTML 메시지
        html_message = f"""<html><body>
                        <h2>✈️ Korip 회원가입 이메일 인증</h2>
                        <p>안녕하세요!!</p>
                        <p>회원가입을 위한 인증 코드입니다.</p>
                        <h3 style="color: #007bff;">인증 코드: {verification_code}</h3>
                        <p>이 코드는 1분 후 만료됩니다.</p>
                        <p>감사합니다. </p>
                        </body></html>"""

        try:
            logger.info(f"이메일 발송 시도: {email}")
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"이메일 발송 성공: {email}")
            return verification_code
        except Exception as e:
            logger.error(f"이메일 발송 실패 - 이메일: {email}, 에러: {e}")
            return None

    @staticmethod
    def check_verification_code(email, code):
        """이메일 인증 코드 확인"""
        verification_code = redis_helper.get_value(f"email_verification:{email}")

        if verification_code is None:
            return False
        
        if verification_code == int(code):
            redis_helper.set_with_expiry(f"email_verified:{email}", "True", 600)
            redis_helper.delete_key(f"email_verification:{email}")
            return True
        return False
    
    @staticmethod
    def check_verification_email(email):
        """이메일 인증 여부 확인"""
        if redis_helper.get_value(f"email_verified:{email}") == "True":
           return True
        return False 
