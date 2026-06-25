"""
Test and compare neural network vs traditional method on real-world videos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.config import Config

def analyze_video(video_path, max_frames=200):
    """Analyze video with both methods and collect metrics"""
    
    config = Config()
    model_path = os.path.join(config.MODEL_DIR, 'lane_net_optimized.pth')
    
    # Initialize detector with model
    detector = OptimizedLaneDetector(config, model_path=model_path if os.path.exists(model_path) else None)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return None
    
    total_frames = min(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), max_frames)
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    
    print(f"\nAnalyzing: {os.path.basename(video_path)}")
    print(f"Frames: {total_frames} | FPS: {fps}")
    print("=" * 60)
    
    # Metrics storage
    results = {
        'traditional': {'times': [], 'lanes_detected': [], 'left': [], 'right': []},
        'neural': {'times': [], 'lanes_detected': [], 'left': [], 'right': []},
        'frames': []
    }
    
    frame_count = 0
    
    # Progress bar
    progress = tqdm(total=total_frames, desc="Processing")
    
    while cap.isOpened() and frame_count < total_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Test traditional method
        start = time.time()
        result_trad, left_trad, right_trad = detector.process_frame(frame, use_neural=False)
        time_trad = time.time() - start
        
        # Test neural network
        start = time.time()
        result_nn, left_nn, right_nn = detector.process_frame(frame, use_neural=True)
        time_nn = time.time() - start
        
        # Store results
        results['traditional']['times'].append(time_trad)
        results['traditional']['lanes_detected'].append((left_trad is not None) + (right_trad is not None))
        results['traditional']['left'].append(left_trad is not None)
        results['traditional']['right'].append(right_trad is not None)
        
        results['neural']['times'].append(time_nn)
        results['neural']['lanes_detected'].append((left_nn is not None) + (right_nn is not None))
        results['neural']['left'].append(left_nn is not None)
        results['neural']['right'].append(right_nn is not None)
        
        results['frames'].append(frame_count)
        
        # Save comparison frame every 30 frames
        if frame_count % 30 == 0:
            # Create comparison visualization
            comparison = np.hstack([result_trad, result_nn])
            cv2.putText(comparison, "Traditional", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(comparison, "Neural Network", (result_trad.shape[1] + 10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Save frame
            os.makedirs("data/output/comparison_frames", exist_ok=True)
            cv2.imwrite(f"data/output/comparison_frames/frame_{frame_count:04d}.jpg", comparison)
        
        frame_count += 1
        progress.update(1)
        progress.set_postfix({
            'Trad': f'{len(results["traditional"]["lanes_detected"])}',
            'NN': f'{len(results["neural"]["lanes_detected"])}'
        })
    
    cap.release()
    progress.close()
    
    return results

def plot_comparison(results, video_name):
    """Plot comparison results"""
    
    if not results:
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Performance Comparison - {video_name}', fontsize=14)
    
    # 1. Processing Time
    ax1 = axes[0, 0]
    ax1.plot(results['frames'], np.array(results['traditional']['times'])*1000, 
             'b-', label='Traditional', alpha=0.7, linewidth=1)
    ax1.plot(results['frames'], np.array(results['neural']['times'])*1000, 
             'r-', label='Neural Network', alpha=0.7, linewidth=1)
    ax1.set_xlabel('Frame')
    ax1.set_ylabel('Time (ms)')
    ax1.set_title('Processing Time per Frame')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Average Time Bar Chart
    ax2 = axes[0, 1]
    avg_trad = np.mean(results['traditional']['times']) * 1000
    avg_nn = np.mean(results['neural']['times']) * 1000
    bars = ax2.bar(['Traditional', 'Neural'], [avg_trad, avg_nn], 
                   color=['blue', 'red'], alpha=0.7)
    ax2.set_ylabel('Time (ms)')
    ax2.set_title('Average Processing Time')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, val in zip(bars, [avg_trad, avg_nn]):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{val:.1f}ms', ha='center', va='bottom')
    
    # 3. Lane Detection Rate
    ax3 = axes[1, 0]
    # Calculate detection rate (frames with at least one lane)
    trad_detected = np.sum(np.array(results['traditional']['lanes_detected']) > 0)
    nn_detected = np.sum(np.array(results['neural']['lanes_detected']) > 0)
    total = len(results['frames'])
    
    bars = ax3.bar(['Traditional', 'Neural'], 
                   [trad_detected/total*100, nn_detected/total*100],
                   color=['blue', 'red'], alpha=0.7)
    ax3.set_ylabel('Detection Rate (%)')
    ax3.set_title('Lane Detection Rate')
    ax3.set_ylim(0, 100)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, val in zip(bars, [trad_detected/total*100, nn_detected/total*100]):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{val:.1f}%', ha='center', va='bottom')
    
    # 4. FPS Comparison
    ax4 = axes[1, 1]
    fps_trad = 1.0 / np.mean(results['traditional']['times'])
    fps_nn = 1.0 / np.mean(results['neural']['times'])
    bars = ax4.bar(['Traditional', 'Neural'], [fps_trad, fps_nn],
                   color=['blue', 'red'], alpha=0.7)
    ax4.set_ylabel('FPS')
    ax4.set_title('Frames Per Second')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, val in zip(bars, [fps_trad, fps_nn]):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{val:.1f}', ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Save figure
    os.makedirs("data/output", exist_ok=True)
    fig_path = f"data/output/comparison_{video_name.replace('.', '_')}.png"
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    print(f"\nComparison plot saved: {fig_path}")
    
    plt.show()
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    print(f"Total frames analyzed: {len(results['frames'])}")
    print(f"\nTraditional Method:")
    print(f"  Avg Time: {np.mean(results['traditional']['times'])*1000:.2f}ms")
    print(f"  FPS: {1.0/np.mean(results['traditional']['times']):.2f}")
    print(f"  Detection Rate: {trad_detected/total*100:.1f}%")
    print(f"\nNeural Network:")
    print(f"  Avg Time: {np.mean(results['neural']['times'])*1000:.2f}ms")
    print(f"  FPS: {1.0/np.mean(results['neural']['times']):.2f}")
    print(f"  Detection Rate: {nn_detected/total*100:.1f}%")
    print(f"\nSpeed Difference: {np.mean(results['neural']['times'])/np.mean(results['traditional']['times']):.2f}x slower")
    print(f"Detection Improvement: +{(nn_detected - trad_detected)/total*100:.1f}%")

def main():
    """Main function"""
    
    print("=" * 60)
    print("REAL-WORLD VIDEO COMPARISON")
    print("=" * 60)
    
    # Find videos to test
    video_dir = "data/real_videos"
    os.makedirs(video_dir, exist_ok=True)
    
    videos = []
    extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    for ext in extensions:
        import glob
        videos.extend(glob.glob(os.path.join(video_dir, f"*{ext}")))
    
    if not videos:
        print("\n⚠ No videos found in data/real_videos/")
        print("\nPlease add videos to test:")
        print("  1. Download from online sources")
        print("  2. Copy your own videos")
        print("  3. Record with your phone")
        print("\nOr use the test video:")
        videos = ["data/input/test_video.avi", "data/input/synthetic_road.mp4"]
        videos = [v for v in videos if os.path.exists(v)]
    
    if not videos:
        print("No videos available. Creating a test video...")
        from scripts.generate_test_video import generate_test_video
        generate_test_video()
        videos = ["data/input/test_video.avi"]
    
    print(f"\nFound {len(videos)} videos to test:")
    for v in videos:
        print(f"  - {os.path.basename(v)}")
    
    print("\n" + "=" * 60)
    
    # Process each video
    for video_path in videos:
        print(f"\nProcessing: {os.path.basename(video_path)}")
        results = analyze_video(video_path, max_frames=150)
        
        if results:
            plot_comparison(results, os.path.basename(video_path).split('.')[0])
    
    print("\n" + "=" * 60)
    print("COMPARISON COMPLETE!")
    print("Check data/output/ for comparison frames and plots")
    print("=" * 60)

if __name__ == "__main__":
    main()
