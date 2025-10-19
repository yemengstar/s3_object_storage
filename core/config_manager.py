"""
配置管理器
支持多配置保存、加载和切换
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import sys 

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = 'uploader_config.json'):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件名（相对于exe目录或当前目录）
        """
        # 获取配置文件路径（支持打包后的exe）
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe
            app_dir = Path(sys.executable).parent
        else:
            # 如果是Python脚本
            app_dir = Path(__file__).parent.parent
        
        self.config_path = app_dir / config_file
        self.configs: Dict[str, dict] = {}
        self.current_profile: str = 'default'
        self.load_configs()
    
    def load_configs(self):
        """从文件加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.configs = data.get('profiles', {})
                    self.current_profile = data.get('current_profile', 'default')
                    
                    # 确保至少有一个默认配置
                    if not self.configs:
                        self.configs['default'] = self._get_default_config()
            except Exception as e:
                print(f'加载配置失败: {e}')
                self.configs = {'default': self._get_default_config()}
        else:
            # 创建默认配置
            self.configs = {'default': self._get_default_config()}
    
    def save_configs(self):
        """保存配置到文件"""
        try:
            data = {
                'profiles': self.configs,
                'current_profile': self.current_profile
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f'保存配置失败: {e}')
            return False
    
    def get_current_config(self) -> dict:
        """获取当前配置"""
        return self.configs.get(self.current_profile, self._get_default_config())
    
    def save_current_config(self, config: dict):
        """保存当前配置"""
        self.configs[self.current_profile] = config.copy()
        self.save_configs()
    
    def get_profile_names(self) -> List[str]:
        """获取所有配置名称列表"""
        return list(self.configs.keys())
    
    def switch_profile(self, profile_name: str) -> bool:
        """切换配置"""
        if profile_name in self.configs:
            self.current_profile = profile_name
            self.save_configs()
            return True
        return False
    
    def add_profile(self, profile_name: str, config: dict = None) -> bool:
        """添加新配置"""
        if profile_name in self.configs:
            return False  # 配置名已存在
        
        if config is None:
            config = self._get_default_config()
        
        self.configs[profile_name] = config
        self.save_configs()
        return True
    
    def delete_profile(self, profile_name: str) -> bool:
        """删除配置"""
        if profile_name == 'default':
            return False  # 不允许删除默认配置
        
        if profile_name in self.configs:
            del self.configs[profile_name]
            
            # 如果删除的是当前配置，切换到默认配置
            if self.current_profile == profile_name:
                self.current_profile = 'default'
            
            self.save_configs()
            return True
        return False
    
    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """重命名配置"""
        if old_name == 'default':
            return False  # 不允许重命名默认配置
        
        if old_name not in self.configs or new_name in self.configs:
            return False
        
        self.configs[new_name] = self.configs.pop(old_name)
        
        # 如果重命名的是当前配置，更新当前配置名
        if self.current_profile == old_name:
            self.current_profile = new_name
        
        self.save_configs()
        return True
    
    def _get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            'endpoint': 'https://s3.example.com',
            'bucket': 'my-bucket',
            'access_key': '',
            'secret_key': '',
            'base_url': 'https://cdn.example.com',
            'prefix': '',
            'make_public': True,
            'max_threads': 3
        }


