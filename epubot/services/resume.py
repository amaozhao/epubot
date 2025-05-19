import json
import os
from typing import Dict, Set

class Resume:
    """简单的断点续传服务，只保存文件内容和状态"""
    
    def __init__(self, state_file: str = ".translation_state.json"):
        self.state_file = state_file
        self.state: Dict[str, Dict] = self._load_state()
    
    def _load_state(self) -> Dict:
        """加载状态文件"""
        if not os.path.exists(self.state_file):
            return {}
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_state(self) -> None:
        """保存状态到文件"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def get_processed_files(self, epub_path: str) -> Set[str]:
        """获取已处理的文件列表"""
        return set(self.state.get(epub_path, {}).get('processed_files', []))
    
    def mark_file_processed(self, epub_path: str, file_path: str) -> None:
        """标记文件为已处理"""
        if epub_path not in self.state:
            self.state[epub_path] = {'processed_files': []}
        
        if file_path not in self.state[epub_path]['processed_files']:
            self.state[epub_path]['processed_files'].append(file_path)
            self._save_state()
    
    def clear_state(self, epub_path: str = None) -> None:
        """清除状态"""
        if epub_path and epub_path in self.state:
            del self.state[epub_path]
            self._save_state()
        elif epub_path is None:
            self.state = {}
            self._save_state()