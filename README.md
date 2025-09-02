# YouTube Playlist Organizer

一个智能的 YouTube 播放列表管理和整理工具，基于内容分析自动分类和重组您的播放列表。

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![YouTube API](https://img.shields.io/badge/YouTube%20API-v3-red.svg)](https://developers.google.com/youtube/v3)

## 🚀 功能特性

- ✅ **播放列表管理**: 查看、创建、删除播放列表
- ✅ **批量操作**: 批量移动、删除、重命名视频
- ✅ **智能分析**: 自动分析播放列表，提供整理建议
- ✅ **数据导出**: 导出播放列表数据为 JSON 格式
- ✅ **自动分类**: 根据关键词自动分类视频
- ✅ **重复检测**: 检测重复的播放列表和视频
- ✅ **安全备份**: 操作前自动备份数据

## 📋 核心组件

| 文件 | 功能描述 |
|------|----------|
| `youtube_playlist_manager.py` | 播放列表数据导出和基础管理 |
| `playlist_organizer.py` | **智能内容分析和重组计划生成** |
| `youtube_playlist_executor.py` | **批量操作执行器（重命名、删除等）** |

### 主要特性

- 🤖 **智能分析**: 基于标题、描述和视频内容的自动分类
- 📊 **置信度评分**: 每个分类建议都有可信度评估
- 🔄 **批量操作**: 支持批量重命名、删除和合并建议
- 🛡️ **安全机制**: 操作前确认和自动备份
- 📈 **详细报告**: 完整的分析和执行日志

## 📋 系统要求

- Python 3.7 或更高版本
- Google 账户
- YouTube Data API v3 访问权限

## 🛠️ 安装步骤

### 1. 克隆或下载项目文件

确保您有以下文件：
- `youtube_playlist_manager.py` - 主程序文件
- `requirements.txt` - 依赖包列表
- `config_template.json` - 配置文件模板
- `README.md` - 使用说明

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 设置 Google API 凭据

#### 步骤 A: 创建 Google Cloud 项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 YouTube Data API v3

#### 步骤 B: 创建 OAuth2 凭据

1. 在 Google Cloud Console 中，转到「凭据」页面
2. 点击「创建凭据」→「OAuth 客户端 ID」
3. 选择应用类型为「桌面应用程序」
4. 下载 JSON 凭据文件
5. 将文件重命名为 `credentials.json` 并放在项目目录中

#### 步骤 C: 获取 API 密钥（可选）

1. 在 Google Cloud Console 中，点击「创建凭据」→「API 密钥」
2. 复制生成的 API 密钥
3. 建议限制 API 密钥只能访问 YouTube Data API

### 4. 配置设置

复制 `config_template.json` 为 `config.json` 并根据需要修改：

```bash
cp config_template.json config.json
```

编辑 `config.json` 文件，填入您的设置。

## 🎯 使用方法

### 基本使用

运行主程序：

```bash
python youtube_playlist_manager.py
```

首次运行时，程序会：
1. 打开浏览器进行 OAuth 认证
2. 要求您登录 Google 账户
3. 授权应用访问您的 YouTube 数据
4. 保存认证令牌以供后续使用

### 主要功能

#### 1. 查看播放列表
- 显示所有播放列表的基本信息
- 包括标题、视频数量、隐私设置等

#### 2. 分析播放列表
- 检测空播放列表
- 识别过大的播放列表（>100个视频）
- 发现可能重复的播放列表标题
- 提供整理建议

#### 3. 导出数据
- 将所有播放列表数据导出为 JSON 文件
- 包含完整的视频信息和元数据
- 可用于备份或数据分析

#### 4. 创建播放列表
- 快速创建新的播放列表
- 设置标题、描述和隐私级别

#### 5. 删除播放列表
- 安全删除不需要的播放列表
- 包含确认步骤防止误删

### 高级功能

#### 批量操作示例

```python
from youtube_playlist_manager import YouTubePlaylistManager

# 初始化管理器
manager = YouTubePlaylistManager()

# 获取所有播放列表
playlists = manager.get_my_playlists()

# 分析播放列表
analysis = manager.analyze_playlists(playlists)
print(f"发现 {len(analysis['empty_playlists'])} 个空播放列表")

# 创建新播放列表
new_playlist_id = manager.create_playlist(
    title="整理后的音乐",
    description="自动整理的音乐视频",
    privacy_status="private"
)

# 导出数据
manager.export_playlists_to_json("backup_2025.json")
```

## ⚙️ 配置选项

### API 设置
- `api_key`: YouTube Data API 密钥
- `credentials_file`: OAuth2 凭据文件路径
- `token_file`: 访问令牌保存路径

### 操作设置
- `max_results_per_request`: 每次 API 请求的最大结果数
- `request_delay_seconds`: API 请求之间的延迟
- `backup_before_operations`: 操作前是否自动备份

### 整理规则
- `auto_delete_empty_playlists`: 是否自动删除空播放列表
- `max_videos_per_playlist`: 播放列表最大视频数
- `duplicate_handling`: 重复内容处理方式
- `default_privacy_status`: 新播放列表的默认隐私设置

### 分类规则
配置文件中的 `categories` 部分定义了自动分类的关键词：

```json
"categories": {
  "music": ["音乐", "歌曲", "MV", "music", "song"],
  "education": ["教程", "学习", "tutorial", "education"],
  "entertainment": ["娱乐", "搞笑", "entertainment", "funny"]
}
```

## 🔒 安全和隐私

- **本地存储**: 所有数据都存储在您的本地计算机上
- **OAuth2 认证**: 使用 Google 官方的安全认证流程
- **权限控制**: 只请求必要的 YouTube 访问权限
- **数据备份**: 重要操作前自动创建备份

## 📊 API 配额限制

YouTube Data API 有以下配额限制：
- 每日配额：10,000 点
- 每个视频操作：约 50 点
- 每个播放列表操作：约 50 点

建议：
- 分批处理大量数据
- 使用导出功能进行离线分析
- 合理安排操作时间

## 🐛 故障排除

### 常见问题

#### 1. 认证失败
```
错误: 找不到凭据文件 credentials.json
```
**解决方案**: 确保从 Google Cloud Console 下载了正确的 OAuth2 凭据文件

#### 2. API 配额超限
```
quotaExceeded: The request cannot be completed because you have exceeded your quota
```
**解决方案**: 等待配额重置（通常在太平洋时间午夜）或申请配额增加

#### 3. 权限不足
```
insufficientPermissions: The request requires user authentication
```
**解决方案**: 重新运行认证流程，确保授予了所有必要权限

#### 4. 网络连接问题
```
ConnectionError: Failed to establish a new connection
```
**解决方案**: 检查网络连接，确保可以访问 Google API

### 调试模式

在代码中添加调试信息：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 贡献

欢迎提交问题报告和功能请求！如果您想贡献代码：

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 🙏 致谢

- Google YouTube Data API
- Python 社区的优秀库
- 所有贡献者和用户

## 📞 支持

如果您遇到问题或需要帮助：

1. 查看本 README 的故障排除部分
2. 搜索现有的 Issues
3. 创建新的 Issue 并提供详细信息

---

## 🎵 Vibe Coding 声明

本项目在开发过程中采用了 **Vibe Coding** 的开发理念和方法论。Vibe Coding 是一种注重开发体验、代码美感和创造性思维的编程方式，强调：

- 🎨 **代码即艺术**: 追求代码的优雅和可读性
- 🌊 **流畅体验**: 注重开发过程的连贯性和愉悦感
- 🚀 **创新思维**: 鼓励创造性解决方案和独特的实现方式
- 🎯 **用户导向**: 始终以用户体验为核心进行设计
- 🔄 **持续迭代**: 拥抱变化，持续优化和改进

通过 Vibe Coding 的指导，本项目不仅实现了功能需求，更在代码结构、用户界面和整体体验上追求卓越。我们相信好的代码不仅要能工作，更要能够激发开发者和用户的灵感。

**感谢 Vibe Coding 社区为现代软件开发带来的新思路和创新精神！** 🎉

---

**注意**: 使用本工具时请遵守 YouTube 的服务条款和 API 使用政策。请负责任地使用 API，避免过度请求。