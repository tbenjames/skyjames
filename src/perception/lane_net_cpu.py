"""
CPU-Optimized Lane Detection Network - Binary Segmentation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2
from collections import deque
import os
from src.config import Config

class LaneNetCPU(nn.Module):
    """Ultra-lightweight lane detection network - binary output"""
    
    def __init__(self, input_channels=3):
        super(LaneNetCPU, self).__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv2d(input_channels, 16, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(32, 16, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
        )
        
        # Output head - single channel for binary segmentation
        self.head = nn.Conv2d(16, 1, kernel_size=1)
    
    def forward(self, x):
        if x.max() > 1.0:
            x = x / 255.0
        
        input_size = x.shape[2:]
        features = self.encoder(x)
        decoded = self.decoder(features)
        
        if decoded.shape[2:] != input_size:
            decoded = F.interpolate(decoded, size=input_size, mode='bilinear', align_corners=False)
        
        return torch.sigmoid(self.head(decoded))

class OptimizedLaneDetector:
    """CPU-optimized lane detector"""
    
    def __init__(self, config=None, model_path=None):
        self.config = config or Config()
        self.device = torch.device('cpu')
        
        self.model = LaneNetCPU(input_channels=3).to(self.device)
        
        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(
                torch.load(model_path, map_location=torch.device('cpu'))
            )
            print(f"Loaded model from {model_path}")
            self.use_neural = True
        else:
            print("Using traditional method (no model found)")
            self.use_neural = False
        
        self.model.eval()
        self.left_history = deque(maxlen=self.config.HISTORY_LENGTH)
        self.right_history = deque(maxlen=self.config.HISTORY_LENGTH)
        self.input_size = self.config.IMAGE_SIZE
    
    def process_frame(self, frame, use_neural=True):
        """Process frame using neural network or traditional method"""
        original = np.copy(frame)
        height, width = frame.shape[:2]
        
        if use_neural and self.use_neural:
            try:
                result, left_line, right_line = self._process_neural(frame, height, width)
                if left_line is not None and right_line is not None:
                    return result, left_line, right_line
            except Exception as e:
                print(f"Neural failed: {e}, falling back")
        
        return self._process_traditional(frame)
    
    def _process_neural(self, frame, height, width):
        """Neural network-based processing"""
        input_tensor = self._preprocess(frame)
        
        with torch.no_grad():
            output = self.model(input_tensor)
            segmentation = output.squeeze().cpu().numpy()
        
        left_line, right_line = self._extract_lanes(segmentation, height, width)
        left_line = self._smooth_line(left_line, self.left_history)
        right_line = self._smooth_line(right_line, self.right_history)
        result = self._draw_lines(frame, left_line, right_line)
        
        return result, left_line, right_line
    
    def _preprocess(self, frame):
        """Preprocess frame for network"""
        resized = cv2.resize(frame, (self.input_size[1], self.input_size[0]))
        tensor = torch.from_numpy(resized).float().permute(2, 0, 1)
        tensor = tensor.unsqueeze(0).to(self.device)
        return tensor / 255.0
    
    def _extract_lanes(self, segmentation, height, width):
        """Extract lane lines from segmentation"""
        # Binary segmentation: values > 0.5 are lanes
        lane_mask = (segmentation > 0.5).astype(np.uint8) * 255
        
        lane_mask = cv2.resize(lane_mask, (width, height), interpolation=cv2.INTER_NEAREST)
        return self._sliding_window(lane_mask, height, width)
    
    def _sliding_window(self, lane_mask, height, width):
        """Sliding window lane detection"""
        nonzero = lane_mask.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        
        if len(nonzeroy) == 0:
            return None, None
        
        histogram = np.sum(lane_mask[height//2:, :], axis=0)
        midpoint = width // 2
        
        leftx_base = np.argmax(histogram[:midpoint]) if np.any(histogram[:midpoint]) else width//4
        rightx_base = np.argmax(histogram[midpoint:]) + midpoint if np.any(histogram[midpoint:]) else 3*width//4
        
        n_windows = 6
        window_height = height // n_windows
        margin = 50
        
        left_lane_inds = []
        right_lane_inds = []
        leftx_current = leftx_base
        rightx_current = rightx_base
        
        for window in range(n_windows):
            win_y_low = height - (window + 1) * window_height
            win_y_high = height - window * window_height
            
            win_xleft_low = max(0, leftx_current - margin)
            win_xleft_high = min(width, leftx_current + margin)
            win_xright_low = max(0, rightx_current - margin)
            win_xright_high = min(width, rightx_current + margin)
            
            good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                            (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
            good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                             (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]
            
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)
            
            if len(good_left_inds) > 30:
                leftx_current = int(np.mean(nonzerox[good_left_inds]))
            if len(good_right_inds) > 30:
                rightx_current = int(np.mean(nonzerox[good_right_inds]))
        
        if left_lane_inds and right_lane_inds:
            left_inds = np.concatenate(left_lane_inds) if any(left_lane_inds) else []
            right_inds = np.concatenate(right_lane_inds) if any(right_lane_inds) else []
            
            if len(left_inds) > 0 and len(right_inds) > 0:
                leftx = nonzerox[left_inds]
                lefty = nonzeroy[left_inds]
                rightx = nonzerox[right_inds]
                righty = nonzeroy[right_inds]
                
                if len(leftx) > 3 and len(rightx) > 3:
                    left_fit = np.polyfit(lefty, leftx, 2)
                    right_fit = np.polyfit(righty, rightx, 2)
                    
                    y_vals = np.linspace(0, height-1, height)
                    left_fitx = left_fit[0]*y_vals**2 + left_fit[1]*y_vals + left_fit[2]
                    right_fitx = right_fit[0]*y_vals**2 + right_fit[1]*y_vals + right_fit[2]
                    
                    roi_top = int(height * self.config.ROI_TOP_LEFT[1])
                    left_line = [int(left_fitx[-1]), height, int(left_fitx[roi_top]), roi_top]
                    right_line = [int(right_fitx[-1]), height, int(right_fitx[roi_top]), roi_top]
                    
                    return left_line, right_line
        
        return None, None
    
    def _process_traditional(self, frame):
        """Traditional OpenCV-based lane detection"""
        height, width = frame.shape[:2]
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, self.config.CANNY_LOW, self.config.CANNY_HIGH)
        
        mask = np.zeros_like(edges)
        vertices = np.array([[
            (0, height),
            (int(width * 0.45), int(height * 0.65)),
            (int(width * 0.55), int(height * 0.65)),
            (width, height)
        ]], dtype=np.int32)
        cv2.fillPoly(mask, vertices, 255)
        masked = cv2.bitwise_and(edges, mask)
        
        lines = cv2.HoughLinesP(masked, 1, np.pi/180, 
                               self.config.HOUGH_THRESHOLD,
                               minLineLength=self.config.MIN_LINE_LENGTH,
                               maxLineGap=self.config.MAX_LINE_GAP)
        
        if lines is None:
            return frame, None, None
        
        left_lines = []
        right_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 - x1 == 0:
                continue
            slope = (y2 - y1) / (x2 - x1)
            
            if abs(slope) < 0.3:
                continue
            
            if slope < 0:
                left_lines.append([x1, y1, x2, y2])
            else:
                right_lines.append([x1, y1, x2, y2])
        
        left_line = self._average_lines(left_lines) if left_lines else None
        right_line = self._average_lines(right_lines) if right_lines else None
        
        left_line = self._smooth_line(left_line, self.left_history)
        right_line = self._smooth_line(right_line, self.right_history)
        
        result = self._draw_lines(frame, left_line, right_line)
        return result, left_line, right_line
    
    def _average_lines(self, lines):
        if not lines:
            return None
        x1_avg = int(np.mean([line[0] for line in lines]))
        y1_avg = int(np.mean([line[1] for line in lines]))
        x2_avg = int(np.mean([line[2] for line in lines]))
        y2_avg = int(np.mean([line[3] for line in lines]))
        return [x1_avg, y1_avg, x2_avg, y2_avg]
    
    def _smooth_line(self, new_line, history):
        if new_line is None:
            return None
        history.append(new_line)
        if history:
            smoothed = np.mean(history, axis=0).astype(int)
            return smoothed.tolist()
        return new_line
    
    def _draw_lines(self, img, left_line, right_line):
        result = np.copy(img)
        overlay = np.zeros_like(result)
        
        if left_line is not None:
            x1, y1, x2, y2 = left_line
            cv2.line(overlay, (x1, y1), (x2, y2), 
                    self.config.LEFT_LANE_COLOR, self.config.LANE_THICKNESS)
        
        if right_line is not None:
            x1, y1, x2, y2 = right_line
            cv2.line(overlay, (x1, y1), (x2, y2), 
                    self.config.RIGHT_LANE_COLOR, self.config.LANE_THICKNESS)
        
        return cv2.addWeighted(result, 0.9, overlay, 0.6, 0)
