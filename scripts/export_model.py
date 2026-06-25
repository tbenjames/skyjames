"""
Export model for deployment (ONNX, TensorRT, etc.)
"""

import torch
import onnx
import onnxruntime
import numpy as np
from src.perception.lane_net_cpu import LaneNetCPU
from src.config import Config

def export_to_onnx(model_path, output_path="models/lane_model.onnx"):
    """Export PyTorch model to ONNX format"""
    
    print("🔄 Exporting to ONNX...")
    
    # Load model
    device = torch.device('cpu')
    model = LaneNetCPU().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    # Create dummy input
    dummy_input = torch.randn(1, 3, 128, 256)
    
    # Export
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size', 2: 'height', 3: 'width'},
            'output': {0: 'batch_size', 2: 'height', 3: 'width'}
        }
    )
    
    print(f"✅ ONNX model saved: {output_path}")
    
    # Verify ONNX model
    onnx_model = onnx.load(output_path)
    onnx.checker.check_model(onnx_model)
    print("✅ ONNX model verified")
    
    return output_path

def test_onnx_inference(onnx_path, sample_input=None):
    """Test ONNX model inference"""
    
    print("🧪 Testing ONNX inference...")
    
    # Create sample input
    if sample_input is None:
        sample_input = np.random.randn(1, 3, 128, 256).astype(np.float32)
    
    # Run ONNX inference
    ort_session = onnxruntime.InferenceSession(onnx_path)
    ort_inputs = {ort_session.get_inputs()[0].name: sample_input}
    ort_outputs = ort_session.run(None, ort_inputs)
    
    print(f"✅ ONNX inference successful! Output shape: {ort_outputs[0].shape}")
    return ort_outputs[0]

def export_to_tensorrt(onnx_path, output_path="models/lane_model.trt"):
    """Convert ONNX to TensorRT (requires NVIDIA GPU)"""
    
    try:
        import tensorrt as trt
        
        print("🔄 Converting to TensorRT...")
        logger = trt.Logger(trt.Logger.WARNING)
        builder = trt.Builder(logger)
        network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
        parser = trt.OnnxParser(network, logger)
        
        with open(onnx_path, 'rb') as f:
            if not parser.parse(f.read()):
                for error in range(parser.num_errors):
                    print(parser.get_error(error))
                return None
        
        # Build engine
        builder.max_workspace_size = 1 << 30
        builder.max_batch_size = 1
        engine = builder.build_cuda_engine(network)
        
        with open(output_path, 'wb') as f:
            f.write(engine.serialize())
        
        print(f"✅ TensorRT engine saved: {output_path}")
        return output_path
        
    except ImportError:
        print("⚠️ TensorRT not available. Skipping...")
        return None

if __name__ == "__main__":
    # Export models
    model_path = "models/lane_net_optimized.pth"
    
    # Export to ONNX
    onnx_path = export_to_onnx(model_path)
    
    # Test ONNX inference
    test_onnx_inference(onnx_path)
    
    # Export to TensorRT (optional)
    export_to_tensorrt(onnx_path)
