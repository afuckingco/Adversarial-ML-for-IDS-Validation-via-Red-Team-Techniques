# Aksara Bali OCR

A simple CNN for Aksara Bali character recognition (demonstration with dummy data).

## Contents
- `src/train.py`: Training script for a simple CNN on synthetic Aksara Bali character images
- `requirements.txt`: Python dependencies (torch, torchvision, flask, pillow, numpy)

## Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Train the model: `python src/train.py`
3. The trained model will be saved to `../model/aksara_bali_cnn.pth`

## Notes
This is a demonstration model using randomly generated images. For a real OCR system, you would need a labeled dataset of Aksara Bali characters.