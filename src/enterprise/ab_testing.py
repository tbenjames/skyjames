
"""
SkyJames - A/B Testing
"""

import os
import json
import random
from datetime import datetime

class ABTesting:
    def __init__(self, config_path="config/ab_testing.json"):
        self.config_path = config_path
        self.load_config()
        print("✅ A/B Testing initialized")
    
    def load_config(self):
        try:
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
        except:
            self.config = {
                "experiments": [],
                "default_traffic": 50
            }
            self.save_config()
    
    def start_experiment(self, name, variants, traffic_split=None):
        if traffic_split is None:
            traffic_split = {v: 100 // len(variants) for v in variants}
        
        experiment = {
            "id": len(self.config["experiments"]) + 1,
            "name": name,
            "start_time": datetime.now().isoformat(),
            "variants": variants,
            "traffic_split": traffic_split,
            "results": {v: {"impressions": 0, "success": 0} for v in variants}
        }
        self.config["experiments"].append(experiment)
        self.save_config()
        return experiment
    
    def get_variant(self, experiment_id, user_id=None):
        exp = self._get_experiment(experiment_id)
        if not exp:
            return None
        
        if user_id:
            seed = hash(f"{exp['id']}_{user_id}")
            random.seed(seed)
            choice = random.random() * 100
        else:
            choice = random.random() * 100
        
        cumulative = 0
        for variant, percentage in exp["traffic_split"].items():
            cumulative += percentage
            if choice < cumulative:
                return variant
        
        return list(exp["variants"])[0]
    
    def record_result(self, experiment_id, variant, success=True):
        exp = self._get_experiment(experiment_id)
        if exp:
            exp["results"][variant]["impressions"] += 1
            if success:
                exp["results"][variant]["success"] += 1
            self.save_config()
    
    def get_experiment_results(self, experiment_id):
        exp = self._get_experiment(experiment_id)
        if exp:
            return exp["results"]
        return None
    
    def get_winner(self, experiment_id):
        results = self.get_experiment_results(experiment_id)
        if not results:
            return None
        
        best_variant = None
        best_rate = 0
        for variant, data in results.items():
            if data["impressions"] > 0:
                rate = data["success"] / data["impressions"]
                if rate > best_rate:
                    best_rate = rate
                    best_variant = variant
        
        return best_variant, best_rate
    
    def _get_experiment(self, experiment_id):
        for exp in self.config["experiments"]:
            if exp["id"] == experiment_id:
                return exp
        return None
    
    def save_config(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)
