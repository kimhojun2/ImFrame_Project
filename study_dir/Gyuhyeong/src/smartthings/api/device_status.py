import requests

# OAuth 토큰과 장치 ID 설정
oauth_token = '8cd2da5e-e34e-4fe5-b38d-7b48301f03fb'
device_id = '33ea54b4-cbda-44c0-a820-094008acd8e3'

# API 엔드포인트 URL
url = f'https://api.smartthings.com/v1/devices/{device_id}/status'

# HTTP 헤더 설정
headers = {
    'Authorization': f'Bearer {oauth_token}',
    'Content-Type': 'application/json'
}

# API 호출
response = requests.get(url, headers=headers)

# 응답 출력
if response.status_code == 200:
    # 성공적으로 장치 상태 정보를 받았을 때
    device_status = response.json()
    print("장치 상태:", device_status)
else:
    # 요청이 실패했을 때 오류 메시지 출력
    print("API 호출 실패:", response.status_code, response.text)
