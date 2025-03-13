import subprocess

def create_shared_folder(path, share_name, description="Shared Folder via Python"):
    try:
        # 폴더 공유 설정을 위한 PowerShell 명령어 구성
        cmd = [
            'powershell',
            'New-SmbShare',
            '-Name', share_name,
            '-Path', path,
            '-FullAccess', 'Everyone',
            '-Description', f'"{description}"'  # 공백이 포함된 문자열을 쌍따옴표로 감싸기
        ]
        
        # PowerShell 명령어 실행
        subprocess.run(cmd, check=True)
        print(f"Folder {path} shared as {share_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error sharing folder: {e}")

# 폴더 공유 실행
create_shared_folder(r"C:\Users\SSAFY\Desktop\share", "NewShare")
