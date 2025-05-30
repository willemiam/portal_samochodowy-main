import { createAuth0Client, Auth0Client, PopupLoginOptions } from "@auth0/auth0-spa-js";
import {user, isAuthenticated, popupOpen} from "./stores/store";
import config from "./auth_config";

let auth0Client : Auth0Client | null = null;

async function getClient() {
    console.log('🔧 getClient() called, checking Auth0 config...');
    console.log('🔧 Domain:', config.domain);
    console.log('🔧 Client ID:', config.clientId);
    
    if (!config.domain || !config.clientId) {
        console.warn('⚠️ Auth0 configuration missing - domain or clientId undefined');
        return null;
    }
    
    if (auth0Client) {
        console.log('✅ Returning existing Auth0 client');
        return auth0Client;
    }
      console.log('🏗️ Creating new Auth0 client...');
    auth0Client = await createAuth0Client({
        domain: config.domain,
        clientId: config.clientId,
        authorizationParams: {
            redirect_uri: window.location.origin
        },
        useRefreshTokens: true,
        cacheLocation: 'localstorage'
    });
    console.log('✅ Auth0 client created successfully');
    return auth0Client;
}

async function checkAuth() {
    console.log('🔍 checkAuth() called');
    const client = await getClient();
    if (!client) {
        console.log('❌ No Auth0 client available');
        return;
    }
    
    const isAuth = await client.isAuthenticated();
    const userData = (await client.getUser()) || {};
    
    console.log('🔐 Authentication status:', isAuth);
    console.log('👤 User data:', userData);
    
    isAuthenticated.set(isAuth);
    user.set(userData);
}

async function createClient() {
    // @ts-ignore
    let auth0Client = await createAuth0Client({
        domain: config.domain,
        clientId: config.clientId,
        authorizationParams: {
            redirect_uri: window.location.origin
        },
        useRefreshTokens: true,
        cacheLocation: 'localstorage'
    });

    return auth0Client
}

async function loginWithPopup(options: PopupLoginOptions | undefined) {
    console.log('🚀 Starting login with popup...');
    console.log('🔧 Current window origin:', window.location.origin);
    console.log('🔧 Auth0 domain:', config.domain);
    console.log('🔧 Auth0 client ID:', config.clientId);
    
    popupOpen.set(true);
    const client = await getClient(); 
    if (!client) {
        console.log('❌ No Auth0 client available for login');
        return;
    }
    try {
        console.log('📝 Calling Auth0 loginWithPopup...');
        await client.loginWithPopup(options);
        console.log('✅ Login successful, checking auth state...');
        // Call checkAuth to properly update authentication state
        await checkAuth();    } catch (e: any) {
        console.error("❌ Login with popup error:", e);
        console.error("❌ Error details:", {
            message: e.message,
            stack: e.stack,
            name: e.name
        });
        
        // Provide specific error guidance
        if (e.message?.includes('Unauthorized') || e.message?.includes('401')) {
            console.error("🔧 Auth0 Configuration Issue Detected!");
            console.error("📋 Required fixes:");
            console.error("   1. Set Application Type to 'Single Page Application'");
            console.error("   2. Add allowed callback URLs: " + window.location.origin);
            console.error("   3. Add allowed web origins: " + window.location.origin);
            console.error("   4. Add allowed CORS origins: " + window.location.origin);
            console.error("📖 See auth0-configuration-fix.md for detailed instructions");
        }
        
        isAuthenticated.set(false); 
        user.set({});
    } finally {
        popupOpen.set(false);
        console.log('🏁 Login process completed');
    }
}

async function logout() { 
    const client = await getClient();
    if (!client) return; 
     try {
        await client.logout({
           logoutParams: {
             returnTo: window.location.origin // Redirect back to the app's origin after logout
           }
        });
        isAuthenticated.set(false);
        user.set({});
    } catch (e: any) {
         console.error("Logout error:", e);
    }
}

async function getAccessToken() {
    const client = await getClient();
    if (!client) return null;
    
    try {
        const token = await client.getTokenSilently();
        return token;
    } catch (e) {
        console.error("Error getting access token:", e);
        return null;
    }
}

const auth = {
    getClient, 
    checkAuth, 
    loginWithPopup,
    logout,
    getAccessToken
};

export default auth;