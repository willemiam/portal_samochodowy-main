"""
Auth0 JWT Token Validation Middleware for Flask
Validates JWT tokens from Auth0 and extracts user information
"""

import json
import jwt
import requests
from functools import wraps
from flask import request, jsonify, current_app
from urllib.request import urlopen
from models import Users
from app import db


class AuthError(Exception):
    """Custom Auth Error Exception"""
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header"""
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


def verify_decode_jwt(token, auth0_domain):
    """Decodes and verifies JWT token from Auth0"""
    try:
        # Get Auth0 public keys
        jsonurl = urlopen(f'https://{auth0_domain}/.well-known/jwks.json')
        jwks = json.loads(jsonurl.read())
        
        # Get the key id from token header
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        
        if 'kid' not in unverified_header:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Authorization malformed.'
            }, 401)

        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                rsa_key = {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }
                break
                
        if rsa_key:
            from jose import jwt as jose_jwt
            payload = jose_jwt.decode(
                token,
                rsa_key,
                algorithms=['RS256'],
                audience=current_app.config.get('AUTH0_AUDIENCE'),
                issuer=f'https://{auth0_domain}/'
            )
            return payload
            
    except jose_jwt.ExpiredSignatureError:
        raise AuthError({
            'code': 'token_expired',
            'description': 'Token expired.'
        }, 401)

    except jose_jwt.JWTClaimsError:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Incorrect claims. Please, check the audience and issuer.'
        }, 401)
    except Exception:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Unable to parse authentication token.'
        }, 400)

    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)


def get_or_create_user(auth0_user_data):
    """Get existing user or create new user from Auth0 data"""
    email = auth0_user_data.get('email')
    auth0_sub = auth0_user_data.get('sub')  # Auth0 user ID
    
    if not email:
        raise AuthError({
            'code': 'invalid_user_data',
            'description': 'User email not found in token.'
        }, 400)
    
    # Try to find user by email
    user = Users.query.filter_by(email=email).first()
    
    if not user:
        # Create new user from Auth0 data
        name_parts = auth0_user_data.get('name', '').split(' ', 1)
        first_name = name_parts[0] if name_parts else 'User'
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        user = Users(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash='auth0_user'  # Auth0 users don't have local passwords
        )
        
        db.session.add(user)
        db.session.commit()
        
        print(f"Created new user from Auth0: {email}")
    
    return user


def requires_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # For development - allow testing without auth
            if current_app.config.get('TESTING') or current_app.config.get('DISABLE_AUTH'):
                # Use test user for development
                test_user = Users.query.first()
                if not test_user:
                    test_user = Users(
                        first_name='Test',
                        last_name='User', 
                        email='test@example.com',
                        password_hash='test'
                    )
                    db.session.add(test_user)
                    db.session.commit()
                request.current_user = test_user
                return f(*args, **kwargs)
            
            # Production auth flow
            token = get_token_auth_header()
            auth0_domain = current_app.config.get('AUTH0_DOMAIN')
            
            if not auth0_domain:
                raise AuthError({
                    'code': 'auth0_not_configured',
                    'description': 'Auth0 domain not configured.'
                }, 500)
            
            payload = verify_decode_jwt(token, auth0_domain)
            user = get_or_create_user(payload)
            request.current_user = user
            
            return f(*args, **kwargs)
            
        except AuthError as e:
            return jsonify(e.error), e.status_code
        except Exception as e:
            return jsonify({
                'code': 'auth_error',
                'description': str(e)
            }), 500
    
    return decorated


def requires_auth_optional(f):
    """Decorator for optional authentication - sets user if token present"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = get_token_auth_header()
            auth0_domain = current_app.config.get('AUTH0_DOMAIN')
            
            if token and auth0_domain:
                payload = verify_decode_jwt(token, auth0_domain)
                user = get_or_create_user(payload)
                request.current_user = user
            else:
                request.current_user = None
                
        except (AuthError, Exception):
            # If auth fails, continue without user
            request.current_user = None
            
        return f(*args, **kwargs)
    
    return decorated
