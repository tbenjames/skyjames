"""
SkyJames - Model Interpretability (SHAP/LIME)
"""

import numpy as np
import matplotlib.pyplot as plt
import torch
import cv2
from captum.attr import IntegratedGradients, Saliency
from src.perception.lane_net_cpu import LaneNetCPU

class ModelInterpreter:
    def __init__(self, model_path="models/lane_net_optimized.pth"):
        self.device = torch.device('cpu')
        self.model = LaneNetCPU()
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        
    def explain_prediction(self, image, method='integrated_gradients'):
        """
        Explain why the model made a certain prediction
        """
        # Preprocess image
        if isinstance(image, np.ndarray):
            image_tensor = torch.from_numpy(image).float()
            if image_tensor.ndim == 3:
                image_tensor = image_tensor.permute(2, 0, 1)
            image_tensor = image_tensor.unsqueeze(0)
        else:
            image_tensor = image
        
        if method == 'integrated_gradients':
            return self._integrated_gradients(image_tensor)
        elif method == 'saliency':
            return self._saliency(image_tensor)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _integrated_gradients(self, image_tensor):
        ig = IntegratedGradients(self.model)
        attributions, delta = ig.attribute(image_tensor, target=0, return_convergence_delta=True)
        return attributions.detach().numpy()
    
    def _saliency(self, image_tensor):
        saliency = Saliency(self.model)
        attributions = saliency.attribute(image_tensor, target=0)
        return attributions.detach().numpy()
    
    def visualize_explanation(self, image, attributions):
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        
        # Original image
        axes[0].imshow(image)
        axes[0].set_title('Original')
        axes[0].axis('off')
        
        # Attribution heatmap
        attr_map = np.mean(attributions.squeeze(), axis=0)
        axes[1].imshow(attr_map, cmap='hot')
        axes[1].set_title('Model Attention')
        axes[1].axis('off')
        
        plt.tight_layout()
        return fig

# Example usage
if __name__ == "__main__":
    import cv2
    interpreter = ModelInterpreter()
    
    # Load sample image
    img = cv2.imread("data/test/sample.jpg")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_tensor = torch.from_numpy(img).float().permute(2, 0, 1).unsqueeze(0)
    
    # Get explanation
    attributions = interpreter.explain_prediction(img_tensor)
    interpreter.visualize_explanation(img, attributions)
