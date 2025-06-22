import json
import os
from typing import Dict, List, Optional
from core.table_model import TableModel
from pathlib import Path


class PresetManager:
    def __init__(self, presets_dir: str = "presets"):
        self.presets_dir = Path(presets_dir)
        self.presets_dir.mkdir(exist_ok=True)
    
    def save_preset(self, table_model: TableModel, name: str, 
                   description: str = "", tags: List[str] = None) -> bool:
        if not name or not self._is_valid_filename(name):
            return False
        
        if tags is None:
            tags = []
        
        preset_data = {
            'name': name,
            'description': description,
            'tags': tags,
            'table_data': table_model.to_dict(),
            'version': '1.0'
        }
        
        filename = f"{name}.json"
        filepath = self.presets_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(preset_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to save preset: {e}")
            return False
    
    def load_preset(self, name: str) -> Optional[TableModel]:
        filename = f"{name}.json"
        filepath = self.presets_dir / filename
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            
            table_data = preset_data.get('table_data', {})
            return TableModel.from_dict(table_data)
        except Exception as e:
            print(f"Failed to load preset: {e}")
            return None
    
    def get_preset_info(self, name: str) -> Optional[Dict]:
        filename = f"{name}.json"
        filepath = self.presets_dir / filename
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            
            return {
                'name': preset_data.get('name', name),
                'description': preset_data.get('description', ''),
                'tags': preset_data.get('tags', []),
                'version': preset_data.get('version', '1.0'),
                'file_path': str(filepath),
                'file_size': filepath.stat().st_size,
                'modified_time': filepath.stat().st_mtime
            }
        except Exception as e:
            print(f"Failed to get preset info: {e}")
            return None
    
    def list_presets(self) -> List[Dict]:
        presets = []
        
        try:
            for filepath in self.presets_dir.glob("*.json"):
                name = filepath.stem
                preset_info = self.get_preset_info(name)
                if preset_info:
                    presets.append(preset_info)
        except Exception as e:
            print(f"Failed to list presets: {e}")
        
        return sorted(presets, key=lambda x: x.get('modified_time', 0), reverse=True)
    
    def delete_preset(self, name: str) -> bool:
        filename = f"{name}.json"
        filepath = self.presets_dir / filename
        
        if not filepath.exists():
            return False
        
        try:
            filepath.unlink()
            return True
        except Exception as e:
            print(f"Failed to delete preset: {e}")
            return False
    
    def rename_preset(self, old_name: str, new_name: str) -> bool:
        if not self._is_valid_filename(new_name):
            return False
        
        old_filepath = self.presets_dir / f"{old_name}.json"
        new_filepath = self.presets_dir / f"{new_name}.json"
        
        if not old_filepath.exists() or new_filepath.exists():
            return False
        
        try:
            with open(old_filepath, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            
            preset_data['name'] = new_name
            
            with open(new_filepath, 'w', encoding='utf-8') as f:
                json.dump(preset_data, f, indent=2, ensure_ascii=False)
            
            old_filepath.unlink()
            return True
        except Exception as e:
            print(f"Failed to rename preset: {e}")
            return False
    
    def export_preset(self, name: str, export_path: str) -> bool:
        filename = f"{name}.json"
        filepath = self.presets_dir / filename
        
        if not filepath.exists():
            return False
        
        try:
            import shutil
            shutil.copy2(filepath, export_path)
            return True
        except Exception as e:
            print(f"Failed to export preset: {e}")
            return False
    
    def import_preset(self, import_path: str, new_name: str = None) -> bool:
        import_file = Path(import_path)
        
        if not import_file.exists() or import_file.suffix != '.json':
            return False
        
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            
            if not self._validate_preset_data(preset_data):
                return False
            
            if new_name:
                preset_data['name'] = new_name
                filename = f"{new_name}.json"
            else:
                filename = import_file.name
            
            filepath = self.presets_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(preset_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Failed to import preset: {e}")
            return False
    
    def search_presets(self, query: str, search_tags: bool = True, 
                      search_description: bool = True) -> List[Dict]:
        query = query.lower()
        results = []
        
        for preset in self.list_presets():
            match = False
            
            if query in preset['name'].lower():
                match = True
            
            if search_description and query in preset.get('description', '').lower():
                match = True
            
            if search_tags:
                for tag in preset.get('tags', []):
                    if query in tag.lower():
                        match = True
                        break
            
            if match:
                results.append(preset)
        
        return results
    
    def get_presets_by_tag(self, tag: str) -> List[Dict]:
        tag = tag.lower()
        results = []
        
        for preset in self.list_presets():
            preset_tags = [t.lower() for t in preset.get('tags', [])]
            if tag in preset_tags:
                results.append(preset)
        
        return results
    
    def _is_valid_filename(self, name: str) -> bool:
        if not name or len(name.strip()) == 0:
            return False
        
        invalid_chars = '<>:"/\\|?*'
        return not any(char in name for char in invalid_chars)
    
    def _validate_preset_data(self, data: Dict) -> bool:
        required_fields = ['table_data']
        
        for field in required_fields:
            if field not in data:
                return False
        
        table_data = data['table_data']
        if not isinstance(table_data, dict):
            return False
        
        if 'rows' not in table_data or 'cols' not in table_data:
            return False
        
        return True