const config = {
    domain:  import.meta.env.VITE_AUTH0_DOMAIN,
    clientId: import.meta.env.VITE_AUTH0_CLIENT_ID
}

console.log('Auth Config Loaded:', config);

export default config;