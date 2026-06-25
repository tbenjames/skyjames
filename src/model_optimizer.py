"""
SkyJames - Model Optimization
Quantization, pruning, and optimization
"""

import torch
import torch.nn as nn
import numpy as np

class ModelOptimizer:
    def __init__(self, model):
        self.model = model
        self.original_size = self._get_model_size()
    
    def _get_model_size(self):
        """Get model size in MB"""
        if self.model is None:
            return 0
        param_size = 0
        for param in self.model.parameters():
            param_size += param.nelement() * param.element_size()
        buffer_size = 0
        for buffer in self.model.buffers():
            buffer_size += buffer.nelement() * buffer.element_size()
        size_all_mb = (param_size + buffer_size) / 1024**2
        return size_all_mb
    
    def quantize_to_int8(self, sample_input):
        """Convert model to INT8 quantization"""
        if self.model is None:
            print("⚠️ No model to quantize")
            return None
        
        try:
            # Try to import quantization modules
            import torch.quantization as quant
            self.model.eval()
            
            # Fuse modules (simplified)
            self.model = quant.fuse_modules(self.model, [['conv1', 'bn1', 'relu1']])
            
            # Prepare quantization
            self.model.qconfig = torch.quantization.default_qconfig
            quant.prepare(self.model, inplace=True)
            
            # Calibrate with sample data
            if sample_input is not None:
                for _ in range(10):
                    self.model(sample_input)
            
            # Convert to quantized model
            quantized_model = quant.convert(self.model, inplace=False)
            return quantized_model
        except Exception as e:
            print(f"Quantization failed: {e}")
            return self.model
    
    def prune_model(self, amount=0.3):
        """Prune model weights"""
        if self.model is None:
            print("⚠️ No model to prune")
            return None
        
        try:
            import torch.nn.utils.prune as prune
            
            for name, module in self.model.named_modules():
                if isinstance(module, nn.Conv2d) or isinstance(module, nn.Linear):
                    prune.l1_unstructured(module, name='weight', amount=amount)
                    prune.remove(module, 'weight')
            
            return self.model
        except Exception as e:
            print(f"Pruning failed: {e}")
            return self.model
    
    def optimize_for_mobile(self, sample_input):
        """Optimize for mobile deployment"""
        if self.model is None:
            print("⚠️ No model to optimize")
            return None
        
        try:
            import torch.jit
            self.model.eval()
            traced_model = torch.jit.trace(self.model, sample_input)
            return traced_model
        except Exception as e:
            print(f"Mobile optimization failed: {e}")
            return self.model
    
    def get_optimization_report(self):
        """Generate optimization report"""
        optimized_size = self._get_model_size()
        reduction = ((self.original_size - optimized_size) / (self.original_size + 1)) * 100
        
        return {
            'original_size_mb': self.original_size,
            'optimized_size_mb': optimized_size,
            'size_reduction_percent': reduction,
            'optimizations_applied': ['quantization', 'pruning']
        }
