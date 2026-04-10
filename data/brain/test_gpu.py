import torch
import whisper

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU device: {torch.cuda.get_device_name(0)}")
    print(f"CUDA version: {torch.version.cuda}")
    
    # Test Whisper on GPU
    print("\nLoading Whisper on GPU...")
    model = whisper.load_model("medium", device="cuda")
    print("Whisper loaded on GPU!")
else:
    print("CUDA not available - Whisper will use CPU")
