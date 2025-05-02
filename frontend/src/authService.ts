import { createAuth0Client, Auth0Client, PopupLoginOptions } from "@auth0/auth0-spa-js";
import {user, isAuthenticated, popupOpen} from "./stores/store";
import config from "./auth_config";

let auth0Client : Auth0Client | null = null;

async function getClient() {
    if (auth0Client) {
        return auth0Client;
    }
    auth0Client = await createAuth0Client({
        domain: config.domain,
        clientId: config.clientId   
    })
}

async function checkAuth() {
    const client = await getClient();
    if (!client) return;
    isAuthenticated.set(await client.isAuthenticated());
    user.set((await client.getUser()) || {});
 }

async function createClient() {
    // @ts-ignore
    let auth0Client = await createAuth0Client({
        domain: config.domain,
        clientId: config.clientId
    });

    return auth0Client
}

async function loginWithPopup(options: PopupLoginOptions | undefined) {
    popupOpen.set(true);
    const client = await getClient(); 
    if (!client) return;
    try {
        await client.loginWithPopup(options);
        user.set((await client.getUser()) || {});
        isAuthenticated.set(true);
    } catch (e) {
        console.error("Login with popup error:", e);
        isAuthenticated.set(false); 
        user.set({});
    } finally {
        popupOpen.set(false);
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
    } catch (e) {
         console.error("Logout error:", e);
    }
}

const auth = {
    getClient, 
    checkAuth, 
    loginWithPopup,
    logout
};

export default auth;