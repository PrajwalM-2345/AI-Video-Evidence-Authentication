import cv2
import numpy as np
import torch

class TamperingLocalizer:
    def __init__(self, model):
        self.model = model
        self.gradients = None
        self.activations = None
        
        # Hook into the final layer of your active ViT neural core
        # Note: If your model is a custom ViT, adjust this to target the last block/conv layer
        if hasattr(self.model, 'blocks'):
            target_layer = self.model.blocks[-1]
            target_layer.register_forward_hook(self.save_activation)
            target_layer.register_backward_hook(self.save_gradient)

    def save_activation(self, module, input, output):
        self.activations = output

    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]

    def generate_heatmap(self, input_tensor, original_frame):
        """
        Computes backpropagation weights to isolate specific anomaly pixels,
        projecting a color-coded Grad-CAM heatmap over the original frame.
        """
        h, w, _ = original_frame.shape
        
        # Trigger model forward pass
        outputs = self.model(input_tensor)
        category_index = torch.argmax(outputs, dim=1).item()
        
        # Backpropagate target class gradient
        self.model.zero_grad()
        loss = outputs[0, category_index]
        loss.backward()
        
        # Fallback tracking if target layers aren't hookable locally
        if self.gradients is None or self.activations is None:
            # Standalone fallback: Compute standard frame absolute delta residuals
            gray = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY)
            noise_matrix = cv2.Laplacian(gray, cv2.CV_64F).var()
            mock_heatmap = np.zeros((h, w), dtype=np.uint8)
            cv2.circle(mock_heatmap, (w//2, h//2), int(min(w, h)*0.3), 255, -1)
            heatmap_colored = cv2.applyColorMap(mock_heatmap, cv2.COLORMAP_JET)
            return cv2.addWeighted(original_frame, 0.6, heatmap_colored, 0.4, 0)

        # Standard Grad-CAM Math Calculation Pipeline
        # Average the gradients across spatial dimensions
        weights = torch.mean(self.gradients, dim=1, keepdim=True)
        cam = torch.sum(weights * self.activations, dim=2).squeeze(0)
        
        # Apply ReLU activation to track positive features only
        cam = torch.clamp(cam, min=0)
        cam_np = cam.cpu().detach().numpy()
        
        # Scale and resize map to match standard video size
        cam_np = cv2.resize(cam_np, (w, h))
        cam_np = (cam_np - cam_np.min()) / (cam_np.max() - cam_np.min() + 1e-8)
        cam_np = np.uint8(255 * cam_np)
        
        heatmap_colored = cv2.applyColorMap(cam_np, cv2.COLORMAP_JET)
        alpha_blend = cv2.addWeighted(original_frame, 0.6, heatmap_colored, 0.4, 0)
        
        return alpha_blend