#!/usr/bin/env python3
"""
YouTube Playlist Organizer

This script analyzes and reorganizes YouTube playlists based on content analysis.
It provides automatic categorization, merging, and renaming functionality.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import os

class PlaylistOrganizer:
    def __init__(self, backup_file: str = "playlists_backup.json"):
        self.backup_file = backup_file
        self.playlists_data = None
        self.categories = {
            "AI_Programming": {
                "keywords": ["ai", "claude", "coding", "programming", "vibe coding", "cursor", "superclaude"],
                "description": "AI编程开发",
                "suggested_name": "🤖 AI编程开发"
            },
            "Investment_Finance": {
                "keywords": ["bitcoin", "crypto", "investment", "finance", "trading", "加密", "投资"],
                "description": "投资理财",
                "suggested_name": "💰 投资理财"
            },
            "Health_Wellness": {
                "keywords": ["康复", "健康", "筋膜", "物理治疗", "health", "wellness", "therapy"],
                "description": "健康养生",
                "suggested_name": "🏥 健康养生"
            },
            "Gaming": {
                "keywords": ["黑神话", "游戏", "game", "gaming", "wukong", "攻略"],
                "description": "游戏娱乐",
                "suggested_name": "🎮 游戏娱乐"
            },
            "Technology_Hardware": {
                "keywords": ["pc", "diy", "hardware", "tech", "computer", "rtx", "cpu"],
                "description": "科技硬件",
                "suggested_name": "🔧 科技硬件"
            },
            "Music_Relaxation": {
                "keywords": ["music", "lo-fi", "lofi", "relaxation", "音乐", "放松", "jazz"],
                "description": "音乐放松",
                "suggested_name": "🎵 音乐放松"
            },
            "Education_Learning": {
                "keywords": ["tutorial", "education", "learning", "教程", "学习", "课程"],
                "description": "教育学习",
                "suggested_name": "📚 教育学习"
            }
        }
        
    def load_data(self) -> bool:
        """Load playlist data from backup file"""
        try:
            with open(self.backup_file, 'r', encoding='utf-8') as f:
                self.playlists_data = json.load(f)
            print(f"✅ 成功加载 {self.playlists_data['total_playlists']} 个播放列表")
            return True
        except FileNotFoundError:
            print(f"❌ 找不到备份文件: {self.backup_file}")
            return False
        except json.JSONDecodeError:
            print(f"❌ 备份文件格式错误: {self.backup_file}")
            return False
    
    def analyze_playlist_content(self, playlist: Dict) -> Tuple[str, float]:
        """Analyze playlist content and return category with confidence score"""
        title = playlist.get('title', '').lower()
        description = playlist.get('description', '').lower()
        
        # Analyze video titles and descriptions
        video_content = ""
        for video in playlist.get('videos', []):
            video_content += f" {video.get('title', '')} {video.get('description', '')}"
        video_content = video_content.lower()
        
        # Combine all text content
        all_content = f"{title} {description} {video_content}"
        
        category_scores = {}
        
        for category, info in self.categories.items():
            score = 0
            for keyword in info['keywords']:
                # Count keyword occurrences with different weights
                title_matches = len(re.findall(keyword, title))
                description_matches = len(re.findall(keyword, description))
                video_matches = len(re.findall(keyword, video_content))
                
                # Weight: title > description > video content
                score += title_matches * 3 + description_matches * 2 + video_matches * 1
            
            category_scores[category] = score
        
        # Find best category
        if not category_scores or max(category_scores.values()) == 0:
            return "Uncategorized", 0.0
        
        best_category = max(category_scores, key=category_scores.get)
        max_score = category_scores[best_category]
        
        # Calculate confidence (normalize by content length)
        confidence = min(max_score / max(len(all_content.split()) / 10, 1), 1.0)
        
        return best_category, confidence
    
    def categorize_playlists(self) -> Dict[str, List[Dict]]:
        """Categorize all playlists"""
        if not self.playlists_data:
            return {}
        
        categorized = defaultdict(list)
        
        for playlist in self.playlists_data['playlists']:
            category, confidence = self.analyze_playlist_content(playlist)
            
            playlist_info = {
                'original_data': playlist,
                'category': category,
                'confidence': confidence,
                'video_count': playlist.get('video_count', 0),
                'title': playlist.get('title', ''),
                'id': playlist.get('id', '')
            }
            
            categorized[category].append(playlist_info)
        
        return dict(categorized)
    
    def generate_reorganization_plan(self) -> Dict:
        """Generate a reorganization plan"""
        categorized = self.categorize_playlists()
        
        plan = {
            'timestamp': datetime.now().isoformat(),
            'original_count': self.playlists_data['total_playlists'],
            'categories': {},
            'merge_suggestions': [],
            'rename_suggestions': [],
            'delete_suggestions': []
        }
        
        for category, playlists in categorized.items():
            if category == "Uncategorized":
                continue
                
            category_info = self.categories.get(category, {})
            
            plan['categories'][category] = {
                'suggested_name': category_info.get('suggested_name', category),
                'description': category_info.get('description', ''),
                'playlists': len(playlists),
                'total_videos': sum(p['video_count'] for p in playlists),
                'playlist_details': [{
                    'title': p['title'],
                    'video_count': p['video_count'],
                    'confidence': round(p['confidence'], 2),
                    'id': p['id']
                } for p in playlists]
            }
            
            # Suggest merges for categories with multiple playlists
            if len(playlists) > 1:
                plan['merge_suggestions'].append({
                    'category': category,
                    'target_name': category_info.get('suggested_name', category),
                    'playlists_to_merge': [p['title'] for p in playlists],
                    'total_videos': sum(p['video_count'] for p in playlists)
                })
            
            # Suggest renames for single playlists
            elif len(playlists) == 1:
                playlist = playlists[0]
                suggested_name = category_info.get('suggested_name', category)
                if playlist['title'] != suggested_name:
                    plan['rename_suggestions'].append({
                        'current_name': playlist['title'],
                        'suggested_name': suggested_name,
                        'category': category,
                        'id': playlist['id']
                    })
        
        # Handle uncategorized playlists
        if "Uncategorized" in categorized:
            uncategorized = categorized["Uncategorized"]
            
            # Suggest deletion for empty or very small playlists
            for playlist in uncategorized:
                if playlist['video_count'] <= 1:
                    plan['delete_suggestions'].append({
                        'title': playlist['title'],
                        'video_count': playlist['video_count'],
                        'reason': '视频数量过少',
                        'id': playlist['id']
                    })
        
        return plan
    
    def save_reorganization_plan(self, plan: Dict, filename: str = "reorganization_plan.json"):
        """Save reorganization plan to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        print(f"✅ 重组计划已保存到: {filename}")
    
    def print_analysis_report(self, plan: Dict):
        """Print detailed analysis report"""
        print("\n" + "="*60)
        print("📊 YouTube 播放列表分析报告")
        print("="*60)
        
        print(f"\n📅 分析时间: {plan['timestamp']}")
        print(f"📝 原始播放列表数量: {plan['original_count']}")
        
        print("\n🗂️ 分类结果:")
        print("-" * 40)
        
        for category, info in plan['categories'].items():
            print(f"\n📁 {info['suggested_name']}")
            print(f"   播放列表数量: {info['playlists']}")
            print(f"   总视频数量: {info['total_videos']}")
            print(f"   包含播放列表:")
            
            for playlist in info['playlist_details']:
                confidence_emoji = "🟢" if playlist['confidence'] > 0.7 else "🟡" if playlist['confidence'] > 0.3 else "🔴"
                print(f"     {confidence_emoji} {playlist['title']} ({playlist['video_count']}个视频, 置信度: {playlist['confidence']})")
        
        if plan['merge_suggestions']:
            print("\n🔄 合并建议:")
            print("-" * 40)
            for suggestion in plan['merge_suggestions']:
                print(f"\n📁 目标: {suggestion['target_name']}")
                print(f"   合并播放列表: {', '.join(suggestion['playlists_to_merge'])}")
                print(f"   总视频数量: {suggestion['total_videos']}")
        
        if plan['rename_suggestions']:
            print("\n✏️ 重命名建议:")
            print("-" * 40)
            for suggestion in plan['rename_suggestions']:
                print(f"   {suggestion['current_name']} → {suggestion['suggested_name']}")
        
        if plan['delete_suggestions']:
            print("\n🗑️ 删除建议:")
            print("-" * 40)
            for suggestion in plan['delete_suggestions']:
                print(f"   {suggestion['title']} ({suggestion['reason']})")
        
        print("\n" + "="*60)

def main():
    """Main function"""
    print("🚀 YouTube 播放列表智能整理工具")
    print("=" * 50)
    
    organizer = PlaylistOrganizer()
    
    # Load data
    if not organizer.load_data():
        return
    
    # Generate reorganization plan
    print("\n🔍 正在分析播放列表内容...")
    plan = organizer.generate_reorganization_plan()
    
    # Save plan
    organizer.save_reorganization_plan(plan)
    
    # Print report
    organizer.print_analysis_report(plan)
    
    print("\n✨ 分析完成！查看 'reorganization_plan.json' 获取详细计划。")
    print("\n💡 下一步建议:")
    print("   1. 审查分析结果和建议")
    print("   2. 手动调整分类（如需要）")
    print("   3. 使用 YouTube API 执行重组操作")

if __name__ == "__main__":
    main()