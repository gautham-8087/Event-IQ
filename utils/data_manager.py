import json
import os
from .supabase_client import supabase

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
USE_SUPABASE = os.environ.get("USE_SUPABASE") == "True"

class DataManager:
    EVENTS_FILE = os.path.join(DATA_DIR, 'events.json')
    RESOURCES_FILE = os.path.join(DATA_DIR, 'resources.json')
    ALLOCATIONS_FILE = os.path.join(DATA_DIR, 'allocations.json')

    @staticmethod
    def _load_json(filepath):
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    @staticmethod
    def _save_json(filepath, data):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def _clean_data(data):
        """Removes keys with None values to match simplified JSON structure."""
        if not data:
            return data
        if isinstance(data, list):
            return [{k: v for k, v in item.items() if v is not None} for item in data]
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if v is not None}
        return data

    @classmethod
    def get_events(cls):
        if USE_SUPABASE:
            # Propagate exceptions to caller
            response = supabase.table('events').select("*").execute()
            return cls._clean_data(response.data)
        return cls._load_json(cls.EVENTS_FILE)

    @classmethod
    def save_events(cls, events):
        """
        Refrain from using this in Supabase mode if possible. 
        It overwrites the entire dataset.
        """
        if USE_SUPABASE:
            print("Warning: save_events called in Supabase mode. This is not fully supported / optimized.")
            return
        cls._save_json(cls.EVENTS_FILE, events)

    @classmethod
    def get_resources(cls):
        if USE_SUPABASE:
            response = supabase.table('resources').select("*").execute()
            return cls._clean_data(response.data)
        return cls._load_json(cls.RESOURCES_FILE)

    @classmethod
    def get_allocations(cls):
        if USE_SUPABASE:
            response = supabase.table('allocations').select("*").execute()
            return cls._clean_data(response.data)
        return cls._load_json(cls.ALLOCATIONS_FILE)

    @classmethod
    def save_allocations(cls, allocations):
        if USE_SUPABASE:
             print("Warning: save_allocations called in Supabase mode via batch save.")
             return
        cls._save_json(cls.ALLOCATIONS_FILE, allocations)

    @classmethod
    def add_event(cls, event):
        if USE_SUPABASE:
            supabase.table('events').insert(event).execute()
            return

        events = cls.get_events()
        events.append(event)
        cls.save_events(events)

    @classmethod
    def add_allocation(cls, allocation):
        if USE_SUPABASE:
            supabase.table('allocations').insert(allocation).execute()
            return

        allocations = cls.get_allocations()
        allocations.append(allocation)
        cls.save_allocations(allocations)

    @classmethod
    def delete_event(cls, event_id):
        if USE_SUPABASE:
            try:
                # Allocations cascade deleted via DB FK constraints
                supabase.table('events').delete().eq('id', event_id).execute()
            except Exception as e:
                print(f"Supabase Error (delete_event): {e}")
            return

        events = cls.get_events()
        events = [e for e in events if e['id'] != event_id]
        cls.save_events(events)
        
        # Remove allocations
        allocations = cls.get_allocations()
        allocations = [a for a in allocations if a['event_id'] != event_id]
        cls.save_allocations(allocations)
