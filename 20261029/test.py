import torch
print("PyTorch:", torch.__version__)
print("빌드 CUDA:",torch.version.cuda)
print("CUDA 사용 가능", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    props = torch.cuda.get_device_properties(0)
    print("VRAM(GB):", round(props.total_memory / 1024**3, 1))