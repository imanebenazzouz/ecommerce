"""
Système de persistance simple avec fichiers JSON
"""

import json
import os
from typing import Dict, List, Any, Optional
import uuid

class PersistentStorage:
    """Stockage persistant avec fichiers JSON"""
    
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        """Crée le dossier de stockage s'il n'existe pas"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
    
    def _get_file_path(self, collection: str) -> str:
        """Retourne le chemin du fichier pour une collection"""
        return os.path.join(self.storage_dir, f"{collection}.json")
    
    def _load_collection(self, collection: str) -> Dict[str, Any]:
        """Charge une collection depuis le fichier JSON"""
        file_path = self._get_file_path(collection)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_collection(self, collection: str, data: Dict[str, Any]):
        """Sauvegarde une collection dans le fichier JSON"""
        file_path = self._get_file_path(collection)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def save_item(self, collection: str, item_id: str, item_data: Dict[str, Any]):
        """Sauvegarde un élément dans une collection"""
        data = self._load_collection(collection)
        data[item_id] = item_data
        self._save_collection(collection, data)
    
    def get_item(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un élément d'une collection"""
        data = self._load_collection(collection)
        return data.get(item_id)
    
    def get_all_items(self, collection: str) -> List[Dict[str, Any]]:
        """Récupère tous les éléments d'une collection"""
        data = self._load_collection(collection)
        return list(data.values())
    
    def delete_item(self, collection: str, item_id: str):
        """Supprime un élément d'une collection"""
        data = self._load_collection(collection)
        if item_id in data:
            del data[item_id]
            self._save_collection(collection, data)
    
    def update_item(self, collection: str, item_id: str, item_data: Dict[str, Any]):
        """Met à jour un élément dans une collection"""
        data = self._load_collection(collection)
        if item_id in data:
            data[item_id].update(item_data)
            self._save_collection(collection, data)

# Instance globale
persistent_storage = PersistentStorage()
