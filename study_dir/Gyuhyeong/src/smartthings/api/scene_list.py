import requests

# 설정
oauth_token = '8cd2da5e-e34e-4fe5-b38d-7b48301f03fb'  # OAuth 토큰 입력
url = 'https://api.smartthings.com/scenes'  # API 엔드포인트

# HTTP 헤더 설정
headers = {
    'Authorization': f'Bearer {oauth_token}',
    'Content-Type': 'application/vnd.smartthings+json'
}

# API 요청
response = requests.get(url, headers=headers)

# 응답 확인
if response.status_code == 200:
    scenes = response.json()
    print("장면 목록:", scenes)
else:
    print("API 호출 실패:", response.status_code, response.text)
