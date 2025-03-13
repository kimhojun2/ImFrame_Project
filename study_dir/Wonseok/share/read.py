import smbclient

# SMB 서버에 로그인하기 위한 계정 정보
username = 'ssafy'
password = ''

# 설정 정보를 smbclient 라이브러리에 전달
smbclient.ClientConfig(username=username, password=password)

# SMB 서버 및 공유 폴더 경로 설정
server_ip = 'SERVER_IP'  # SMB 서버의 IP 주소
share_name = 'SharedFolder'  # 공유 폴더 이름
share_path = fr"\\{server_ip}\{share_name}"  # 공유 폴더의 전체 경로

# 공유 폴더 내 파일 목록 확인
try:
    files = smbclient.listdir(share_path)
    print("Files in share:")
    for file in files:
        print(file)
except smbclient.SambaClientError as e:
    print(f"Error accessing share: {e}")
