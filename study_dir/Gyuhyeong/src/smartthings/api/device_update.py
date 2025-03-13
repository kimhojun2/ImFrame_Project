import requests

# 설정
device_id = 'your_device_id'
oauth_token = 'your_oauth_token'
url = f'https://api.smartthings.com/v1/devices/{device_id}/events'

headers = {
    'Authorization': f'Bearer {oauth_token}',
    'Content-Type': 'application/json'
}

data = {
    "deviceEvents": [
        {
            "component": "main",
            "capability": "switch",
            "attribute": "switch",
            "value": "on"
        }
    ]
}

# API 요청
response = requests.post(url, json=data, headers=headers)

# 응답 확인
if response.status_code == 200:
    print("이벤트 생성 성공")
else:
    print(f"에러 발생: {response.status_code} - {response.text}")
