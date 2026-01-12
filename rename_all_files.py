#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 한글 파일명을 영어로 변경하는 스크립트입니다.
Windows에서의 호환성을 위해 필수입니다.
"""

import os
import shutil

def rename_all_files():
    """모든 한글 파일명을 영어로 변경합니다."""
    
    # 파일명 매핑 (한글 -> 영문)
    file_mappings = {
        # title_state
        "뚜뚜의 어드벤처.png": "title_adventure.png",
        "1위.png": "rank_1.png",
        "2위.png": "rank_2.png", 
        "3위.png": "rank_3.png",
        "4위.png": "rank_4.png",
        "5위.png": "rank_5.png",
        "carrot_character.png": "carrot_character.png",  # 이미 영문
        "tomato_character.png": "tomato_character.png",  # 이미 영문
        "board_background.png": "board_background.png",  # 이미 영문
        "광명x쓸모.png": "gwangmyeong_x_ssulmo.png",
        "누구 보드가.png": "who_board.png",
        "뚜뚜 보드.png": "dduddu_board.png",
        "image.png": "image.png",  # 이미 영문
        "background.jpg": "background.jpg",  # 이미 영문
        
        # game_state
        "쓸모센터로 가는 길.png": "way_to_ssulmo_center.png",
        "웃책.png": "smile_book.png",
        "웃뚜.png": "smile_dduddu.png",
        "쓸몬.png": "ssulmon.png",
        "광명x쓸모 (흰).png": "gwangmyeong_x_ssulmo_white.png",
        "background.jpg": "background.jpg",  # 이미 영문
        "background_rail.png": "background_rail.png",  # 이미 영문
        
        # result_state
        "dntxh.png": "dntxh.png",  # 이미 영문
        "dntEKd.png": "dntEKd.png",  # 이미 영문
        "대단해.png": "amazing.png",
        "우와~.png": "wow.png",
        "뚜뚜 보드.png": "dduddu_board.png",  # 중복
        "뚜뚜의 어드벤처.png": "title_adventure.png",  # 중복
        "쓸몬.png": "ssulmon.png",  # 중복
        "웃책.png": "smile_book.png",  # 중복
        "background.jpg": "background.jpg",  # 이미 영문
        "board_background.png": "board_background.png",  # 이미 영문
    }
    
    # 각 이미지 폴더에 대해 파일명 변경
    image_folders = [
        "assets/images/title_state",
        "assets/images/game_state", 
        "assets/images/result_state"
    ]
    
    total_renamed = 0
    total_errors = 0
    
    for folder in image_folders:
        if not os.path.exists(folder):
            print(f"⚠️  폴더가 존재하지 않습니다: {folder}")
            continue
            
        print(f"\n📁 {folder} 폴더 처리 중...")
        
        for filename in os.listdir(folder):
            if filename in file_mappings:
                old_path = os.path.join(folder, filename)
                new_filename = file_mappings[filename]
                new_path = os.path.join(folder, new_filename)
                
                try:
                    # 파일이 이미 존재하는지 확인
                    if os.path.exists(new_path):
                        print(f"  ⚠️  {filename} -> {new_filename} (이미 존재함, 건너뜀)")
                        continue
                    
                    # 파일명 변경
                    os.rename(old_path, new_path)
                    print(f"  ✅ {filename} -> {new_filename}")
                    total_renamed += 1
                    
                except Exception as e:
                    print(f"  ❌ {filename} 변경 실패: {e}")
                    total_errors += 1
    
    print(f"\n🎉 파일명 변경 완료!")
    print(f"✅ 성공: {total_renamed}개")
    if total_errors > 0:
        print(f"❌ 실패: {total_errors}개")
    
    print("\n이제 코드에서 영문 파일명을 사용하도록 수정해야 합니다.")
    print("코드 수정이 완료되면 게임을 실행할 수 있습니다.")

if __name__ == "__main__":
    rename_all_files()
