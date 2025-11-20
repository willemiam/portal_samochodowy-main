"""
Platform configuration and preview service
Handles platform creation and mock MCP preview generation
"""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

# Storage file path
DATA_DIR = Path(__file__).parent.parent / 'data'
PLATFORMS_FILE = DATA_DIR / 'platforms.json'

def ensure_storage():
    """Ensure data directory and storage file exist"""
    DATA_DIR.mkdir(exist_ok=True)
    if not PLATFORMS_FILE.exists():
        PLATFORMS_FILE.write_text(json.dumps({}))

def load_platforms():
    """Load all platforms from storage"""
    ensure_storage()
    try:
        with open(PLATFORMS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_platforms(platforms):
    """Save platforms to storage"""
    ensure_storage()
    with open(PLATFORMS_FILE, 'w') as f:
        json.dump(platforms, f, indent=2)

def create_platform(config):
    """Create a new platform configuration
    
    Args:
        config: Platform configuration dict
        
    Returns:
        dict: Platform object with id and metadata
    """
    platform_id = str(uuid.uuid4())
    platforms = load_platforms()
    
    platform = {
        'id': platform_id,
        'config': config,
        'created_at': datetime.utcnow().isoformat(),
        'previews': []
    }
    
    platforms[platform_id] = platform
    save_platforms(platforms)
    
    return platform

def get_platform(platform_id):
    """Get a platform by ID
    
    Args:
        platform_id: Platform UUID
        
    Returns:
        dict: Platform object or None
    """
    platforms = load_platforms()
    return platforms.get(platform_id)

def generate_preview(platform_id, domain, item_data):
    """Generate mock preview using item data
    
    This is a mock implementation that will be replaced with real MCP integration
    
    Args:
        platform_id: Platform UUID
        domain: Domain name (e.g., 'automotive')
        item_data: Item data dict
        
    Returns:
        dict: Preview result with enhanced_text, sources, and session_id
    """
    platforms = load_platforms()
    platform = platforms.get(platform_id)
    
    if not platform:
        raise ValueError(f"Platform {platform_id} not found")
    
    # Mock MCP enhancement - create a simple template-based enhanced text
    item_name = item_data.get('name', 'Unknown Item')
    
    # Build a description from available data
    description_parts = [f"[MOCK ENHANCED] {item_name}"]
    
    for key, value in item_data.items():
        if key != 'name' and value:
            description_parts.append(f"{key}: {value}")
    
    enhanced_text = " — ".join(description_parts)
    enhanced_text += f"\n\nThis is a mock preview for the '{domain}' domain. "
    enhanced_text += "In production, this would be enhanced by MCP with AI-powered descriptions, "
    enhanced_text += "enriched data, and contextual information."
    
    # Create preview result
    session_id = str(uuid.uuid4())
    preview_result = {
        'enhanced_text': enhanced_text,
        'sources': [],  # Mock empty sources
        'session_id': session_id,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Save preview to platform record
    platform['previews'].append({
        'session_id': session_id,
        'domain': domain,
        'item_data': item_data,
        'result': preview_result,
        'created_at': datetime.utcnow().isoformat()
    })
    
    platforms[platform_id] = platform
    save_platforms(platforms)
    
    return preview_result
