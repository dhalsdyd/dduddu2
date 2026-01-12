#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows에서 웹캠 연결 문제를 진단하고 테스트하는 스크립트입니다.
"""

import os
import sys
import cv2 as cv

def test_webcam_connection():
    """웹캠 연결을 테스트합니다."""
    print("=== 웹캠 연결 테스트 ===")
    print(f"운영체제: {os.name}")
    print(f"OpenCV 버전: {cv.__version__}")
    print()
    
    # 사용 가능한 백엔드 확인
    backends = [
        (cv.CAP_ANY, "CAP_ANY"),
        (cv.CAP_DSHOW, "CAP_DSHOW (DirectShow)"),
        (cv.CAP_MSMF, "CAP_MSMF (Media Foundation)"),
        (cv.CAP_V4L2, "CAP_V4L2 (Linux)"),
        (cv.CAP_AVFOUNDATION, "CAP_AVFOUNDATION (macOS)")
    ]
    
    print("사용 가능한 백엔드:")
    for backend_id, backend_name in backends:
        print(f"  {backend_id}: {backend_name}")
    print()
    
    # Windows에서 권장 백엔드
    if os.name == 'nt':
        print("Windows 권장 백엔드 순서:")
        print("  1. CAP_DSHOW (DirectShow) - 가장 안정적")
        print("  2. CAP_MSMF (Media Foundation) - 최신 Windows")
        print("  3. CAP_ANY (자동 선택)")
        print()
    
    # 각 카메라 인덱스와 백엔드로 연결 시도
    max_camera_index = 5  # 0~4번까지 시도
    
    for camera_index in range(max_camera_index):
        print(f"카메라 인덱스 {camera_index} 테스트:")
        
        for backend_id, backend_name in backends:
            if os.name == 'nt' and backend_id in [cv.CAP_V4L2, cv.CAP_AVFOUNDATION]:
                # Windows에서는 Linux/macOS 전용 백엔드 건너뛰기
                continue
                
            try:
                print(f"  {backend_name} 시도...")
                cap = cv.VideoCapture(camera_index, backend_id)
                
                if cap and cap.isOpened():
                    # 카메라 정보 가져오기
                    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv.CAP_PROP_FPS)
                    
                    print(f"    ✅ 연결 성공!")
                    print(f"      해상도: {width}x{height}")
                    print(f"      FPS: {fps}")
                    
                    # 프레임 읽기 테스트
                    ret, frame = cap.read()
                    if ret:
                        print(f"      프레임 읽기: 성공 (크기: {frame.shape})")
                    else:
                        print(f"      프레임 읽기: 실패")
                    
                    cap.release()
                    break  # 이 카메라 인덱스는 성공했으므로 다음으로
                else:
                    print(f"    ❌ 연결 실패")
                    if cap:
                        cap.release()
                        
            except Exception as e:
                print(f"    ❌ 오류: {e}")
                if 'cap' in locals() and cap:
                    cap.release()
        
        print()
    
    print("=== 테스트 완료 ===")

def list_available_cameras():
    """사용 가능한 카메라를 나열합니다."""
    print("=== 사용 가능한 카메라 목록 ===")
    
    for i in range(10):  # 0~9번까지 확인
        cap = cv.VideoCapture(i)
        if cap.isOpened():
            # 카메라 정보 가져오기
            width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv.CAP_PROP_FPS)
            
            print(f"카메라 {i}: {width}x{height} @ {fps}fps")
            
            # 백엔드 정보 가져오기 (가능한 경우)
            try:
                backend = cap.get(cv.CAP_PROP_BACKEND)
                print(f"  백엔드: {backend}")
            except:
                pass
                
            cap.release()
        else:
            print(f"카메라 {i}: 연결 불가")
    
    print("=== 목록 완료 ===")

def interactive_camera_test():
    """대화형 카메라 테스트를 실행합니다."""
    print("=== 대화형 카메라 테스트 ===")
    print("종료하려면 'q'를 누르세요.")
    print()
    
    # 카메라 선택
    camera_index = input("카메라 인덱스를 입력하세요 (기본값: 0): ").strip()
    if not camera_index:
        camera_index = 0
    else:
        try:
            camera_index = int(camera_index)
        except ValueError:
            print("잘못된 입력입니다. 0을 사용합니다.")
            camera_index = 0
    
    # 백엔드 선택
    if os.name == 'nt':
        print("Windows 백엔드 선택:")
        print("1. DirectShow (권장)")
        print("2. Media Foundation")
        print("3. 자동 선택")
        backend_choice = input("백엔드를 선택하세요 (1-3, 기본값: 1): ").strip()
        
        if backend_choice == "2":
            backend = cv.CAP_MSMF
        elif backend_choice == "3":
            backend = cv.CAP_ANY
        else:
            backend = cv.CAP_DSHOW
    else:
        backend = cv.CAP_ANY
    
    print(f"카메라 {camera_index}, 백엔드 {backend}로 연결 시도...")
    
    cap = cv.VideoCapture(camera_index, backend)
    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return
    
    print("카메라 연결 성공! 영상이 표시됩니다.")
    print("종료: 'q' 키")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("프레임을 읽을 수 없습니다.")
                break
            
            # 화면에 표시
            cv.imshow('Camera Test', frame)
            
            # 키 입력 확인
            key = cv.waitKey(1) & 0xFF
            if key == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
    finally:
        cap.release()
        cv.destroyAllWindows()
        print("카메라 테스트 종료")

if __name__ == "__main__":
    print("웹캠 진단 도구")
    print("1. 웹캠 연결 테스트")
    print("2. 사용 가능한 카메라 목록")
    print("3. 대화형 카메라 테스트")
    print("4. 모든 테스트 실행")
    
    choice = input("\n선택하세요 (1-4, 기본값: 4): ").strip()
    
    if choice == "1":
        test_webcam_connection()
    elif choice == "2":
        list_available_cameras()
    elif choice == "3":
        interactive_camera_test()
    else:
        print("\n" + "="*50)
        test_webcam_connection()
        print("\n" + "="*50)
        list_available_cameras()
        print("\n" + "="*50)
        print("대화형 테스트를 원하면 다시 실행하고 3을 선택하세요.")

