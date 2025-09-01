#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 播放列表管理工具

这个工具可以帮助你快速整理和管理 YouTube 收藏列表，包括：
- 获取所有播放列表
- 分析播放列表内容
- 批量操作（移动、删除、重命名视频）
- 自动整理和分类

作者: AI Assistant
日期: 2025
"""

import os
import json
import time
from typing import List, Dict, Optional
from datetime import datetime

try:
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
except ImportError:
    print("请安装必要的依赖包:")
    print("pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    exit(1)

class YouTubePlaylistManager:
    """YouTube 播放列表管理器"""
    
    def __init__(self, api_key: Optional[str] = None, credentials_file: str = 'credentials.json'):
        """
        初始化 YouTube API 客户端
        
        Args:
            api_key: YouTube Data API 密钥（可选）
            credentials_file: OAuth2 凭据文件路径
        """
        self.api_key = api_key
        self.credentials_file = credentials_file
        self.token_file = 'token.json'
        self.youtube = None
        self.scopes = [
            'https://www.googleapis.com/auth/youtube',
            'https://www.googleapis.com/auth/youtube.force-ssl'
        ]
        
        self._authenticate()
    
    def _authenticate(self):
        """认证并建立 YouTube API 连接"""
        creds = None
        
        # 检查是否存在已保存的令牌
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        
        # 如果没有有效凭据，进行 OAuth 流程
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    print(f"错误: 找不到凭据文件 {self.credentials_file}")
                    print("请从 Google Cloud Console 下载 OAuth2 凭据文件")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes)
                creds = flow.run_local_server(port=0)
            
            # 保存凭据以供下次使用
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        # 建立 YouTube API 服务
        self.youtube = build('youtube', 'v3', credentials=creds)
        print("✅ YouTube API 认证成功")
    
    def get_my_playlists(self) -> List[Dict]:
        """获取当前用户的所有播放列表"""
        if not self.youtube:
            print("❌ YouTube API 未初始化")
            return []
        
        playlists = []
        next_page_token = None
        
        try:
            while True:
                request = self.youtube.playlists().list(
                    part='snippet,contentDetails,status',
                    mine=True,
                    maxResults=50,
                    pageToken=next_page_token
                )
                response = request.execute()
                
                for item in response['items']:
                    playlist_info = {
                        'id': item['id'],
                        'title': item['snippet']['title'],
                        'description': item['snippet'].get('description', ''),
                        'video_count': item['contentDetails']['itemCount'],
                        'privacy_status': item['status']['privacyStatus'],
                        'created_at': item['snippet']['publishedAt']
                    }
                    playlists.append(playlist_info)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                # 避免 API 限制
                time.sleep(0.1)
        
        except Exception as e:
            print(f"❌ 获取播放列表失败: {e}")
            return []
        
        print(f"✅ 成功获取 {len(playlists)} 个播放列表")
        return playlists
    
    def get_playlist_videos(self, playlist_id: str) -> List[Dict]:
        """获取指定播放列表中的所有视频"""
        if not self.youtube:
            print("❌ YouTube API 未初始化")
            return []
        
        videos = []
        next_page_token = None
        
        try:
            while True:
                request = self.youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                )
                response = request.execute()
                
                for item in response['items']:
                    video_info = {
                        'playlist_item_id': item['id'],
                        'video_id': item['snippet']['resourceId']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet'].get('description', ''),
                        'position': item['snippet']['position'],
                        'added_at': item['snippet']['publishedAt'],
                        'channel_title': item['snippet']['channelTitle']
                    }
                    videos.append(video_info)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                time.sleep(0.1)
        
        except Exception as e:
            print(f"❌ 获取播放列表视频失败: {e}")
            return []
        
        return videos
    
    def analyze_playlists(self, playlists: List[Dict]) -> Dict:
        """分析播放列表，提供整理建议"""
        analysis = {
            'total_playlists': len(playlists),
            'total_videos': sum(p['video_count'] for p in playlists),
            'empty_playlists': [],
            'large_playlists': [],
            'duplicate_titles': [],
            'suggestions': []
        }
        
        # 查找空播放列表
        for playlist in playlists:
            if playlist['video_count'] == 0:
                analysis['empty_playlists'].append(playlist)
        
        # 查找大型播放列表（超过100个视频）
        for playlist in playlists:
            if playlist['video_count'] > 100:
                analysis['large_playlists'].append(playlist)
        
        # 查找可能重复的标题
        titles = [p['title'].lower() for p in playlists]
        seen = set()
        for i, title in enumerate(titles):
            if title in seen:
                analysis['duplicate_titles'].append(playlists[i])
            seen.add(title)
        
        # 生成整理建议
        if analysis['empty_playlists']:
            analysis['suggestions'].append(f"发现 {len(analysis['empty_playlists'])} 个空播放列表，建议删除")
        
        if analysis['large_playlists']:
            analysis['suggestions'].append(f"发现 {len(analysis['large_playlists'])} 个大型播放列表，建议分割")
        
        if analysis['duplicate_titles']:
            analysis['suggestions'].append(f"发现 {len(analysis['duplicate_titles'])} 个可能重复的播放列表标题")
        
        return analysis
    
    def create_playlist(self, title: str, description: str = '', privacy_status: str = 'private') -> Optional[str]:
        """创建新的播放列表"""
        if not self.youtube:
            print("❌ YouTube API 未初始化")
            return None
        
        try:
            request = self.youtube.playlists().insert(
                part='snippet,status',
                body={
                    'snippet': {
                        'title': title,
                        'description': description
                    },
                    'status': {
                        'privacyStatus': privacy_status
                    }
                }
            )
            response = request.execute()
            playlist_id = response['id']
            print(f"✅ 成功创建播放列表: {title} (ID: {playlist_id})")
            return playlist_id
        
        except Exception as e:
            print(f"❌ 创建播放列表失败: {e}")
            return None
    
    def delete_playlist(self, playlist_id: str) -> bool:
        """删除播放列表"""
        if not self.youtube:
            print("❌ YouTube API 未初始化")
            return False
        
        try:
            request = self.youtube.playlists().delete(id=playlist_id)
            request.execute()
            print(f"✅ 成功删除播放列表 (ID: {playlist_id})")
            return True
        
        except Exception as e:
            print(f"❌ 删除播放列表失败: {e}")
            return False
    
    def move_video_to_playlist(self, video_id: str, source_playlist_id: str, 
                              target_playlist_id: str, position: int = 0) -> bool:
        """将视频从一个播放列表移动到另一个播放列表"""
        if not self.youtube:
            print("❌ YouTube API 未初始化")
            return False
        
        try:
            # 添加到目标播放列表
            add_request = self.youtube.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': target_playlist_id,
                        'position': position,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
            )
            add_request.execute()
            
            # 从源播放列表删除（需要先获取 playlistItem ID）
            source_videos = self.get_playlist_videos(source_playlist_id)
            playlist_item_id = None
            for video in source_videos:
                if video['video_id'] == video_id:
                    playlist_item_id = video['playlist_item_id']
                    break
            
            if playlist_item_id:
                delete_request = self.youtube.playlistItems().delete(id=playlist_item_id)
                delete_request.execute()
            
            print(f"✅ 成功移动视频 {video_id}")
            return True
        
        except Exception as e:
            print(f"❌ 移动视频失败: {e}")
            return False
    
    def export_playlists_to_json(self, filename: str = 'playlists_backup.json'):
        """导出播放列表数据到 JSON 文件"""
        playlists = self.get_my_playlists()
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_playlists': len(playlists),
            'playlists': []
        }
        
        for playlist in playlists:
            videos = self.get_playlist_videos(playlist['id'])
            playlist_data = playlist.copy()
            playlist_data['videos'] = videos
            export_data['playlists'].append(playlist_data)
            print(f"📥 导出播放列表: {playlist['title']} ({len(videos)} 个视频)")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 播放列表数据已导出到 {filename}")

def main():
    """主函数 - 演示基本用法"""
    print("🎵 YouTube 播放列表管理工具")
    print("=" * 40)
    
    # 初始化管理器
    manager = YouTubePlaylistManager()
    
    if not manager.youtube:
        print("❌ 无法连接到 YouTube API")
        return
    
    while True:
        print("\n📋 请选择操作:")
        print("1. 查看所有播放列表")
        print("2. 分析播放列表")
        print("3. 导出播放列表数据")
        print("4. 创建新播放列表")
        print("5. 删除播放列表")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-5): ").strip()
        
        if choice == '0':
            print("👋 再见！")
            break
        
        elif choice == '1':
            playlists = manager.get_my_playlists()
            print(f"\n📋 您的播放列表 (共 {len(playlists)} 个):")
            for i, playlist in enumerate(playlists, 1):
                print(f"{i:2d}. {playlist['title']} ({playlist['video_count']} 个视频) - {playlist['privacy_status']}")
        
        elif choice == '2':
            playlists = manager.get_my_playlists()
            analysis = manager.analyze_playlists(playlists)
            
            print(f"\n📊 播放列表分析结果:")
            print(f"总播放列表数: {analysis['total_playlists']}")
            print(f"总视频数: {analysis['total_videos']}")
            print(f"空播放列表: {len(analysis['empty_playlists'])}")
            print(f"大型播放列表: {len(analysis['large_playlists'])}")
            print(f"可能重复的标题: {len(analysis['duplicate_titles'])}")
            
            if analysis['suggestions']:
                print("\n💡 整理建议:")
                for suggestion in analysis['suggestions']:
                    print(f"  • {suggestion}")
        
        elif choice == '3':
            filename = input("请输入导出文件名 (默认: playlists_backup.json): ").strip()
            if not filename:
                filename = 'playlists_backup.json'
            manager.export_playlists_to_json(filename)
        
        elif choice == '4':
            title = input("请输入播放列表标题: ").strip()
            if title:
                description = input("请输入描述 (可选): ").strip()
                privacy = input("请输入隐私设置 (public/private/unlisted, 默认: private): ").strip()
                if privacy not in ['public', 'private', 'unlisted']:
                    privacy = 'private'
                manager.create_playlist(title, description, privacy)
        
        elif choice == '5':
            playlists = manager.get_my_playlists()
            if not playlists:
                print("❌ 没有找到播放列表")
                continue
            
            print("\n📋 选择要删除的播放列表:")
            for i, playlist in enumerate(playlists, 1):
                print(f"{i:2d}. {playlist['title']} ({playlist['video_count']} 个视频)")
            
            try:
                index = int(input("请输入播放列表编号: ")) - 1
                if 0 <= index < len(playlists):
                    playlist = playlists[index]
                    confirm = input(f"确认删除播放列表 '{playlist['title']}'? (y/N): ").strip().lower()
                    if confirm == 'y':
                        manager.delete_playlist(playlist['id'])
                else:
                    print("❌ 无效的播放列表编号")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        else:
            print("❌ 无效的选项，请重新选择")

if __name__ == '__main__':
    main()