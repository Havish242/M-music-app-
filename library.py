import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

LIB_FILE = os.path.join(os.path.dirname(__file__), 'library.json')
LIB_DIR = os.path.join(os.path.dirname(__file__), 'library')

os.makedirs(LIB_DIR, exist_ok=True)


def _load() -> Dict:
    """Return a dict with keys: 'tracks' (list) and 'playlists' (list).
    Keep backwards compatibility when the file contains a raw list of tracks.
    """
    if not os.path.exists(LIB_FILE):
        return {'tracks': [], 'playlists': []}
    try:
        with open(LIB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return {'tracks': data, 'playlists': []}
            if isinstance(data, dict):
                return {
                    'tracks': data.get('tracks', []),
                    'playlists': data.get('playlists', []),
                }
            return {'tracks': [], 'playlists': []}
    except Exception:
        return {'tracks': [], 'playlists': []}


def _save(state: Dict):
    with open(LIB_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def list_tracks() -> List[Dict]:
    return _load().get('tracks', [])


def add_track(title: str, file_path: str, duration: float = 0.0, prompt: Optional[str] = None) -> Dict:
    state = _load()
    tracks = state.get('tracks', [])
    track = {
        'id': str(uuid.uuid4()),
        'title': title,
        'file': os.path.abspath(file_path),
        'duration': float(duration),
        'prompt': prompt or '',
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }
    tracks.insert(0, track)
    state['tracks'] = tracks
    _save(state)
    return track


def find_track(track_id: str) -> Optional[Dict]:
    tracks = _load().get('tracks', [])
    for t in tracks:
        if t.get('id') == track_id:
            return t
    return None


def list_playlists() -> List[Dict]:
    return _load().get('playlists', [])


def add_playlist(name: str) -> Dict:
    state = _load()
    playlists = state.get('playlists', [])
    pl = {'id': str(uuid.uuid4()), 'name': name, 'track_ids': []}
    playlists.append(pl)
    state['playlists'] = playlists
    _save(state)
    return pl


def add_track_to_playlist(playlist_id: str, track_id: str) -> bool:
    state = _load()
    playlists = state.get('playlists', [])
    for pl in playlists:
        if pl.get('id') == playlist_id:
            if track_id not in pl.get('track_ids', []):
                pl.setdefault('track_ids', []).append(track_id)
                state['playlists'] = playlists
                _save(state)
            return True
    return False


def list_tracks_in_playlist(playlist_id: str) -> List[Dict]:
    state = _load()
    playlists = state.get('playlists', [])
    tracks = state.get('tracks', [])
    for pl in playlists:
        if pl.get('id') == playlist_id:
            ids = pl.get('track_ids', [])
            return [t for t in tracks if t.get('id') in ids]
    return []
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

LIB_FILE = os.path.join(os.path.dirname(__file__), 'library.json')
LIB_DIR = os.path.join(os.path.dirname(__file__), 'library')

os.makedirs(LIB_DIR, exist_ok=True)


def _load() -> List[Dict]:
    if not os.path.exists(LIB_FILE):
        return []
    try:
        with open(LIB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def _load() -> Dict:
    """Return a dict with keys: 'tracks' (list) and 'playlists' (list).
    Keep backwards compatibility when the file contains a raw list of tracks.
    """
    if not os.path.exists(LIB_FILE):
        return {'tracks': [], 'playlists': []}
    try:
        with open(LIB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return {'tracks': data, 'playlists': []}
            if isinstance(data, dict):
                # ensure keys exist
                return {
                    'tracks': data.get('tracks', []),
                    'playlists': data.get('playlists', []),
                }
            return {'tracks': [], 'playlists': []}
    except Exception:
        return {'tracks': [], 'playlists': []}

def _save(all_tracks: List[Dict]):
    with open(LIB_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_tracks, f, ensure_ascii=False, indent=2)

def _save(state: Dict):
    with open(LIB_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def list_tracks() -> List[Dict]:
    return _load()


def add_track(title: str, file_path: str, duration: float = 0.0, prompt: Optional[str] = None) -> Dict:
    tracks = _load()
    track = {
        'id': str(uuid.uuid4()),
        'title': title,
        'file': os.path.abspath(file_path),
        'duration': float(duration),
        'prompt': prompt or '',
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }
    tracks.insert(0, track)
    _save(tracks)
    return track

def add_track(title: str, file_path: str, duration: float = 0.0, prompt: Optional[str] = None) -> Dict:
    state = _load()
    tracks = state.get('tracks', [])
    track = {
        'id': str(uuid.uuid4()),
        'title': title,
        'file': os.path.abspath(file_path),
        'duration': float(duration),
        'prompt': prompt or '',
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }
    tracks.insert(0, track)
    state['tracks'] = tracks
    _save(state)
    return track

def find_track(track_id: str) -> Optional[Dict]:
    tracks = _load()
    for t in tracks:
        if t.get('id') == track_id:
            return t
    return None

    tracks = _load().get('tracks', [])
    for t in tracks:
        if t.get('id') == track_id:
            return t
    return None


def list_playlists() -> List[Dict]:
    return _load().get('playlists', [])


def add_playlist(name: str) -> Dict:
    state = _load()
    playlists = state.get('playlists', [])
    pl = {'id': str(uuid.uuid4()), 'name': name, 'track_ids': []}
    playlists.append(pl)
    state['playlists'] = playlists
    _save(state)
    return pl


def add_track_to_playlist(playlist_id: str, track_id: str) -> bool:
    state = _load()
    playlists = state.get('playlists', [])
    for pl in playlists:
        if pl.get('id') == playlist_id:
            if track_id not in pl.get('track_ids', []):
                pl.setdefault('track_ids', []).append(track_id)
                state['playlists'] = playlists
                _save(state)
            return True
    return False


def list_tracks_in_playlist(playlist_id: str) -> List[Dict]:
    state = _load()
    playlists = state.get('playlists', [])
    tracks = state.get('tracks', [])
    for pl in playlists:
        if pl.get('id') == playlist_id:
            ids = pl.get('track_ids', [])
            return [t for t in tracks if t.get('id') in ids]
    return []