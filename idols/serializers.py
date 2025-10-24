from rest_framework import serializers
from idols.models import IdolRequest


class IdolRequestSerializer(serializers.ModelSerializer):
    # user는 자동으로 현재 로그인한 유저로 설정될 거라서 읽기 전용
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = IdolRequest
        fields = [
            "id",
            "user",
            "idol_name",
            "agency",
            "related_info",
            "additional_notes",
            "created_at"
        ]
        read_only_fields = ["id", "user", "created_at"]

    # user 필드를 이메일로 보여주기
    def get_user(self, obj):
        return obj.user.email if obj.user else None
