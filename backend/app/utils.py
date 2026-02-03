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
