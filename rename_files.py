#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows에서 한글 파일명으로 인한 문제를 방지하기 위해 
파일명을 영문으로 변경하는 스크립트입니다.
"""

import os
import shutil

def rename_files():
    """한글 파일명을 영문으로 변경합니다."""
    
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
        
        # game_state
        "쓸모센터로 가는 길.png": "way_to_ssulmo_center.png",
        "웃책.png": "smile_book.png",
        "웃뚜.png": "smile_dduddu.png",
        "쓸몬.png": "ssulmon.png",
        "광명x쓸모 (흰).png": "gwangmyeong_x_ssulmo_white.png",
        
        # result_state
        "dntxh.png": "dntxh.png",  # 이미 영문
        "dntEKd.png": "dntEKd.png",  # 이미 영문
        "대단해.png": "amazing.png",
        "우와~.png": "wow.png",
        "광명x쓸모.png": "gwangmyeong_x_ssulmo.png",  # 중복
    }
    
    # 각 이미지 폴더에 대해 파일명 변경
    image_folders = [
        "assets/images/title_state",
        "assets/images/game_state", 
        "assets/images/result_state"
    ]
    
    for folder in image_folders:
        if not os.path.exists(folder):
            print(f"폴더가 존재하지 않습니다: {folder}")
            continue
            
        print(f"\n{folder} 폴더 처리 중...")
        
        for filename in os.listdir(folder):
            if filename in file_mappings:
                old_path = os.path.join(folder, filename)
                new_filename = file_mappings[filename]
                new_path = os.path.join(folder, new_filename)
                
                try:
                    shutil.copy2(old_path, new_path)
                    print(f"  {filename} -> {new_filename} (복사됨)")
                except Exception as e:
                    print(f"  {filename} 복사 실패: {e}")
    
    print("\n파일명 변경 완료!")
    print("이제 코드에서 영문 파일명을 사용하도록 수정해야 합니다.")

if __name__ == "__main__":
    rename_files()
