import socket

def client():
    # 소켓 생성
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 서버 호스트와 포트
    host = '70.12.246.136'  # localhost
    port = 12345

    # 서버에 연결
    client_socket.connect((host, port))
    print("서버에 연결되었습니다.")

    while True:
        # 클라이언트로부터 메시지 받기
        message = input()
        client_socket.send(message.encode())

        # 서버로부터 응답 받기
        response = client_socket.recv(1024).decode()
        print( response)

    # 연결 종료
    client_socket.close()

if __name__ == "__main__":
    client()