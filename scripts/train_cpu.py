"""
CPU-Optimized Training Script for CULane Dataset
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
import time
from src.perception.lane_net_cpu import LaneNetCPU
from src.data.culane_loader import create_dataloader
from src.config import Config

def train():
    print("=" * 60)
    print("CPU-Optimized Training - Binary Segmentation")
    print("=" * 60)
    
    config = Config()
    device = torch.device('cpu')
    
    print(f"Device: {device}")
    print(f"Batch size: {config.BATCH_SIZE}")
    print(f"Epochs: {config.NUM_EPOCHS}")
    print(f"CULane path: {config.CULANE_PATH}")
    
    # Create dataloaders
    print("\nLoading training data...")
    train_loader = create_dataloader(config, split='train', max_samples=200)
    
    if train_loader is None or len(train_loader.dataset) == 0:
        print("Error: No training data loaded!")
        return
    
    print("\nLoading validation data...")
    val_loader = create_dataloader(config, split='val', max_samples=50)
    
    print(f"Training samples: {len(train_loader.dataset)}")
    if val_loader:
        print(f"Validation samples: {len(val_loader.dataset)}")
    else:
        print("No validation data available")
    
    # Model
    print("\nInitializing model...")
    model = LaneNetCPU(input_channels=3).to(device)
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total parameters: {total_params:,}")
    
    # Loss and optimizer
    criterion = nn.BCELoss()  # Binary cross entropy for single channel
    optimizer = optim.Adam(model.parameters(), lr=config.LEARNING_RATE)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)
    
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    
    print("\nStarting training...")
    print("=" * 60)
    start_time = time.time()
    
    for epoch in range(1, config.NUM_EPOCHS + 1):
        model.train()
        epoch_loss = 0
        batch_count = 0
        
        progress_bar = tqdm(train_loader, desc=f'Epoch {epoch}/{config.NUM_EPOCHS}')
        for batch in progress_bar:
            images = batch['image'].to(device)
            masks = batch['mask'].to(device)
            
            # Forward pass
            outputs = model(images)
            
            # Ensure outputs and masks have same shape
            # outputs: [batch, 1, H, W], masks: [batch, 1, H, W]
            loss = criterion(outputs, masks)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            batch_count += 1
            progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})
        
        avg_loss = epoch_loss / batch_count if batch_count > 0 else 0
        
        # Validation
        if val_loader and epoch % 5 == 0:
            model.eval()
            val_loss = 0
            val_count = 0
            with torch.no_grad():
                for batch in val_loader:
                    images = batch['image'].to(device)
                    masks = batch['mask'].to(device)
                    outputs = model(images)
                    loss = criterion(outputs, masks)
                    val_loss += loss.item()
                    val_count += 1
            
            val_avg = val_loss / val_count if val_count > 0 else 0
            print(f"Epoch {epoch}: Train Loss={avg_loss:.4f}, Val Loss={val_avg:.4f}")
        else:
            print(f"Epoch {epoch}/{config.NUM_EPOCHS} - Loss: {avg_loss:.4f}")
        
        # Update scheduler
        scheduler.step()
        
        # Save checkpoint every 5 epochs
        if epoch % 5 == 0:
            checkpoint_path = os.path.join(config.MODEL_DIR, f'checkpoint_epoch_{epoch}.pth')
            torch.save(model.state_dict(), checkpoint_path)
            print(f"Saved checkpoint: {checkpoint_path}")
    
    total_time = time.time() - start_time
    
    # Save final model
    final_path = os.path.join(config.MODEL_DIR, 'lane_net_final.pth')
    torch.save(model.state_dict(), final_path)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Total time: {total_time:.2f}s")
    print(f"Model saved to: {final_path}")
    
    # Also save as optimized model for detector
    optimized_path = os.path.join(config.MODEL_DIR, 'lane_net_optimized.pth')
    torch.save(model.state_dict(), optimized_path)
    print(f"Optimized model saved to: {optimized_path}")
    print("=" * 60)

if __name__ == "__main__":
    train()
