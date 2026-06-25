
"""
SkyJames - MLflow Integration
"""

import mlflow
import torch
import os
from datetime import datetime

class SkyJamesMLflow:
    def __init__(self, tracking_uri="http://localhost:5000", experiment_name="SkyJames"):
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        self.experiment = mlflow.get_experiment_by_name(experiment_name)
        if self.experiment is None:
            self.experiment_id = mlflow.create_experiment(experiment_name)
        else:
            self.experiment_id = self.experiment.experiment_id
        print("✅ MLflow tracking initialized")
    
    def start_run(self, run_name=None):
        if run_name is None:
            run_name = f"skyjames_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return mlflow.start_run(run_name=run_name)
    
    def log_params(self, params):
        for key, value in params.items():
            mlflow.log_param(key, value)
    
    def log_metrics(self, metrics, step=None):
        for key, value in metrics.items():
            mlflow.log_metric(key, value, step=step)
    
    def log_model(self, model, model_name, model_path):
        mlflow.pytorch.log_model(model, model_name)
        os.makedirs(model_path, exist_ok=True)
        torch.save(model.state_dict(), os.path.join(model_path, f"{model_name}.pth"))
    
    def get_best_model(self, metric="val_loss", ascending=True):
        client = mlflow.tracking.MlflowClient()
        runs = client.search_runs(
            experiment_ids=[self.experiment_id],
            order_by=[f"metrics.{metric} {'ASC' if ascending else 'DESC'}"]
        )
        if runs:
            best_run = runs[0]
            return best_run.info.run_id, best_run.data.metrics.get(metric)
        return None, None
