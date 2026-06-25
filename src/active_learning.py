"""
SkyJames - Active Learning System
Automatically selects most informative samples for labeling
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from scipy.spatial.distance import cdist

class ActiveLearner:
    def __init__(self, pool_size=1000):
        self.pool_size = pool_size
        self.labeled_data = []
        self.unlabeled_data = []
        self.model = RandomForestClassifier()
    
    def add_unlabeled(self, samples):
        """Add new unlabeled samples to pool"""
        self.unlabeled_data.extend(samples)
        if len(self.unlabeled_data) > self.pool_size:
            self.unlabeled_data = self.unlabeled_data[-self.pool_size:]
    
    def query_samples(self, n_samples=10):
        """Select most uncertain samples for labeling"""
        if len(self.unlabeled_data) < n_samples:
            return self.unlabeled_data
        
        # Calculate uncertainty scores
        uncertainties = []
        for sample in self.unlabeled_data:
            if len(self.labeled_data) > 0:
                # Distance to labeled data
                distances = cdist([sample], np.array(self.labeled_data))
                uncertainty = float(np.min(distances))
                uncertainties.append(uncertainty)
            else:
                uncertainties.append(np.random.random())
        
        # Select top N most uncertain
        indices = np.argsort(uncertainties)[-n_samples:]
        selected = [self.unlabeled_data[i] for i in indices]
        
        # Remove selected from pool
        self.unlabeled_data = [x for i, x in enumerate(self.unlabeled_data) if i not in indices]
        
        return selected
    
    def add_labeled(self, samples, labels):
        """Add labeled samples to training set"""
        self.labeled_data.extend(samples)
        self.model.fit(self.labeled_data, labels)
    
    def predict(self, sample):
        """Predict using current model"""
        if len(self.labeled_data) > 0:
            return self.model.predict([sample])[0]
        return None
