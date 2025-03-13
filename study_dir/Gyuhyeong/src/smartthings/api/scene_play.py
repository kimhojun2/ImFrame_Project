import requests

# 설정
scene_id = 'ec22f091-90b4-4f91-8e23-a2783326bad3'  # 실행하려는 장면의 ID
oauth_token = '8cd2da5e-e34e-4fe5-b38d-7b48301f03fb'  # OAuth 토큰
url = f'https://api.smartthings.com/scenes/{scene_id}/execute'  # API 엔드포인트

# HTTP 헤더 설정
headers = {
    'Authorization': f'Bearer {oauth_token}',
    'Content-Type': 'application/json'
}


# API 요청
response = requests.post(url, headers=headers)

# 응답 확인
if response.status_code == 200:
    print("장면 실행 성공")
    print(response.json())  # 성공 시 응답 내용 출력
else:
    print("장면 실행 실패:", response.status_code, response.text)  # 실패 시 오류 메시지 출력
