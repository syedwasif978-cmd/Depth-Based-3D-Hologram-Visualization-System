import aiofiles
import cv2
import numpy as np

async def save_upload_file(upload_file, dest_path):
    async with aiofiles.open(dest_path, 'wb') as out:
        content = await upload_file.read()
        await out.write(content)
    return dest_path


def save_depth_png(depth_np, path):
    # depth_np expected normalized 0..1 float32
    depth_8 = (depth_np * 255).astype("uint8")
    # save as single-channel PNG
    cv2.imwrite(path, depth_8)
    return path


# --- Postprocessing helpers ---
def apply_edge_sharpen(depth_np, weight: float = 0.25):
    """Enhance edges detected on the depth map by adding a scaled edge map to the depth.
    depth_np: normalized float32 0..1
    weight: influence of edges to add
    returns: adjusted depth (clipped 0..1)
    """
    depth_8 = (depth_np * 255).astype("uint8")
    edges = cv2.Canny(depth_8, 50, 150)
    edges_norm = edges.astype("float32") / 255.0
    depth_out = depth_np + weight * edges_norm
    depth_out = np.clip(depth_out, 0.0, 1.0)
    return depth_out


def apply_background_blur_to_image(image_path, depth_np, out_path, blur_sigma: int = 15, depth_threshold: float = 0.45):
    """Blur regions detected as background based on depth map and save processed image to out_path.
    depth_threshold: pixels with depth < threshold are considered background (far)
    """
    img = cv2.imread(image_path)
    if img is None:
        raise RuntimeError(f"Failed to load image for background blur: {image_path}")
    # ensure depth map matches image size
    if depth_np.shape[:2] != img.shape[:2]:
        depth_resized = cv2.resize(depth_np, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)
    else:
        depth_resized = depth_np

    # background mask: where depth is low (farther)
    mask_bg = (depth_resized < depth_threshold).astype("uint8")
    blurred = cv2.GaussianBlur(img, (0,0), blur_sigma)

    mask_3 = np.repeat(mask_bg[:, :, np.newaxis], 3, axis=2)
    out = np.where(mask_3 == 1, blurred, img)
    cv2.imwrite(out_path, out)
    return out_path
