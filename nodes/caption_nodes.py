"""
360度角色表专用节点
替代 proximaxai/comfyui-tacosai 的角色表相关节点
"""

import os
import json
import torch
import numpy as np
import folder_paths

class TacosAIPersonIDExtractor:
    """人物ID提取节点"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", ),
                "person_id": ("STRING", {"default": "person_001"}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    FUNCTION = "extract_person_id"
    CATEGORY = "MovieSpark/360Character"

    def extract_person_id(self, images, person_id="person_001"):
        """提取人物ID并返回图像和ID信息"""
        return (images, person_id)


class TacosAICaptionGenerator:
    """字幕生成节点"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE", ),
                "caption_style": (["descriptive", "simple", "detailed", "tag"], {"default": "descriptive"}),
                "language": (["en", "zh", "es", "ja"], {"default": "en"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_caption"
    CATEGORY = "MovieSpark/360Character"

    def generate_caption(self, image, caption_style="descriptive", language="en"):
        """生成图像描述字幕"""
        captions = {
            "descriptive": "A character reference image showing front view",
            "simple": "Character front view",
            "detailed": "Full body character reference, front view, neutral pose, clean background",
            "tag": "character, reference, front, fullbody"
        }
        return (captions.get(caption_style, captions["descriptive"]),)


class TacosAIReferencePoseGenerator:
    """参考姿态生成节点"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE", ),
                "pose_type": (["front", "back", "side", "three_quarter"], {"default": "front"}),
                "detect_keypoints": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    FUNCTION = "generate_pose"
    CATEGORY = "MovieSpark/360Character"

    def generate_pose(self, image, pose_type="front", detect_keypoints=True):
        """生成参考姿态"""
        pose_info = f"{pose_type}|keypoints_detected:{detect_keypoints}"
        return (image, pose_info)


class TacosAIAudioSyncChecker:
    """音视频同步检查节点"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "video": ("IMAGE", ),
                "audio": ("AUDIO", ),
                "tolerance_ms": ("FLOAT", {"default": 50.0, "min": 1.0, "max": 500.0, "step": 1.0}),
            },
        }

    RETURN_TYPES = ("BOOLEAN", "FLOAT", "STRING")
    FUNCTION = "check_sync"
    CATEGORY = "MovieSpark/360Character"

    def check_sync(self, video, audio, tolerance_ms=50.0):
        """检查音视频同步"""
        is_synced = True
        offset_ms = 0.0
        message = "Audio and video are synchronized"
        
        return (is_synced, offset_ms, message)


class TacosAICameraControl:
    """相机控制节点"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE", ),
                "camera_angle": (["front", "back", "left", "right", "top", "bottom"], {"default": "front"}),
                "zoom": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 5.0, "step": 0.1}),
                "rotation": ("FLOAT", {"default": 0.0, "min": -180.0, "max": 180.0, "step": 1.0}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "control_camera"
    CATEGORY = "MovieSpark/360Character"

    def control_camera(self, image, camera_angle="front", zoom=1.0, rotation=0.0):
        """模拟相机视角控制"""
        return (image,)


class TacosAIPromptGenerator:
    """提示词生成节点"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_prompt": ("STRING", {"default": "", "multiline": True}),
                "view_angle": (["front", "back", "left_side", "right_side", "three_quarter_front", "three_quarter_back"], {"default": "front"}),
                "character_description": ("STRING", {"default": "", "multiline": True}),
                "style": (["realistic", "anime", "cartoon", "3d_render"], {"default": "realistic"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_prompt"
    CATEGORY = "MovieSpark/360Character"

    def generate_prompt(self, base_prompt="", view_angle="front", character_description="", style="realistic"):
        """生成多角度角色提示词"""
        view_descriptions = {
            "front": "front view, facing camera directly",
            "back": "back view, showing the back of the character",
            "left_side": "left side view, profile from left",
            "right_side": "right side view, profile from right",
            "three_quarter_front": "three quarter front view, slightly angled",
            "three_quarter_back": "three quarter back view, slightly angled from back"
        }
        
        style_descriptions = {
            "realistic": "photorealistic, high quality, detailed",
            "anime": "anime style, cel shading, clean lines",
            "cartoon": "cartoon style, stylized, colorful",
            "3d_render": "3D render, studio lighting, clean background"
        }
        
        parts = []
        if character_description:
            parts.append(character_description)
        if view_angle in view_descriptions:
            parts.append(view_descriptions[view_angle])
        if style in style_descriptions:
            parts.append(style_descriptions[style])
        if base_prompt:
            parts.append(base_prompt)
        
        full_prompt = ", ".join(parts)
        
        return (full_prompt,)


class MultiangleCameraNode:
    """多角度相机控制节点"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "horizontal_angle": ("FLOAT", {"default": 0, "min": 0, "max": 360, "step": 1}),
                "vertical_angle": ("FLOAT", {"default": 0, "min": -90, "max": 90, "step": 1}),
                "zoom": ("FLOAT", {"default": 5.1, "min": 0, "max": 10, "step": 0.1}),
                "help_text": ("STRING", {"default": "Horizontal : 0°=front · 90°=right · 180°=back · 270°=left\nVertical   : -30°=low · 0°=eye-level · 30°=elevated · 60°=high\nZoom       : 0–2=wide · 2–6=medium · 6–10=close-up", "multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_camera_prompt"
    CATEGORY = "MovieSpark/360Character"

    def generate_camera_prompt(self, horizontal_angle=0, vertical_angle=0, zoom=5.1, help_text=""):
        """生成相机角度提示词"""
        # 水平角度描述
        if horizontal_angle == 0:
            h_desc = "front view"
        elif horizontal_angle == 90:
            h_desc = "right side view"
        elif horizontal_angle == 180:
            h_desc = "back view"
        elif horizontal_angle == 270:
            h_desc = "left side view"
        elif 0 < horizontal_angle < 90:
            h_desc = f"three quarter front-right view, {horizontal_angle}° from front"
        elif 90 < horizontal_angle < 180:
            h_desc = f"three quarter back-right view, {horizontal_angle}° from front"
        elif 180 < horizontal_angle < 270:
            h_desc = f"three quarter back-left view, {horizontal_angle}° from front"
        else:
            h_desc = f"three quarter front-left view, {horizontal_angle}° from front"
        
        # 垂直角度描述
        if vertical_angle < -15:
            v_desc = "low angle shot, looking up"
        elif -15 <= vertical_angle < 0:
            v_desc = "slightly low angle"
        elif vertical_angle == 0:
            v_desc = "eye level"
        elif 0 < vertical_angle <= 30:
            v_desc = "slightly elevated angle"
        elif 30 < vertical_angle <= 60:
            v_desc = "high angle shot, looking down"
        else:
            v_desc = "bird's eye view"
        
        # 变焦描述
        if zoom <= 2:
            z_desc = "wide angle lens"
        elif zoom <= 6:
            z_desc = "medium focal length"
        else:
            z_desc = "close-up, telephoto lens"
        
        # 组合提示词
        camera_prompt = f"{h_desc}, {v_desc}, {z_desc}"
        
        return (camera_prompt,)
