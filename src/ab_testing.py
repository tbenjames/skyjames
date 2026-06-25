"""
SkyJames - A/B Testing Framework for Model Comparison
"""

import random
import json
from datetime import datetime
from collections import defaultdict

class ABTesting:
    def __init__(self, config_path="config/ab_testing.json"):
        self.config_path = config_path
        self.load_config()
        self.results = defaultdict(list)
    
    def load_config(self):
        """Load A/B testing configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {
                'experiments': [],
                'default_traffic': 50  # 50% to each variant
            }
    
    def start_experiment(self, name, variants, traffic_split=None):
        """Start a new A/B experiment"""
        if traffic_split is None:
            traffic_split = {v: 100 // len(variants) for v in variants}
        
        experiment = {
            'id': len(self.config['experiments']) + 1,
            'name': name,
            'start_time': datetime.now().isoformat(),
            'variants': variants,
            'traffic_split': traffic_split,
            'results': {v: {'impressions': 0, 'success': 0} for v in variants}
        }
        self.config['experiments'].append(experiment)
        self.save_config()
        return experiment
    
    def get_variant(self, experiment_id, user_id=None):
        """Get variant for a user"""
        exp = self._get_experiment(experiment_id)
        if not exp:
            return None
        
        # Deterministic assignment based on user_id
        if user_id:
            seed = hash(f"{exp['id']}_{user_id}")
            random.seed(seed)
            choice = random.random() * 100
        else:
            choice = random.random() * 100
        
        # Assign variant based on traffic split
        cumulative = 0
        for variant, percentage in exp['traffic_split'].items():
            cumulative += percentage
            if choice < cumulative:
                return variant
        
        return list(exp['variants'])[0]
    
    def record_result(self, experiment_id, variant, success=True):
        """Record A/B test result"""
        exp = self._get_experiment(experiment_id)
        if exp:
            exp['results'][variant]['impressions'] += 1
            if success:
                exp['results'][variant]['success'] += 1
            self.save_config()
    
    def get_experiment_results(self, experiment_id):
        """Get results for an experiment"""
        exp = self._get_experiment(experiment_id)
        if exp:
            return exp['results']
        return None
    
    def get_winner(self, experiment_id):
        """Determine the winning variant"""
        results = self.get_experiment_results(experiment_id)
        if not results:
            return None
        
        best_variant = None
        best_rate = 0
        for variant, data in results.items():
            if data['impressions'] > 0:
                rate = data['success'] / data['impressions']
                if rate > best_rate:
                    best_rate = rate
                    best_variant = variant
        
        return best_variant, best_rate
    
    def _get_experiment(self, experiment_id):
        """Get experiment by ID"""
        for exp in self.config['experiments']:
            if exp['id'] == experiment_id:
                return exp
        return None
    
    def save_config(self):
        """Save configuration"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

# Example usage
def test_models():
    ab = ABTesting()
    
    # Start experiment comparing two models
    exp = ab.start_experiment(
        "lane_detection_models",
        ["model_v1", "model_v2"],
        {"model_v1": 50, "model_v2": 50}
    )
    
    # In production, use:
    # variant = ab.get_variant(exp['id'], user_id)
    # if variant == 'model_v1':
    #     use_model_v1()
    # else:
    #     use_model_v2()
    
    return ab
