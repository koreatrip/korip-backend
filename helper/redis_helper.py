from django_redis import get_redis_connection
import json

class RedisHelper:
    def __init__(self):
        self.redis_client = get_redis_connection("default")
    
    def set_with_expiry(self, key, value, seconds=300):
        """값 저장 및 유효기간 설정"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.redis_client.setex(key, seconds, value)
    
    def get_value(self, key):
        """값 조회"""
        value = self.redis_client.get(key)
        if value:
            # bytes인 경우 디코딩
            if isinstance(value, bytes):
                value = value.decode('utf-8')
            # JSON 형태인지 확인하고 파싱 시도
            try:
                return json.loads(value)
            except:
                return value
        return None
    
    def delete_key(self, key):
        """키 삭제"""
        return self.redis_client.delete(key)
    
    def exists(self, key):
        """키 존재 확인"""
        return bool(self.redis_client.exists(key))