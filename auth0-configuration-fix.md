# 🔐 Auth0 Configuration Fix Guide

**Issue**: 401 Unauthorized error during Auth0 login popup
**Error**: `POST https://dev-xy7eii07l2th1yfm.us.auth0.com/oauth/token 401 (Unauthorized)`

## 🎯 Root Cause
The 401 error indicates that your Auth0 application configuration is missing required settings for the Single Page Application (SPA) authentication flow.

## ✅ Required Auth0 Application Settings

### 1. **Application Type**
- **Must be**: Single Page Application (SPA)
- **Not**: Regular Web Application, Machine to Machine, or Native

### 2. **Allowed Callback URLs**
Add these URLs to your Auth0 application settings:
```
http://localhost:5173
http://localhost:5174
http://localhost:3000
```

### 3. **Allowed Web Origins**
Add these URLs:
```
http://localhost:5173
http://localhost:5174
http://localhost:3000
```

### 4. **Allowed Origins (CORS)**
Add these URLs:
```
http://localhost:5173
http://localhost:5174
http://localhost:3000
```

### 5. **Allowed Logout URLs**
Add these URLs:
```
http://localhost:5173
http://localhost:5174
http://localhost:3000
```

## 🔧 Step-by-Step Auth0 Setup

### Step 1: Access Auth0 Dashboard
1. Go to [Auth0 Dashboard](https://manage.auth0.com/)
2. Navigate to **Applications** → **Applications**
3. Find your application: `PUFmYfq51AI30rTBeXE2YCpFJNJTvoEm`

### Step 2: Verify Application Type
1. Click on your application
2. Go to **Settings** tab
3. **Application Type** should be **Single Page Application**
4. If not, change it to **Single Page Application**

### Step 3: Configure URLs
In the **Application URIs** section:

**Allowed Callback URLs**:
```
http://localhost:5173, http://localhost:5174, http://localhost:3000
```

**Allowed Logout URLs**:
```
http://localhost:5173, http://localhost:5174, http://localhost:3000
```

**Allowed Web Origins**:
```
http://localhost:5173, http://localhost:5174, http://localhost:3000
```

**Allowed Origins (CORS)**:
```
http://localhost:5173, http://localhost:5174, http://localhost:3000
```

### Step 4: Advanced Settings
Scroll down to **Advanced Settings**:

1. **Grant Types** - Ensure these are checked:
   - ✅ Authorization Code
   - ✅ Refresh Token
   - ✅ Implicit (for compatibility)

### Step 4b: Credentials Settings (CRITICAL FOR SPA)
Navigate to **Credentials** tab:

1. **Application Authentication**:
   - **Token Endpoint Authentication Method**: Select **None** (for SPA)
   - ⚠️ **IMPORTANT**: This setting was moved from Advanced Settings to Credentials > Application Authentication in recent Auth0 updates
   - If this is set to "POST" or "Basic", you will get 401 Unauthorized errors during token exchange

### Step 5: Save Changes
1. Click **Save Changes** at the bottom
2. Wait for the configuration to propagate (usually immediate)

## 🧪 Test the Fix

After updating Auth0 settings:

1. **Restart your development server**:
   ```bash
   # Stop current server (Ctrl+C)
   cd "c:\Users\patst\source\repos\inz\portal_samochodowy-main\frontend"
   npm run dev
   ```

2. **Clear browser cache and localStorage**:
   - Open DevTools (F12)
   - Go to Application tab
   - Clear Local Storage and Session Storage
   - Close and reopen browser

3. **Test authentication**:
   - Navigate to: http://localhost:5174/addItem
   - Click "Zaloguj się" 
   - Should now work without 401 error

## 🔍 Alternative Diagnosis

If the above doesn't work, the issue might be:

### Check 1: Domain Configuration
Verify your Auth0 domain is correct:
- Your domain: `dev-xy7eii07l2th1yfm.us.auth0.com`
- Should match exactly in Auth0 dashboard

### Check 2: Client ID
Verify your Client ID is correct:
- Your Client ID: `PUFmYfq51AI30rTBeXE2YCpFJNJTvoEm`
- Should match exactly in Auth0 application settings

### Check 3: Test with Simple Configuration
Try this minimal test configuration in `authService.ts`:

```typescript
auth0Client = await createAuth0Client({
    domain: 'dev-xy7eii07l2th1yfm.us.auth0.com',
    clientId: 'PUFmYfq51AI30rTBeXE2YCpFJNJTvoEm',
    authorizationParams: {
        redirect_uri: window.location.origin
    }
});
```

## 🚨 Common Auth0 SPA Mistakes

1. **Wrong Application Type**: Using "Regular Web Application" instead of "Single Page Application"
2. **Missing Callback URLs**: Not adding localhost URLs to allowed callbacks
3. **CORS Issues**: Not adding localhost to allowed origins
4. **Grant Types**: Not enabling proper grant types for SPA
5. **Authentication Method**: Using "POST" instead of "None" for SPA

## 📞 If Still Not Working

1. **Check Auth0 Logs**:
   - Go to Auth0 Dashboard → Monitoring → Logs
   - Look for failed authentication attempts
   - Check error details

2. **Enable Debug Mode**:
   ```typescript
   // Add to authService.ts
   const auth0Client = await createAuth0Client({
       domain: config.domain,
       clientId: config.clientId,
       authorizationParams: {
           redirect_uri: window.location.origin
       },
       cacheLocation: 'localstorage',
       useRefreshTokens: true
   });
   ```

3. **Contact Support**:
   - Provide Auth0 domain and Client ID
   - Share the exact error message
   - Include Auth0 application configuration screenshot

---

**Expected Result**: After proper Auth0 configuration, the login popup should work without 401 errors and authentication state should update correctly.
