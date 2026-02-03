import torch
import cv2
import numpy as np
import torch.nn.functional as F

class MidasRunner:
    def __init__(self, device="cpu"):
        self.device = device
        # Use MiDaS small for speed on CPU-friendly systems
        try:
            self.model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small").to(device).eval()
            self.transforms = torch.hub.load("intel-isl/MiDaS", "transforms").small_transform
        except Exception as e:
            raise RuntimeError("Failed to load MiDaS model. Ensure network access and correct torch version.") from e

    def infer(self, img_path):
        # read image (BGR -> RGB)
        img = cv2.imread(img_path)
        if img is None:
            raise RuntimeError(f"Failed to load image: {img_path}")
        img = img[:, :, ::-1]
        input_batch = self.transforms(img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            prediction = self.model(input_batch)
            prediction = F.interpolate(prediction.unsqueeze(1), size=img.shape[:2], mode="bilinear", align_corners=False).squeeze().cpu().numpy()
        # normalize to 0..1
        pred = (prediction - prediction.min()) / (prediction.max() - prediction.min() + 1e-8)
        return pred.astype("float32")
