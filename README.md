# ComfyUI-MovieSpark 部署说明

## 概述

`comfyui-moviespark` 是一个自定义节点包，用于替代 `proximaxai/comfyui-tacosai` 的加密节点。

## 安装步骤

### 方法一：手动复制（推荐）

1. 将 `comfyui-moviespark` 文件夹复制到ComfyUI的custom_nodes目录：
   ```
   从: d:\线上工作流\comfyui-moviespark
   到: E:\comfyUI配置\ComfyUI\custom_nodes\comfyui-moviespark
   ```

2. 重启ComfyUI服务

### 方法二：命令行复制

在PowerShell中执行：
```powershell
Copy-Item -Path "d:\线上工作流\comfyui-moviespark" -Destination "E:\comfyUI配置\ComfyUI\custom_nodes\comfyui-moviespark" -Recurse -Force
```

## 节点列表

### 图像节点
- **SaveImageNoMetaData** - 保存图像（无元数据）

### 视频节点
- **SaveVideoNoMetaData** - 保存视频（无元数据）

### 语音节点
- **TacosAICharacterVoices** - 角色声音选择
- **TacosAICharacterVoiceSave** - 角色声音保存
- **TacosAIChatterBoxEngine** - ChatterBox TTS引擎
- **TacosAIVoiceChanger** - 声音转换

### 360度角色表专用节点
- **TacosAIPersonIDExtractor** - 人物ID提取
- **TacosAICaptionGenerator** - 字幕生成
- **TacosAIReferencePoseGenerator** - 参考姿态生成
- **TacosAIAudioSyncChecker** - 音视频同步检查
- **TacosAICameraControl** - 相机控制
- **TacosAIPromptGenerator** - 提示词生成

## 工作流更新

所有11个工作流文件的 `aux_id` 识别码已从 `proximaxai/comfyui-tacosai` 更新为 `proximaxai/comfyui-moviespark`：

- Gallery-IMG-360-CharacterSheet V4-Release.json
- Gallery_FullBodyFront_V4_Release.json
- IMG-FAST_V4_Release.json
- IMG-PRO-PLUS_V4_Release.json
- IMG-PRO_V4_Release.json
- IMG-SHOT_V4_Release.json
- TACOS-VID-LF-V4-Release.json
- tacos-voice-design-V4-release.json
- tacos-voice-generate-V4-release.json
- tacos-voice-save-V4-release.json
- voice_test_v4.json

## 测试步骤

1. 启动ComfyUI服务
2. 访问 http://127.0.0.1:8188/
3. 加载任意一个工作流文件
4. 检查节点是否正常显示（应显示为 "MovieSpark" 后缀）
5. 运行工作流测试功能

## 注意事项

1. 部分节点（如语音合成）可能需要额外的依赖库
2. 音频处理节点需要 `librosa` 库支持
3. 视频处理节点需要 `imageio-ffmpeg` 库支持
4. 如果节点显示红色（缺失），请检查ComfyUI控制台输出

## 依赖安装

如果需要安装额外依赖，在ComfyUI目录下执行：
```bash
pip install librosa imageio imageio-ffmpeg soundfile
```
