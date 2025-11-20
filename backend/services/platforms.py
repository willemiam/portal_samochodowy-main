"""
Platform Creator API Blueprint
Provides endpoints for creating and managing platforms with file-based JSON storage.
"""
from flask import Blueprint, request, jsonify
import json
import os
import uuid
from datetime import datetime

platforms_bp = Blueprint('platforms', __name__)

# Path to JSON storage file
PLATFORMS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'platforms.json')

def load_platforms():
    """Load platforms from JSON file."""
    if not os.path.exists(PLATFORMS_FILE):
        return {}
    try:
        with open(PLATFORMS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_platforms(platforms):
    """Save platforms to JSON file."""
    os.makedirs(os.path.dirname(PLATFORMS_FILE), exist_ok=True)
    with open(PLATFORMS_FILE, 'w') as f:
        json.dump(platforms, f, indent=2)

@platforms_bp.route('/api/platforms', methods=['POST'])
def create_platform():
    """
    Create a new platform.
    Request body should contain platform configuration data.
    Returns: JSON with platform id and created_at timestamp.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Generate unique ID for the platform
        platform_id = str(uuid.uuid4())
        
        # Load existing platforms
        platforms = load_platforms()
        
        # Create platform object
        platform = {
            'id': platform_id,
            'data': data,
            'previews': [],
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Save platform
        platforms[platform_id] = platform
        save_platforms(platforms)
        
        return jsonify({
            'id': platform_id,
            'created_at': platform['created_at']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@platforms_bp.route('/api/platforms/<platform_id>', methods=['GET'])
def get_platform(platform_id):
    """
    Get a specific platform by ID.
    Returns: JSON with platform data.
    """
    try:
        platforms = load_platforms()
        
        if platform_id not in platforms:
            return jsonify({'error': 'Platform not found'}), 404
        
        return jsonify(platforms[platform_id]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@platforms_bp.route('/api/platforms/<platform_id>/preview', methods=['POST'])
def create_preview(platform_id):
    """
    Generate a preview for a platform.
    This is a mock implementation that returns enhanced text and session ID.
    Returns: JSON with id, enhanced_text, sources, session_id, and created_at.
    """
    try:
        platforms = load_platforms()
        
        if platform_id not in platforms:
            return jsonify({'error': 'Platform not found'}), 404
        
        # Generate mock preview data
        preview_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        
        platform_data = platforms[platform_id]['data']
        platform_name = platform_data.get('name', 'Unnamed Platform')
        platform_domain = platform_data.get('domain', 'general')
        
        # Create mock enhanced text based on platform data
        enhanced_text = f"""
# Platform Preview: {platform_name}

## Overview
This is a mock preview for the {platform_name} platform in the {platform_domain} domain.

## Features
The platform has been configured with the following capabilities:
- Enhanced AI processing
- Real-time data analysis
- Custom domain integration

## Status
Preview generated successfully. This is a placeholder for actual AI-enhanced content.
        """.strip()
        
        preview = {
            'id': preview_id,
            'platform_id': platform_id,
            'enhanced_text': enhanced_text,
            'sources': [],
            'session_id': session_id,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Append preview to platform's previews list
        platforms[platform_id]['previews'].append(preview)
        save_platforms(platforms)
        
        return jsonify(preview), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
