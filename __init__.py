"""
ComfyUI-MovieSpark - 自定义节点包
替代 proximaxai/comfyui-tacosai 的加密节点
"""

import sys
import os

# 添加nodes目录到路径
nodes_path = os.path.join(os.path.dirname(__file__), 'nodes')
if nodes_path not in sys.path:
    sys.path.insert(0, nodes_path)

from image_nodes import Image360Pack, ConvertRGBAtoRGB, SaveImageNoMetaData
from video_nodes import SaveVideoNoMetaData
from voice_nodes import (
    TacosAICharacterVoices,
    TacosAICharacterVoiceSave,
    TacosAIChatterBoxEngine,
    TacosAISaveAudio,
    TacosAIVoiceChanger
)
from caption_nodes import (
    TacosAIPersonIDExtractor,
    TacosAICaptionGenerator,
    TacosAIReferencePoseGenerator,
    TacosAIAudioSyncChecker,
    TacosAICameraControl,
    TacosAIPromptGenerator,
    MultiangleCameraNode
)

# 节点映射
NODE_CLASS_MAPPINGS = {
    # 图像节点
    "Image360Pack": Image360Pack,
    "ConvertRGBAtoRGB": ConvertRGBAtoRGB,
    "SaveImageNoMetaData": SaveImageNoMetaData,
    
    # 视频节点
    "SaveVideoNoMetaData": SaveVideoNoMetaData,
    
    # 语音节点
    "TacosAICharacterVoices": TacosAICharacterVoices,
    "TacosAICharacterVoiceSave": TacosAICharacterVoiceSave,
    "TacosAIChatterBoxEngine": TacosAIChatterBoxEngine,
    "TacosAISaveAudio": TacosAISaveAudio,
    "TacosAIVoiceChanger": TacosAIVoiceChanger,
    
    # 360度角色表专用节点
    "TacosAIPersonIDExtractor": TacosAIPersonIDExtractor,
    "TacosAICaptionGenerator": TacosAICaptionGenerator,
    "TacosAIReferencePoseGenerator": TacosAIReferencePoseGenerator,
    "TacosAIAudioSyncChecker": TacosAIAudioSyncChecker,
    "TacosAICameraControl": TacosAICameraControl,
    "TacosAIPromptGenerator": TacosAIPromptGenerator,
    "MultiangleCameraNode": MultiangleCameraNode,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "Image360Pack": "Image 360 Pack - MovieSpark",
    "ConvertRGBAtoRGB": "Convert RGBA to RGB - MovieSpark",
    "SaveImageNoMetaData": "Save Image (No Metadata) - MovieSpark",
    "SaveVideoNoMetaData": "Save Video (No Metadata) - MovieSpark",
    "TacosAICharacterVoices": "Character Voices - MovieSpark",
    "TacosAICharacterVoiceSave": "Character Voice Save - MovieSpark",
    "TacosAIChatterBoxEngine": "ChatterBox TTS Engine - MovieSpark",
    "TacosAISaveAudio": "Save Audio - MovieSpark",
    "TacosAIVoiceChanger": "Voice Changer - MovieSpark",
    "TacosAIPersonIDExtractor": "Person ID Extractor - MovieSpark",
    "TacosAICaptionGenerator": "Caption Generator - MovieSpark",
    "TacosAIReferencePoseGenerator": "Reference Pose Generator - MovieSpark",
    "TacosAIAudioSyncChecker": "Audio Sync Checker - MovieSpark",
    "TacosAICameraControl": "Camera Control - MovieSpark",
    "TacosAIPromptGenerator": "Prompt Generator - MovieSpark",
    "MultiangleCameraNode": "Multiangle Camera - MovieSpark",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
