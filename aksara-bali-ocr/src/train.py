#!/usr/bin/env python3
"""
Train a simple CNN for Aksara Bali OCR (dummy data for demonstration).
"""

import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image, ImageDraw

# Dummy dataset: generate random images with patterns (to mimic characters)
class AksaraBaliDataset(Dataset):
    def __init__(self, num_samples=1000, image_size=(32, 32), num_classes=10, transform=None):
        self.num_samples = num_samples
        self.image_size = image_size
        self.num_classes = num_classes
        self.transform = transform
        # Generate random labels
        self.labels = np.random.randint(0, num_classes, size=num_samples)
        # Generate random images (for simplicity, we'll create images with random patterns)
        self.images = [self._generate_random_image() for _ in range(num_samples)]

    def _generate_random_image(self):
        # Create a blank image
        img = Image.new('L', self.image_size, color=255)  # White background
        draw = ImageDraw.Draw(img)
        # Draw some random shapes and lines to mimic characters
        for _ in range(5):
            x0 = np.random.randint(0, self.image_size[0])
            y0 = np.random.randint(0, self.image_size[1])
            x1 = np.random.randint(0, self.image_size[0])
            y1 = np.random.randint(0, self.image_size[1])
            draw.line([(x0, y0), (x1, y1)], fill=0, width=2)  # Black line
            # Draw a random rectangle
            rect_size = np.random.randint(2, 8)
            draw.rectangle([x0, y0, x0+rect_size, y0+rect_size], outline=0, fill=0)
        return img

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        img = self.images[idx]
        label = self.labels[idx]
        if self.transform:
            img = self.transform(img)
        else:
            # Convert to tensor and normalize
            img = torch.tensor(np.array(img), dtype=torch.float32).unsqueeze(0) / 255.0
        return img, label

# Simple CNN model assuming input size 32x32
class SimpleCNN(nn.Module):
    def __init__(self, num_classes=10):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        # After two pools: 32 -> 16 -> 8
        self.fc1 = nn.Linear(32 * 8 * 8, 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

if __name__ == '__main__':
    # Parameters
    image_size = (32, 32)
    num_classes = 10
    batch_size = 32
    num_epochs = 5  # Keep it short for demo but enough to see learning

    # Define transforms
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    # Create dataset and dataloader
    dataset = AksaraBaliDataset(num_samples=400, image_size=image_size, num_classes=num_classes, transform=transform)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Initialize model, loss, optimizer
    model = SimpleCNN(num_classes=num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Training loop
    model.train()
    for epoch in range(num_epochs):
        running_loss = 0.0
        correct = 0
        total = 0
        for i, (inputs, labels) in enumerate(dataloader):
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            if i % 10 == 9:  # Print every 10 mini-batches
                print(f'Epoch [{epoch+1}/{num_epochs}], Step [{i+1}/{len(dataloader)}], Loss: {running_loss/10:.4f}, Acc: {100*correct/total:.2f}%')
                running_loss = 0.0
                correct = 0
                total = 0

    print('Training finished.')

    # Save the model
    os.makedirs('../model', exist_ok=True)
    torch.save(model.state_dict(), '../model/aksara_bali_cnn.pth')
    print('Model saved to ../model/aksara_bali_cnn.pth')