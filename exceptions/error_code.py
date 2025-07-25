from enum import Enum

class ErrorCode(Enum):
    # 회원
    EMAIL_ALREADY_REGISTERED = ("EMAIL_ALREADY_REGISTERED", "이미 사용 중인 이메일입니다")
    EMAIL_NOT_CERTIFIED = ("EMAIL_NOT_CERTIFIED", "이메일 인증이 필요합니다")
    EMAIL_SEND_FAILED = ("EMAIL_SEND_FAILED", "이메일 발송을 실패했습니다.")
    EMAIL_CERTIFICATION_FAIL = ("EMAIL_CERTIFICATION_FAIL", "이메일 또는 인증번호가 일치하지 않거나 유효기간이 만료되었습니다.")
    SAME_CURRENT_PASSWORD = ("SAME_CURRENT_PASSWORD", "현재 비밀번호와 새로 변경할 비밀번호가 일치합니다.")
    MISSMATCHED_PASSWORD = ("MISSMATCHED_PASSWORD", "비밀번호가 일치하지 않습니다.")
    INVALID_USER_INFO = ("INVALID_USER_INFO", "이메일 또는 비밀번호가 올바르지 않습니다")
    INVALID_PASSWORD = ("INVALID_PASSWORD", "비밀번호 조건을 만족하지 않습니다.")
    INVALID_REFRESH_TOKEN = ("INVALID_REFRESH_TOKEN", "유효하지 않은 리프레시 토큰입니다.")
    LOGOUT_FAIL = ("LOGOUT_FAIL", "로그아웃 처리 중 오류가 발생했습니다.")
    USER_NOT_FOUND = ("USER_NOT_FOUND", "사용자를 찾을 수 없습니다")
    ACCOUNT_INACTIVE = ("ACCOUNT_INACTIVE", "비활성화된 계정입니다.")
    MISSING_CREDENTIALS = ("MISSING_CREDENTIALS", "이메일과 비밀번호를 모두 입력해주세요.")
    
    def __init__(self, code, message):
        self.code = code
        self.message = message