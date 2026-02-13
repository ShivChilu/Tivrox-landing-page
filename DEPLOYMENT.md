# TIVROX Deployment Guide for Render

## Quick Overview
This application consists of:
- **Backend**: FastAPI (Python) - handles bookings, admin auth, emails
- **Frontend**: React - landing page + admin dashboard  
- **Database**: MongoDB Atlas (cloud-hosted)

## Deployment Options

### Option 1: Using render.yaml (Recommended)
1. Push the `render.yaml` file to your repository
2. In Render Dashboard, click "New +" → "Blueprint"
3. Connect your repository
4. Render will automatically detect and deploy both services
5. Manually set sensitive environment variables (marked with `sync: false`)

### Option 2: Manual Deployment

#### Backend Deployment
1. **Create Web Service** in Render
2. **Configure**:
   - Runtime: Python 3
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT`
3. **Environment Variables**:
   ```
   MONGO_URL=<your-mongodb-atlas-url>
   DB_NAME=tivrox_db
   CORS_ORIGINS=*
   RESEND_API_KEY=<your-resend-key>
   SENDER_EMAIL=onboarding@resend.dev
   ADMIN_EMAIL=<your-email>
   JWT_SECRET=<your-secret>
   ADMIN_USERNAME=tivrox
   ADMIN_PASSWORD=<your-password>
   ```

#### Frontend Deployment
1. **Create Static Site** in Render
2. **Configure**:
   - Build Command: `cd frontend && yarn install && yarn build`
   - Publish Directory: `frontend/build`
3. **Environment Variables**:
   ```
   REACT_APP_BACKEND_URL=<your-backend-url>
   ```
4. **Add Redirects**: Ensure `/frontend/public/_redirects` exists with:
   ```
   /*    /index.html   200
   ```

## Environment Variables Explained

### Backend Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URL` | MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `DB_NAME` | Database name | `tivrox_db` |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `https://yourfrontend.com` or `*` |
| `RESEND_API_KEY` | Resend API key for emails | `re_xxxxx` |
| `SENDER_EMAIL` | Email sender address | `onboarding@resend.dev` |
| `ADMIN_EMAIL` | Admin notification email | `admin@yourdomain.com` |
| `JWT_SECRET` | Secret for JWT tokens | `your-secret-key` |
| `ADMIN_USERNAME` | Admin dashboard username | `tivrox` |
| `ADMIN_PASSWORD` | Admin dashboard password | `your-secure-password` |

### Frontend Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_BACKEND_URL` | Backend API URL | `https://your-backend.onrender.com` |

## Post-Deployment Checklist

### ✅ Testing Steps
1. **Homepage**: Visit your frontend URL
2. **Booking Form**: Submit a test booking
3. **Email Notifications**: Check if emails are received
4. **Admin Login**: Access `/admin/login` and authenticate
5. **Admin Dashboard**: 
   - View bookings
   - Filter by service/status
   - Update booking status
   - Export CSV
   - Check statistics

### ⚠️ Common Issues

#### 1. CORS Errors
- **Problem**: Frontend can't connect to backend
- **Solution**: Update `CORS_ORIGINS` in backend with your frontend URL

#### 2. Admin Routes 404
- **Problem**: `/admin/login` returns 404
- **Solution**: Ensure `_redirects` file exists in `frontend/public/`

#### 3. Database Connection Failed
- **Problem**: Backend can't connect to MongoDB
- **Solution**: Verify `MONGO_URL` is correct and MongoDB Atlas allows connections from anywhere (IP whitelist: `0.0.0.0/0`)

#### 4. Emails Not Sending
- **Problem**: Booking submitted but no emails
- **Solution**: Check `RESEND_API_KEY` is valid and Resend account is active

## MongoDB Atlas Configuration

1. **Login to MongoDB Atlas**
2. **Network Access**: Add IP `0.0.0.0/0` (allow from anywhere)
3. **Database User**: Ensure user has read/write permissions
4. **Connection String**: Use the connection string in `MONGO_URL`

## Custom Domain Setup (Optional)

### For Frontend
1. In Render dashboard, go to your Static Site
2. Settings → Custom Domains → Add Custom Domain
3. Update DNS records as instructed by Render

### For Backend
1. Go to your Web Service
2. Settings → Custom Domains → Add Custom Domain
3. Update DNS records
4. Update `REACT_APP_BACKEND_URL` in frontend to use new domain

## Security Recommendations

⚠️ **Before Production**:
1. Change `ADMIN_PASSWORD` to a strong password
2. Generate a new `JWT_SECRET` (use: `openssl rand -hex 32`)
3. Set `CORS_ORIGINS` to your specific frontend domain (remove `*`)
4. Consider adding rate limiting at Render level
5. Enable Render's DDoS protection

## Monitoring

- **Backend Logs**: Render Dashboard → Backend Service → Logs
- **Frontend Build Logs**: Render Dashboard → Static Site → Logs
- **Database**: MongoDB Atlas → Monitoring

## Support

- Render Documentation: https://render.com/docs
- MongoDB Atlas: https://www.mongodb.com/docs/atlas/
- Resend: https://resend.com/docs

## Rollback Strategy

If deployment fails:
1. Render keeps previous successful builds
2. Go to Deploys tab → Manual Deploy → Select previous commit
3. Or trigger redeploy from last working commit in Git

---

**Need Help?** Check Render logs first, then verify all environment variables are set correctly.
