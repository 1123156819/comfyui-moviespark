"""
视频保存节点 - 无元数据保存
替代 proximaxai/comfyui-tacosai 的 SaveVideoNoMetaData 节点
支持 ComfyUI 0.21+ 的 VideoFromComponents 类型
"""

import os
import subprocess
import torch
import numpy as np
import folder_paths
from fractions import Fraction

class SaveVideoNoMetaData:
    
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "video": ("VIDEO", ),
                "filename_prefix": ("STRING", {"default": "tacosai-video"}),
                "format": (["auto", "mp4", "webm", "gif"], {"default": "auto"}),
                "codec": (["auto", "h264", "vp9", "gif"], {"default": "auto"}),
                "save_metadata": ("BOOLEAN", {"default": False}),
                "overwrite": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    OUTPUT_NODE = True
    FUNCTION = "save_video"
    CATEGORY = "MovieSpark/Video"

    def _extract_tensor(self, video):
        video_type = type(video).__name__
        
        if hasattr(video, 'get_components'):
            components = video.get_components()
            return components.images, getattr(components, 'frame_rate', Fraction(24))
        
        if hasattr(video, 'samples'):
            return video.samples, Fraction(24)
        if hasattr(video, 'frame'):
            return video.frame, Fraction(24)
        
        if isinstance(video, dict):
            if "samples" in video:
                return video["samples"], Fraction(24)
            if "frame" in video:
                return video["frame"], Fraction(24)
            for key in video:
                if isinstance(video[key], torch.Tensor):
                    return video[key], Fraction(24)
            raise ValueError(f"无法从视频字典中提取数据: {video.keys()}")
        
        if isinstance(video, torch.Tensor):
            return video, Fraction(24)
        
        raise ValueError(f"不支持的视频类型: {type(video)} (类名: {video_type})")

    def _save_as_mp4(self, video_uint8, filepath, fps):
        import subprocess
        h, w = video_uint8.shape[1], video_uint8.shape[2]
        cmd = [
            'ffmpeg', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
            '-s', f'{w}x{h}', '-pix_fmt', 'rgb24',
            '-r', str(float(fps)), '-i', '-',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
            '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
            filepath
        ]
        subprocess.run(cmd, input=video_uint8.tobytes(), check=True,
                       capture_output=True)

    def _save_as_webm(self, video_uint8, filepath, fps):
        import subprocess
        h, w = video_uint8.shape[1], video_uint8.shape[2]
        cmd = [
            'ffmpeg', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
            '-s', f'{w}x{h}', '-pix_fmt', 'rgb24',
            '-r', str(float(fps)), '-i', '-',
            '-c:v', 'libvpx-vp9', '-crf', '30', '-b:v', '0',
            '-pix_fmt', 'yuv420p', filepath
        ]
        subprocess.run(cmd, input=video_uint8.tobytes(), check=True,
                       capture_output=True)

    def _save_as_gif(self, video_uint8, filepath, fps):
        from PIL import Image
        frames = [Image.fromarray(frame) for frame in video_uint8]
        duration = int(1000 / float(fps))
        frames[0].save(filepath, save_all=True, append_images=frames[1:],
                       duration=duration, loop=0)

    def save_video(self, video, filename_prefix="tacosai-video", format="auto", codec="auto", save_metadata=False, overwrite=True):
        video_tensor, fps = self._extract_tensor(video)
        
        video_np = video_tensor.cpu().numpy()
        
        if video_np.ndim == 5:
            video_np = video_np[0].transpose(0, 2, 3, 1)
        elif video_np.ndim == 4:
            if video_np.shape[1] <= 4:
                video_np = video_np.transpose(0, 2, 3, 1)
        
        video_uint8 = np.clip(video_np * 255, 0, 255).astype(np.uint8)
        
        height, width = video_uint8.shape[1], video_uint8.shape[2]
        
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, width, height
        )
        
        if format == "auto":
            if codec == "gif":
                fmt = "gif"
            elif codec in ("h264", "vp9"):
                fmt = "mp4" if codec == "h264" else "webm"
            else:
                fmt = "mp4"
        else:
            fmt = format
        
        suffix = f".{fmt}"
        if overwrite:
            file = f"{filename}{suffix}"
        else:
            file = f"{filename}_{counter:04}{suffix}"
        
        os.makedirs(full_output_folder, exist_ok=True)
        filepath = os.path.join(full_output_folder, file)
        
        if fmt == "gif":
            self._save_as_gif(video_uint8, filepath, fps)
        elif fmt == "webm":
            try:
                self._save_as_webm(video_uint8, filepath, fps)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self._save_as_gif(video_uint8, filepath.replace('.webm', '.gif'), fps)
                file = file.replace('.webm', '.gif')
        else:
            try:
                self._save_as_mp4(video_uint8, filepath, fps)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self._save_as_gif(video_uint8, filepath.replace('.mp4', '.gif'), fps)
                file = file.replace('.mp4', '.gif')
        
        last_frame = torch.from_numpy(video_uint8[-1].astype(np.float32) / 255.0)
        
        results = [{
            "filename": file,
            "subfolder": subfolder,
            "type": self.type
        }]
        
        return {"ui": {"images": results}, "result": (last_frame.unsqueeze(0),)}
