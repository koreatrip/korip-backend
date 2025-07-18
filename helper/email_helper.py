from django.core.mail import send_mail
from django.conf import settings
from helper.redis_helper import RedisHelper

import secrets
import logging

logger = logging.getLogger(__name__)
redis_helper = RedisHelper()

class EmailHelper:

    @staticmethod
    def generate_verification_code():
        """이메일 인증 코드 생성"""
        return secrets.randbelow(900000) + 100000


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
            redis_helper.set_with_expiry(f"email_verified:{email}", "True", 6000)
            redis_helper.delete_key(f"email_verification:{email}")
            return True
        return False
    
    @staticmethod
    def check_verification_email(email):
        """이메일 인증 여부 확인"""
        if redis_helper.get_value(f"email_verified:{email}") == "True":
           return True
        return False 
