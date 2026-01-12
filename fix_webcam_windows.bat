@echo off
chcp 65001 >nul
echo Windows 웹캠 문제 해결 도구
echo ================================
echo.

echo 1. 웹캠 진단 실행...
python webcam_test.py

echo.
echo 2. 웹캠 문제 해결 방법:
echo.
echo [권한 문제]
echo - Windows 설정 > 개인정보 > 카메라
echo - "앱이 카메라에 액세스할 수 있도록 허용" 활성화
echo.
echo [다른 프로그램 사용 중]
echo - Zoom, Teams, Discord 등 종료
echo - Windows 카메라 앱 종료
echo.
echo [드라이버 문제]
echo - 장치 관리자 > 이미징 장치
echo - 웹캠 우클릭 > 드라이버 업데이트
echo.
echo [하드웨어 문제]
echo - USB 포트 변경
echo - 웹캠 재연결
echo.

echo 3. 게임에서 카메라 인덱스 변경 시도...
echo main.py에서 cam_index=1로 변경해보세요
echo.

echo 4. 관리자 권한으로 실행 시도...
echo 명령 프롬프트를 관리자 권한으로 실행하고
echo 다시 이 배치 파일을 실행해보세요
echo.

pause

