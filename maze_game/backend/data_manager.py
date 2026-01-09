import json
import os
import datetime
from pathlib import Path

DATA_FILE = "maze_game_data.json"

class DataManager:
    def __init__(self):
        self.file_path = DATA_FILE
        self.data = self._load_data()

    def _load_data(self):
        if not os.path.exists(self.file_path):
            return {
                "leaderboard": {"normal": [], "daily": []},
                "streak": {"count": 0, "last_date": None, "record": 0}
            }
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except:
            return {
                "leaderboard": {"normal": [], "daily": []},
                "streak": {"count": 0, "last_date": None, "record": 0}
            }

    def _save_data(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    # --- LEADERBOARD ---
    def add_score(self, mode, player_name, score, time_taken, moves, hints):
        entry = {
            "name": player_name,
            "score": score,
            "time": time_taken,
            "moves": moves,
            "hints": hints,
            "date": datetime.date.today().isoformat()
        }
        
        category = "daily" if mode == "Daily" else "normal"
        self.data["leaderboard"][category].append(entry)
        
        # Sort: Score (Desc), Moves (Asc), Time (Asc)
        self.data["leaderboard"][category].sort(
            key=lambda x: (-x["score"], x["moves"], x["time"])
        )
        
        self.data["leaderboard"][category] = self.data["leaderboard"][category][:50] # Top 50
        self._save_data()

    def get_leaderboard(self, mode):
        category = "daily" if mode == "Daily" else "normal"
        return self.data["leaderboard"][category]

    # --- STREAK ---
    def update_streak(self):
        today = datetime.date.today().isoformat()
        last_date = self.data["streak"]["last_date"]
        
        if last_date == today:
            return self.data["streak"]["count"] # Already done today
            
        if last_date:
            last = datetime.date.fromisoformat(last_date)
            curr = datetime.date.fromisoformat(today)
            delta = (curr - last).days
            
            if delta == 1:
                self.data["streak"]["count"] += 1
            else:
                self.data["streak"]["count"] = 1 # Reset if missed a day
        else:
            self.data["streak"]["count"] = 1
            
        self.data["streak"]["last_date"] = today
        if self.data["streak"]["count"] > self.data["streak"]["record"]:
            self.data["streak"]["record"] = self.data["streak"]["count"]
            
        self._save_data()
        return self.data["streak"]["count"]

    def get_streak_info(self):
        today = datetime.date.today().isoformat()
        last = self.data["streak"]["last_date"]
        count = self.data["streak"]["count"]
        
        # Check if broken proactively for UI
        if last and last != today:
             delta = (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(last)).days
             if delta > 1:
                 return 0, today # Broken
        
        return count, last
