"""
Lane Detection Implementation
"""

import cv2
import numpy as np
from collections import deque
from src.config import Config
from src.utils import calculate_slope

class LaneDetector:
    def __init__(self, config=None):
        self.config = config or Config()
        
        # For smoothing
        self.left_history = deque(maxlen=self.config.HISTORY_LENGTH)
        self.right_history = deque(maxlen=self.config.HISTORY_LENGTH)
        
        # Frame dimensions
        self.frame_height = None
        self.frame_width = None
        
    def process_frame(self, frame, draw_debug=False):
        """Main processing pipeline"""
        self.frame_height, self.frame_width = frame.shape[:2]
        original = np.copy(frame)
        
        # Step 1: Preprocessing
        gray = self._grayscale(frame)
        blurred = self._gaussian_blur(gray)
        edges = self._canny_edges(blurred)
        masked = self._region_of_interest(edges)
        
        # Step 2: Detect lines
        lines = self._hough_lines(masked)
        
        # Step 3: Average and smooth lines
        left_line, right_line = self._get_averaged_lines(lines)
        left_line = self._smooth_line(left_line, self.left_history)
        right_line = self._smooth_line(right_line, self.right_history)
        
        # Step 4: Draw results
        result = self._draw_lines(original, left_line, right_line)
        
        if draw_debug:
            return result, edges, masked
        return result
    
    def _grayscale(self, img):
        """Convert to grayscale"""
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    def _gaussian_blur(self, img):
        """Apply Gaussian blur"""
        kernel_size = 5
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
    
    def _canny_edges(self, img):
        """Detect edges using Canny"""
        return cv2.Canny(img, self.config.CANNY_LOW, self.config.CANNY_HIGH)
    
    def _region_of_interest(self, img):
        """Mask everything except the road"""
        height, width = img.shape
        # Use config ratios
        tl_x = int(width * self.config.ROI_TOP_LEFT[0])
        tl_y = int(height * self.config.ROI_TOP_LEFT[1])
        tr_x = int(width * self.config.ROI_TOP_RIGHT[0])
        tr_y = int(height * self.config.ROI_TOP_RIGHT[1])
        bl_x = int(width * self.config.ROI_BOTTOM_LEFT[0])
        bl_y = int(height * self.config.ROI_BOTTOM_LEFT[1])
        br_x = int(width * self.config.ROI_BOTTOM_RIGHT[0])
        br_y = int(height * self.config.ROI_BOTTOM_RIGHT[1])
        
        vertices = np.array([[(bl_x, bl_y), (tl_x, tl_y), 
                            (tr_x, tr_y), (br_x, br_y)]], dtype=np.int32)
        
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, vertices, 255)
        return cv2.bitwise_and(img, mask)
    
    def _hough_lines(self, img):
        """Detect lines using Hough Transform"""
        return cv2.HoughLinesP(
            img,
            rho=1,
            theta=np.pi/180,
            threshold=self.config.HOUGH_THRESHOLD,
            minLineLength=self.config.MIN_LINE_LENGTH,
            maxLineGap=self.config.MAX_LINE_GAP
        )
    
    def _get_averaged_lines(self, lines):
        """Separate and average left/right lines"""
        if lines is None:
            return None, None
        
        left_lines = []
        right_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            slope = calculate_slope(x1, y1, x2, y2)
            
            if slope is None or abs(slope) < self.config.MIN_SLOPE:
                continue
            
            if slope < 0:
                left_lines.append((slope, (x1, y1, x2, y2)))
            else:
                right_lines.append((slope, (x1, y1, x2, y2)))
        
        left_line = self._average_line(left_lines) if left_lines else None
        right_line = self._average_line(right_lines) if right_lines else None
        
        return left_line, right_line
    
    def _average_line(self, lines):
        """Calculate average line from multiple segments"""
        if not lines:
            return None
        
        slopes = []
        intercepts = []
        
        for slope, (x1, y1, x2, y2) in lines:
            intercept = y1 - slope * x1
            slopes.append(slope)
            intercepts.append(intercept)
        
        avg_slope = np.mean(slopes)
        avg_intercept = np.mean(intercepts)
        
        # Extrapolate to bottom and top of ROI
        y1 = self.frame_height
        y2 = int(self.frame_height * self.config.ROI_TOP_LEFT[1])
        
        x1 = int((y1 - avg_intercept) / avg_slope)
        x2 = int((y2 - avg_intercept) / avg_slope)
        
        return [x1, y1, x2, y2]
    
    def _smooth_line(self, new_line, history):
        """Apply temporal smoothing"""
        if new_line is None:
            return None
        
        history.append(new_line)
        if len(history) > 0:
            smoothed = np.mean(history, axis=0).astype(int)
            return smoothed.tolist()
        return new_line
    
    def _draw_lines(self, img, left_line, right_line):
        """Draw lane lines on image"""
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
    
    def process_video(self, video_path, output_path=None, progress_callback=None):
        """Process entire video"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Set output path
        if output_path is None:
            output_path = f"output_{video_path}"
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*self.config.OUTPUT_FOURCC)
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            result = self.process_frame(frame)
            out.write(result)
            
            frame_count += 1
            if progress_callback:
                progress_callback(frame_count, total_frames)
            
            # Print progress
            if frame_count % 30 == 0:
                print(f"Processed {frame_count}/{total_frames} frames")
        
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print(f"Video saved to: {output_path}")
        return output_path
