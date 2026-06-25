"""
SkyJames - MLflow Integration for Model Tracking
"""

import mlflow
import mlflow.pytorch
import torch
import os
from datetime import datetime
from pathlib import Path

class SkyJamesMLflow:
    def __init__(self, tracking_uri="http://localhost:5000", experiment_name="SkyJames"):
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        self.experiment = mlflow.get_experiment_by_name(experiment_name)
    
    def start_run(self, run_name=None):
        """Start a new MLflow run"""
        if run_name is None:
            run_name = f"skyjames_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return mlflow.start_run(run_name=run_name)
    
    def log_params(self, params):
        """Log parameters"""
        for key, value in params.items():
            mlflow.log_param(key, value)
    
    def log_metrics(self, metrics, step=None):
        """Log metrics"""
        for key, value in metrics.items():
            mlflow.log_metric(key, value, step=step)
    
    def log_model(self, model, model_name, model_path):
        """Log model to MLflow"""
        mlflow.pytorch.log_model(model, model_name)
        
        # Save model locally
        os.makedirs(model_path, exist_ok=True)
        torch.save(model.state_dict(), os.path.join(model_path, f"{model_name}.pth"))
    
    def log_artifacts(self, artifact_dir):
        """Log artifacts"""
        mlflow.log_artifacts(artifact_dir)
    
    def get_best_model(self, metric="val_loss", ascending=True):
        """Get best model from experiments"""
        client = mlflow.tracking.MlflowClient()
        runs = client.search_runs(
            experiment_ids=[self.experiment.experiment_id],
            order_by=[f"metrics.{metric} {'ASC' if ascending else 'DESC'}"]
        )
        if runs:
            best_run = runs[0]
            return best_run.info.run_id, best_run.data.metrics.get(metric)
        return None, None
    
    def compare_runs(self, run_ids):
        """Compare multiple runs"""
        client = mlflow.tracking.MlflowClient()
        runs = []
        for run_id in run_ids:
            run = client.get_run(run_id)
            runs.append({
                'run_id': run_id,
                'metrics': run.data.metrics,
                'params': run.data.params,
                'tags': run.data.tags
            })
        return runs

def log_training_run(model, train_loss, val_loss, accuracy, params):
    """Helper to log a training run"""
    mlflow_tracker = SkyJamesMLflow()
    
    with mlflow_tracker.start_run("lane_detection_training"):
        # Log parameters
        mlflow_tracker.log_params(params)
        
        # Log metrics
        mlflow_tracker.log_metrics({
            'train_loss': train_loss,
            'val_loss': val_loss,
            'accuracy': accuracy
        })
        
        # Log model
        mlflow_tracker.log_model(model, "lane_net", "models/mlflow")
        
        print(f"✅ Training logged to MLflow")
        return mlflow_tracker.get_best_model()
