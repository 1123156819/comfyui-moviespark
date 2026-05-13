"""
语音相关节点
替代 proximaxai/comfyui-tacosai 的语音相关节点
"""

import os
import torch
import folder_paths

class TacosAICharacterVoices:
    """角色声音选择节点"""
    
    @classmethod
    def INPUT_TYPES(s):
        # 获取声音文件目录
        voice_dir = os.path.join(folder_paths.get_output_directory(), "tacosai-voice-character")
        os.makedirs(voice_dir, exist_ok=True)
        
        # 扫描可用的声音文件
        voice_files = []
        if os.path.exists(voice_dir):
            for f in os.listdir(voice_dir):
                if f.endswith('.zip') or f.endswith('.wav') or f.endswith('.pt'):
                    voice_files.append(f)
        
        # 添加默认选项
        default_voices = [
            "en-Alice_woman.zip",
            "system_morganfreeman.zip",
            "zh-default_male.zip",
            "zh-default_female.zip"
        ]
        
        all_voices = list(set(voice_files + default_voices))
        all_voices.sort()
        
        return {
            "required": {
                "voice_file": (all_voices, {"default": "en-Alice_woman.zip"}),
                "output_path": ("STRING", {"default": "tacosai-voice-character"}),
                "action": (["Upload Voice Zip", "Load Voice", "Preview Voice"], {"default": "Upload Voice Zip"}),
            },
        }

    RETURN_TYPES = ("VOICE_CLONE_PROMPT",)
    FUNCTION = "load_voice"
    CATEGORY = "MovieSpark/Voice"

    def load_voice(self, voice_file, output_path="tacosai-voice-character", action="Upload Voice Zip"):
        """加载角色声音"""
        # 构建声音文件路径
        voice_path = os.path.join(folder_paths.get_output_directory(), output_path, voice_file)
        
        # 创建声音克隆提示
        voice_prompt = {
            "voice_file": voice_file,
            "voice_path": voice_path,
            "output_path": output_path,
            "action": action
        }
        
        return (voice_prompt,)


class TacosAICharacterVoiceSave:
    """角色声音保存节点"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "voice_clone_prompt": ("VOICE_CLONE_PROMPT", ),
                "character_name": ("STRING", {"default": "my_character"}),
                "reference_text": ("STRING", {"default": "", "multiline": True}),
                "save_model": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "audio": ("AUDIO", ),
            }
        }

    RETURN_TYPES = ("STRING",)
    OUTPUT_NODE = True
    FUNCTION = "save_voice"
    CATEGORY = "MovieSpark/Voice"

    def save_voice(self, voice_clone_prompt, character_name="my_character", reference_text="", save_model=True, audio=None):
        """保存角色声音"""
        # 构建保存路径
        output_dir = folder_paths.get_output_directory()
        voice_dir = os.path.join(output_dir, "tacosai-voice-character")
        os.makedirs(voice_dir, exist_ok=True)
        
        # 生成保存文件名
        save_path = os.path.join(voice_dir, f"{character_name}.pt")
        
        return (save_path,)


class TacosAIChatterBoxEngine:
    """ChatterBox TTS语音合成引擎节点"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "language": (["English", "Chinese", "Spanish", "Japanese", "Korean"], {"default": "English"}),
                "device": (["cuda", "cpu", "auto"], {"default": "cuda"}),
                "speed": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 2.0, "step": 0.1}),
                "temperature": ("FLOAT", {"default": 0.8, "min": 0.1, "max": 1.5, "step": 0.1}),
                "top_p": ("FLOAT", {"default": 0.8, "min": 0.1, "max": 1.0, "step": 0.05}),
                "filler_pattern": ("STRING", {"default": "hmm ,, {seg} hmm ,,"}),
            },
        }

    RETURN_TYPES = ("TTS_ENGINE",)
    FUNCTION = "init_engine"
    CATEGORY = "MovieSpark/Voice"

    def init_engine(self, language="English", device="cuda", speed=0.5, temperature=0.8, top_p=0.8, filler_pattern="hmm ,, {seg} hmm ,,"):
        """初始化TTS引擎"""
        engine_config = {
            "language": language,
            "device": device,
            "speed": speed,
            "temperature": temperature,
            "top_p": top_p,
            "filler_pattern": filler_pattern,
            "engine_type": "chatterbox"
        }
        
        return (engine_config,)


class TacosAISaveAudio:
    """保存音频节点"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO", ),
                "filename_prefix": ("STRING", {"default": "tacosai-audio"}),
                "format": (["voice", "wav", "mp3", "flac", "bgm"], {"default": "voice"}),
                "save_metadata": ("BOOLEAN", {"default": False}),
                "overwrite": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    OUTPUT_NODE = True
    FUNCTION = "save_audio"
    CATEGORY = "MovieSpark/Voice"

    def _extract_audio(self, audio):
        if hasattr(audio, 'get_components'):
            components = audio.get_components()
            return components.waveform, getattr(components, 'sample_rate', 22050)
        if hasattr(audio, 'waveform'):
            return audio.waveform, getattr(audio, 'sample_rate', 22050)
        if isinstance(audio, dict):
            return audio.get("waveform", None), audio.get("sample_rate", 22050)
        return audio, 22050

    def save_audio(self, audio, filename_prefix="tacosai-audio", format="voice", save_metadata=False, overwrite=True):
        import soundfile as sf
        
        waveform, sample_rate = self._extract_audio(audio)
        
        if waveform is None:
            raise ValueError("No audio waveform provided")
        
        # 转换为numpy
        if isinstance(waveform, torch.Tensor):
            audio_np = waveform.cpu().numpy()
        else:
            audio_np = waveform
        
        # 构建保存路径
        output_dir = folder_paths.get_output_directory()
        audio_dir = os.path.join(output_dir, "tacosai-audio")
        os.makedirs(audio_dir, exist_ok=True)
        
        # 生成文件名
        file = f"{filename_prefix}.{format}" if overwrite else f"{filename_prefix}_{int(torch.rand()*10000):04d}.{format}"
        filepath = os.path.join(audio_dir, file)
        
        # 保存音频
        sf.write(filepath, audio_np, sample_rate, format=format)
        
        return (audio,)


class TacosAIVoiceChanger:
    """声音转换节点"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO", ),
                "pitch_shift": ("INT", {"default": 2, "min": -12, "max": 12, "step": 1}),
                "formant_shift": ("INT", {"default": 60, "min": 0, "max": 200, "step": 1}),
                "method": (["smart", "linear", "logarithmic"], {"default": "smart"}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    FUNCTION = "change_voice"
    CATEGORY = "MovieSpark/Voice"

    def _extract_audio(self, audio):
        if hasattr(audio, 'get_components'):
            components = audio.get_components()
            return components.waveform, getattr(components, 'sample_rate', 22050)
        if hasattr(audio, 'waveform'):
            return audio.waveform, getattr(audio, 'sample_rate', 22050)
        if isinstance(audio, dict):
            return audio.get("waveform", None), audio.get("sample_rate", 22050)
        return audio, 22050

    def change_voice(self, audio, pitch_shift=2, formant_shift=60, method="smart"):
        waveform, sample_rate = self._extract_audio(audio)
        
        if waveform is None:
            raise ValueError("No audio waveform provided")
        
        return (audio,)
