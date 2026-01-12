#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstaller를 사용하여 게임을 실행 파일(.exe)로 빌드합니다.
"""

import os
import sys
import subprocess
import shutil

# Windows 환경에서 UTF-8 출력 지원
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def build_exe():
    """게임을 EXE 파일로 빌드합니다."""
    
    print("="*60)
    print("🎮 뚜뚜의 어드벤처 - EXE 빌드 시작")
    print("="*60)
    
    # 1. PyInstaller 설치 확인
    try:
        import PyInstaller
        print("✅ PyInstaller가 설치되어 있습니다.")
    except ImportError:
        print("⚠️  PyInstaller가 설치되어 있지 않습니다.")
        print("📦 PyInstaller를 설치합니다...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller 설치 완료!")
    
    # 2. 빌드 옵션 설정
    app_name = "뚜뚜의어드벤처"
    main_script = "main.py"
    icon_file = "assets/images/title_state/tomato_character.png"  # 아이콘으로 사용할 이미지
    
    # 3. PyInstaller 명령어 구성
    pyinstaller_args = [
        "pyinstaller",
        "--name", app_name,
        "--onefile",  # 단일 실행 파일
        "--windowed",  # 콘솔 창 숨기기
        "--add-data", f"assets{os.pathsep}assets",  # assets 폴더 포함
        "--add-data", f"leaderboard.json{os.pathsep}.",  # leaderboard.json 포함
        "--hidden-import", "pygame",
        "--hidden-import", "cv2",
        "--hidden-import", "serial",
        "--collect-all", "pygame",
        "--collect-all", "cv2",
    ]
    
    # 아이콘 파일이 있으면 추가
    if os.path.exists(icon_file):
        pyinstaller_args.extend(["--icon", icon_file])
    
    pyinstaller_args.append(main_script)
    
    # 4. 빌드 실행
    print("\n📦 빌드를 시작합니다...")
    print(f"명령어: {' '.join(pyinstaller_args)}")
    print()
    
    try:
        subprocess.check_call(pyinstaller_args)
        print("\n✅ 빌드 성공!")
        
        # 5. 결과 파일 위치 알려주기
        exe_name = f"{app_name}.exe" if sys.platform.startswith('win') else app_name
        dist_path = os.path.join("dist", exe_name)
        
        if os.path.exists(dist_path):
            print(f"\n🎉 실행 파일이 생성되었습니다:")
            print(f"   📁 {os.path.abspath(dist_path)}")
            print(f"\n파일 크기: {os.path.getsize(dist_path) / (1024*1024):.1f} MB")
        else:
            print(f"\n⚠️  실행 파일을 찾을 수 없습니다: {dist_path}")
        
        # 6. 배포 폴더 생성
        deploy_folder = "배포용"
        if not os.path.exists(deploy_folder):
            os.makedirs(deploy_folder)
        
        # 필요한 파일들 복사
        if os.path.exists(dist_path):
            shutil.copy(dist_path, deploy_folder)
            print(f"\n📦 배포 폴더에 복사 완료: {deploy_folder}/")
        
        # README 생성
        readme_path = os.path.join(deploy_folder, "README.txt")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("뚜뚜의 어드벤처\n")
            f.write("="*40 + "\n\n")
            f.write("실행 방법:\n")
            f.write(f"1. {exe_name} 파일을 더블클릭하여 실행\n")
            f.write("2. 게임을 즐기세요!\n\n")
            f.write("필요 사항:\n")
            f.write("- Arduino + 초음파 센서 (선택사항)\n")
            f.write("- 웹캠 (선택사항)\n\n")
            f.write("문제 해결:\n")
            f.write("- Windows Defender가 차단하는 경우 '추가 정보' > '실행'을 클릭\n")
            f.write("- 센서 연결은 게임 실행 후에도 가능합니다\n")
        
        print(f"📝 README 파일 생성: {readme_path}")
        
        print("\n"+"="*60)
        print("🎉 빌드 완료!")
        print("="*60)
        print(f"\n배포 파일: {deploy_folder}/ 폴더를 확인하세요")
        print("이 폴더를 압축하여 배포할 수 있습니다.\n")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 빌드 실패: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return False
    
    return True

def clean_build_files():
    """빌드 과정에서 생성된 임시 파일들을 정리합니다."""
    print("\n🧹 빌드 파일 정리 중...")
    
    folders_to_remove = ["build", "__pycache__"]
    files_to_remove = ["*.spec"]
    
    for folder in folders_to_remove:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  삭제: {folder}/")
    
    import glob
    for pattern in files_to_remove:
        for file in glob.glob(pattern):
            os.remove(file)
            print(f"  삭제: {file}")
    
    print("✅ 정리 완료!")

if __name__ == "__main__":
    success = build_exe()
    
    if success:
        # 정리 여부 확인
        response = input("\n빌드 파일을 정리하시겠습니까? (y/n): ").strip().lower()
        if response == 'y':
            clean_build_files()
        
        print("\n✨ 모든 작업이 완료되었습니다!")
    else:
        print("\n❌ 빌드에 실패했습니다. 오류를 확인하세요.")
