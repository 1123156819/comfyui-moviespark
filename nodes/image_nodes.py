"""
图像保存节点 - 无元数据保存
替代 proximaxai/comfyui-tacosai 的 SaveImageNoMetaData 节点
"""

import os
import json
import torch
import zipfile
import numpy as np
from PIL import Image
import folder_paths
from comfy.cli_args import args

class Image360Pack:
    """360度图像打包节点"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", ),
                "person_id": ("STRING", {"default": "person_001"}),
                "start_angle": ("INT", {"default": 1, "min": 0, "max": 360, "step": 1}),
                "total_images": ("INT", {"default": 8, "min": 1, "max": 36, "step": 1}),
                "angle_step": ("INT", {"default": 45, "min": 1, "max": 360, "step": 1}),
                "camera_height": (["eye", "low", "high"], {"default": "eye"}),
                "format": (["WEBP", "PNG", "JPEG"], {"default": "WEBP"}),
                "quality": ("INT", {"default": 85, "min": 1, "max": 100, "step": 1}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    OUTPUT_NODE = True
    FUNCTION = "pack_images"
    CATEGORY = "MovieSpark/360Character"

    def pack_images(self, images, person_id="person_001", start_angle=1, total_images=8, angle_step=45, camera_height="eye", format="WEBP", quality=85):
        """将360度图像打包成zip文件"""
        # 创建输出目录
        output_dir = folder_paths.get_output_directory()
        pack_dir = os.path.join(output_dir, "tacosai-360-packs")
        os.makedirs(pack_dir, exist_ok=True)
        
        # 生成打包文件名
        zip_filename = f"{person_id}_360pack.zip"
        zip_path = os.path.join(pack_dir, zip_filename)
        
        # 创建manifest
        manifest = {
            "person_id": person_id,
            "start_angle": start_angle,
            "total_images": total_images,
            "angle_step": angle_step,
            "camera_height": camera_height,
            "format": format,
            "quality": quality,
            "images": []
        }
        
        # 打包图像
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for idx, image in enumerate(images[:total_images]):
                # 计算角度
                angle = start_angle + (idx * angle_step)
                
                # 转换tensor为图像
                i = 255.0 * image.cpu().numpy()
                img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
                
                # 生成文件名
                img_filename = f"{person_id}_{angle:03d}.{format.lower()}"
                
                # 保存到zip
                if format == "WEBP":
                    import io
                    buffer = io.BytesIO()
                    img.save(buffer, format="WEBP", quality=quality)
                    buffer.seek(0)
                    zf.writestr(img_filename, buffer.read())
                elif format == "PNG":
                    import io
                    buffer = io.BytesIO()
                    img.save(buffer, format="PNG", optimize=True)
                    buffer.seek(0)
                    zf.writestr(img_filename, buffer.read())
                elif format == "JPEG":
                    import io
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=quality)
                    buffer.seek(0)
                    zf.writestr(img_filename, buffer.read())
                
                # 添加到manifest
                manifest["images"].append({
                    "filename": img_filename,
                    "angle": angle,
                    "camera_height": camera_height
                })
        
        # 保存manifest
        manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False)
        
        return (zip_path, manifest_json)


class ConvertRGBAtoRGB:
    """将RGBA图像转换为RGB格式"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE", ),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "convert"
    CATEGORY = "MovieSpark/Image"

    def convert(self, image):
        """转换RGBA为RGB"""
        # 如果图像有alpha通道，移除它
        if image.shape[-1] == 4:
            # 取前3个通道（RGB）
            return (image[:, :, :, :3],)
        return (image,)


class SaveImageNoMetaData:
    """保存图像但不包含任何元数据"""
    
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", ),
                "filename_prefix": ("STRING", {"default": "tacosai-img"}),
                "format": (["WEBP", "PNG", "JPEG"], {"default": "WEBP"}),
                "quality": ("INT", {"default": 92, "min": 1, "max": 100, "step": 1}),
                "save_metadata": ("BOOLEAN", {"default": False}),
                "overwrite": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    OUTPUT_NODE = True
    FUNCTION = "save_images"
    CATEGORY = "MovieSpark/Image"

    def save_images(self, images, filename_prefix="tacosai-img", format="WEBP", quality=92, save_metadata=False, overwrite=True):
        """保存图像但不包含元数据"""
        results = []
        
        for image in images:
            # 转换tensor为numpy数组
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            # 生成文件名
            full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
                filename_prefix, self.output_dir, img.width, img.height
            )
            
            # 生成唯一文件名
            if overwrite:
                file = f"{filename}.webp" if format == "WEBP" else f"{filename}.{format.lower()}"
            else:
                file = f"{filename}_{counter:04}.webp" if format == "WEBP" else f"{filename}_{counter:04}.{format.lower()}"
            
            # 确保输出目录存在
            os.makedirs(full_output_folder, exist_ok=True)
            
            # 保存图像（不包含元数据）
            filepath = os.path.join(full_output_folder, file)
            
            if format == "WEBP":
                img.save(filepath, format="WEBP", quality=quality)
            elif format == "PNG":
                img.save(filepath, format="PNG", optimize=True)
            elif format == "JPEG":
                # JPEG需要RGB模式
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(filepath, format="JPEG", quality=quality)
            
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
        
        return {"ui": {"images": results}, "result": (images,)}
