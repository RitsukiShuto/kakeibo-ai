import json
import os

class CategoryMapper:
    def __init__(self, mapping_path="local/config/mapping.json"):
        self.mapping_path = mapping_path
        self.mapping = self._load_mapping()
        
    def _load_mapping(self):
        if os.path.exists(self.mapping_path):
            try:
                with open(self.mapping_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "category_mappings": {},
            "genre_mappings": {}
        }
        
    def apply_mapping(self, raw_category: str, raw_genre: str):
        if not self.mapping:
            return raw_category, raw_genre
            
        # 1. Genre-level overrides (highest priority)
        genre_rules = self.mapping.get("genre_mappings", {})
        if raw_genre in genre_rules:
            rule = genre_rules[raw_genre]
            if isinstance(rule, dict):
                return rule.get("category", raw_category), rule.get("genre", raw_genre)
            elif isinstance(rule, str):
                return raw_category, rule
            
        # 2. Category-level overrides
        cat_rules = self.mapping.get("category_mappings", {})
        if raw_category in cat_rules:
            new_cat = cat_rules[raw_category]
            return new_cat, raw_genre
            
        return raw_category, raw_genre
