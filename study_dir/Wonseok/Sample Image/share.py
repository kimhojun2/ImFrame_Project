import requests

def add_folder(api_key, folder_id, folder_path, device_id, url='http://localhost:8384'):
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'id': folder_id,
        'path': folder_path,
        'type': 'sendreceive',
        'devices': [{'deviceID': device_id}],
        'rescanIntervalS': 10  # 폴더 재스캔 간격(초)
    }
    response = requests.post(url + '/rest/config/folders', json=data, headers=headers)
    if response.status_code == 200:
        print("Folder added successfully")
    else:
        print("Failed to add folder: ", response.text)

# API 키, 폴더 ID, 폴더 경로, 연결할 장치 ID 등을 입력하세요.
api_key = '3qyyFftYThmmEAZTuvjf5nCmVi2zik2D'
folder_id = 'newFolderID'
folder_path = '/path/to/new/folder'
device_id = 'deviceID_of_the_connected_device'

# 함수 호출
add_folder(api_key, folder_id, folder_path, device_id)
