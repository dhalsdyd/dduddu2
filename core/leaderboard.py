# core/leaderboard.py
import json, os, time
from typing import List, Dict, Optional
from config import DATA_FILE, SESSION_FILE

def ensure_sample_data():
    if os.path.exists(DATA_FILE):
        return
    sample = [
        {"name":"네오","best_fast_ms":520,"best_close_cm":0.0,"best_score":1800},
        {"name":"레이","best_fast_ms":600,"best_close_cm":0.8,"best_score":1720},
        {"name":"아라","best_fast_ms":710,"best_close_cm":1.2,"best_score":1650},
        {"name":"보","best_fast_ms":540,"best_close_cm":2.5,"best_score":1600},
        {"name":"민","best_fast_ms":880,"best_close_cm":0.6,"best_score":1500},
        {"name":"켄","best_fast_ms":760,"best_close_cm":1.0,"best_score":1480},
    ]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)

def load_scores() -> List[Dict]:
    ensure_sample_data()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_current_player(name: str):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump({"player_name": name, "ts": time.time()}, f, ensure_ascii=False, indent=2)

def get_fast_board(data, topk=5):
    rows = [d for d in data if d.get("best_fast_ms") is not None]
    rows.sort(key=lambda x: x["best_fast_ms"])
    return rows[:topk]

def get_close_board(data, topk=5):
    rows = [d for d in data if d.get("best_close_cm") is not None]
    rows.sort(key=lambda x: x["best_close_cm"])
    return rows[:topk]

def reset_leaderboard():
    """리더보드를 빈 배열로 초기화"""
    sample = []
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)
    print("[LEADERBOARD] 리더보드가 초기화되었습니다")

def save_score(name: str, best_fast_ms: Optional[int] = None, best_close_cm: Optional[float] = None):
    """새로운 기록을 리더보드에 저장"""
    # 기존 데이터 로드
    data = load_scores()
    
    # 현재 플레이어의 기존 기록 찾기
    player_record = None
    for record in data:
        if record.get("name") == name:
            player_record = record
            break
    
    # 새로운 기록 생성 또는 업데이트
    if player_record is None:
        # 새로운 플레이어
        player_record = {
            "name": name,
            "best_fast_ms": best_fast_ms,
            "best_close_cm": best_close_cm,
            "best_score": 0  # 기본값
        }
        data.append(player_record)
    else:
        # 기존 플레이어 기록 업데이트
        if best_fast_ms is not None:
            if player_record.get("best_fast_ms") is None or best_fast_ms < player_record["best_fast_ms"]:
                player_record["best_fast_ms"] = best_fast_ms
                fast_sec = best_fast_ms / 1000.0
                print(f"[LEADERBOARD] 새로운 SPEED 기록! {name}: {fast_sec:.2f}초")
        
        if best_close_cm is not None:
            if player_record.get("best_close_cm") is None or best_close_cm < player_record["best_close_cm"]:
                player_record["best_close_cm"] = best_close_cm
                print(f"[LEADERBOARD] 새로운 CLOSEST 기록! {name}: {best_close_cm}cm")
    
    # 점수 계산 (SPEED 모드 기준)
    if player_record.get("best_fast_ms") is not None:
        # SPEED 모드 점수: 2000ms 기준으로 계산 (빠를수록 높은 점수)
        base_score = 2000
        time_score = max(0, base_score - player_record["best_fast_ms"])
        player_record["best_score"] = time_score
    
    # 데이터 저장
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[LEADERBOARD] 기록 저장 완료: {name}")
    return player_record
