# exports/services/google_calendar.py
# 구글 캘린더 API 연동 서비스

import os
from datetime import datetime, timezone
from typing import List, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from django.conf import settings


class GoogleCalendarService:
    """구글 캘린더 API 연동 서비스 클래스"""

    def __init__(self):
        self.client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
        self.client_secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_OAUTH2_REDIRECT_URI
        self.scopes = settings.GOOGLE_CALENDAR_SCOPES

    def get_authorization_url(self, user_id: int) -> str:
        """OAuth 인증 URL 생성"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                }
            },
            scopes=self.scopes
        )
        flow.redirect_uri = self.redirect_uri

        # 사용자 ID를 state에 포함시켜서 콜백에서 식별할 수 있도록 함
        authorization_url, state = flow.authorization_url(
            access_type="offline",  # 리프레시 토큰 받기 위해
            include_granted_scopes="true",
            state=str(user_id)  # 사용자 ID 저장
        )

        return authorization_url

    def handle_callback(self, authorization_code: str, state: str) -> Dict[str, Any]:
        """OAuth 콜백 처리 및 토큰 받기"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                }
            },
            scopes=self.scopes
        )
        flow.redirect_uri = self.redirect_uri

        # 토큰 받기
        flow.fetch_token(code=authorization_code)

        credentials = flow.credentials

        # 사용자 정보 가져오기
        service = build("oauth2", "v2", credentials=credentials)
        user_info = service.userinfo().get().execute()

        return {
            "user_id": int(state),  # 콜백에서 받은 사용자 ID
            "google_email": user_info.get("email"),
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_expires_at": credentials.expiry.isoformat() if credentials.expiry else None
        }

    def create_calendar_events(self, access_token: str, travel_plan_data: Dict[str, Any]) -> List[str]:
        """여행 계획을 구글 캘린더 이벤트로 생성"""
        credentials = Credentials(token=access_token)

        try:
            # Calendar API 서비스 생성
            service = build("calendar", "v3", credentials=credentials)

            # 생성된 이벤트 ID들을 저장
            event_ids = []

            # 여행 계획 제목과 설명
            plan_title = travel_plan_data.get("title", "여행 계획")
            plan_description = travel_plan_data.get("description", "")

            # 일정별로 이벤트 생성
            for day_schedule in travel_plan_data.get("schedule", []):
                date = day_schedule.get("date")  # "2025-09-06" 형식
                day_number = day_schedule.get("day")

                # 해당 날짜의 관광지들
                places = day_schedule.get("places", [])

                for place in places:
                    place_name = place.get("place_name")
                    time = place.get("time")  # "09:00" 형식
                    category = place.get("category", "")

                    # 빈 장소는 건너뛰기
                    if not place_name or not time:
                        continue

                    # 이벤트 시작/종료 시간 계산 (2시간씩 할당)
                    start_datetime = f"{date}T{time}:00"

                    # 시간을 파싱해서 2시간 후 계산
                    hour = int(time.split(":")[0])
                    end_hour = hour + 2
                    if end_hour >= 24:
                        end_hour = 23
                        end_minute = 59
                    else:
                        end_minute = 0

                    end_datetime = f"{date}T{end_hour:02d}:{end_minute:02d}:00"

                    # 이벤트 데이터 구성
                    event = {
                        "summary": f"[{plan_title}] {place_name}",  # 이벤트 제목
                        "description": f"여행 {day_number}일차\n카테고리: {category}\n\n{plan_description}",
                        "start": {
                            "dateTime": start_datetime,
                            "timeZone": "Asia/Seoul",
                        },
                        "end": {
                            "dateTime": end_datetime,
                            "timeZone": "Asia/Seoul",
                        },
                        "location": place_name,
                    }

                    # 구글 캘린더에 이벤트 생성
                    created_event = service.events().insert(
                        calendarId="primary",
                        body=event
                    ).execute()

                    event_ids.append(created_event.get("id"))

            return event_ids

        except HttpError as error:
            print(f"Google Calendar API 에러: {error}")
            raise Exception(f"캘린더 이벤트 생성 실패: {error}")

    def refresh_access_token(self, refresh_token: str) -> str:
        """리프레시 토큰으로 새 액세스 토큰 받기"""
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret
        )

        # 토큰 갱신
        credentials.refresh(Request())
        return credentials.token
