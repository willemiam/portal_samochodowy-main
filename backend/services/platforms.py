from flask import Blueprint, request, jsonify
import json
import os
import uuid
from datetime import datetime

platforms_bp = Blueprint('platforms', __name__)

# Path to platforms storage file
PLATFORMS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'platforms.json')

def load_platforms():
    """Load platforms from JSON file"""
    if not os.path.exists(PLATFORMS_FILE):
        return {}
    
    try:
        with open(PLATFORMS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_platforms(platforms):
    """Save platforms to JSON file"""
    os.makedirs(os.path.dirname(PLATFORMS_FILE), exist_ok=True)
    with open(PLATFORMS_FILE, 'w') as f:
        json.dump(platforms, f, indent=2)

@platforms_bp.route('/api/platforms', methods=['POST'])
def create_platform():
    """
    Create a new platform configuration
    
    Request body:
    {
        "platform_config": {
            "name": "...",
            "description": "...",
            "domain": "...",
            "features": {...},
            "domainDetails": {...},
            "advanced": {...}
        }
    }
    
    Response:
    {
        "id": "uuid",
        "message": "Platform created successfully",
        "platform_config": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'platform_config' not in data:
            return jsonify({'error': 'platform_config is required'}), 400
        
        platform_config = data['platform_config']
        
        # Validate required fields
        if not platform_config.get('name'):
            return jsonify({'error': 'Platform name is required'}), 400
        if not platform_config.get('domain'):
            return jsonify({'error': 'Platform domain is required'}), 400
        
        # Generate platform ID
        platform_id = str(uuid.uuid4())
        
        # Load existing platforms
        platforms = load_platforms()
        
        # Create platform entry
        platform_entry = {
            'id': platform_id,
            'platform_config': platform_config,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'previews': []
        }
        
        # Save platform
        platforms[platform_id] = platform_entry
        save_platforms(platforms)
        
        return jsonify({
            'id': platform_id,
            'message': 'Platform created successfully',
            'platform_config': platform_config
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@platforms_bp.route('/api/platforms/<platform_id>', methods=['GET'])
def get_platform(platform_id):
    """
    Get a platform configuration by ID
    
    Response:
    {
        "id": "uuid",
        "platform_config": {...},
        "created_at": "...",
        "updated_at": "...",
        "previews": [...]
    }
    """
    try:
        platforms = load_platforms()
        
        if platform_id not in platforms:
            return jsonify({'error': 'Platform not found'}), 404
        
        return jsonify(platforms[platform_id]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@platforms_bp.route('/api/platforms/<platform_id>/preview', methods=['POST'])
def preview_platform(platform_id):
    """
    Generate a preview for a platform using mock MCP
    
    Request body:
    {
        "domain": "automotive",
        "item_data": {
            "make": "Toyota",
            "model": "Camry",
            "year": "2023"
        }
    }
    
    Response:
    {
        "id": "preview_uuid",
        "enhanced_text": "Mock enhanced description...",
        "sources": [],
        "session_id": "session_uuid",
        "created_at": "..."
    }
    """
    try:
        platforms = load_platforms()
        
        if platform_id not in platforms:
            return jsonify({'error': 'Platform not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        domain = data.get('domain', 'unknown')
        item_data = data.get('item_data', {})
        
        # Generate mock preview
        preview_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        
        # Create mock enhanced text based on domain and item_data
        item_description = ', '.join([f"{k}: {v}" for k, v in item_data.items()])
        enhanced_text = (
            f"[MOCK MCP RESPONSE] Enhanced description for {domain} item. "
            f"Item details: {item_description}. "
            f"This is a simulated AI-enhanced description that would normally come from "
            f"a Model Context Protocol endpoint. The actual implementation would connect "
            f"to a real MCP service to generate contextually relevant, enhanced descriptions "
            f"based on the domain and item data provided."
        )
        
        # Create preview entry
        preview_entry = {
            'id': preview_id,
            'enhanced_text': enhanced_text,
            'sources': [],  # Mock sources - would come from MCP in real implementation
            'session_id': session_id,
            'created_at': datetime.utcnow().isoformat(),
            'domain': domain,
            'item_data': item_data
        }
        
        # Save preview to platform
        platforms[platform_id]['previews'].append(preview_entry)
        platforms[platform_id]['updated_at'] = datetime.utcnow().isoformat()
        save_platforms(platforms)
        
        # Return preview response (without storing full item_data in response)
        response = {
            'id': preview_id,
            'enhanced_text': enhanced_text,
            'sources': [],
            'session_id': session_id,
            'created_at': preview_entry['created_at']
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
