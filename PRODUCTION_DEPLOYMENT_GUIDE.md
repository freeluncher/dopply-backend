# 🚀 PRODUCTION DEPLOYMENT GUIDE - DOPPLY BACKEND

## 📋 ISSUE SUMMARY
**Problem**: Flutter app mendapat error 404 saat request `GET /api/v1/doctors/3/patients`
**Root Cause**: Endpoint tidak tersedia di production server
**Solution**: Deploy perubahan backend yang sudah ditambahkan endpoint

---

## ✅ CHANGES COMMITTED & PUSHED

**Git Commit**: `93898c8` - "fix: Add missing GET /doctors/{doctor_id}/patients endpoint"

**Files Changed**:
- ✅ `app/api/v1/endpoints/doctor_dashboard.py` - Added missing endpoint
- ✅ `DOCTOR_MONITORING_FLOW_TECHNICAL_GUIDE.md` - Technical documentation  
- ✅ `deploy_fix.sh` - Deployment script

**Verification**:
- ✅ Local server: Returns 401 (endpoint exists)
- ❌ Production server: Returns 404 (needs deployment)

---

## 🔧 PRODUCTION DEPLOYMENT STEPS

### **Option 1: Manual Deployment**

```bash
# 1. SSH to production server
ssh root@dopply.my.id
# or
ssh user@your-production-server

# 2. Navigate to backend directory
cd /path/to/dopply-backend

# 3. Pull latest changes
git pull origin main

# 4. Restart backend service (choose one method):

# Method A: SystemD
sudo systemctl restart dopply-backend
sudo systemctl status dopply-backend

# Method B: Supervisor
sudo supervisorctl restart dopply-backend
sudo supervisorctl status dopply-backend

# Method C: PM2
pm2 restart dopply-backend
pm2 status

# Method D: Docker (if using containers)
docker-compose restart backend
docker-compose ps

# Method E: Manual restart (if running uvicorn directly)
pkill -f uvicorn
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

### **Option 2: Automated Deployment**

If you have CI/CD pipeline, trigger deployment or run:

```bash
# GitHub Actions (if configured)
# Push to main branch will auto-deploy

# Or manual webhook trigger
curl -X POST "https://your-deployment-webhook-url" \
     -H "Content-Type: application/json" \
     -d '{"ref": "refs/heads/main"}'
```

---

## 🧪 VERIFICATION STEPS

### **1. Test Endpoint Availability**

```bash
# Test that endpoint now returns 401 instead of 404
curl -X GET "https://dopply.my.id/api/v1/doctors/3/patients" \
     -H "Authorization: Bearer test_token"

# Expected response:
# Status: 401 Unauthorized
# Body: {"status": "error", "code": 401, "message": "Invalid or expired token"}
```

### **2. Test with Valid Authentication**

```bash
# If you have valid doctor token, test full functionality
curl -X GET "https://dopply.my.id/api/v1/doctors/3/patients?limit=10" \
     -H "Authorization: Bearer YOUR_VALID_TOKEN"

# Expected response:
# Status: 200 OK
# Body: {"patients": [...], "total": X, "limit": 10, "offset": 0}
```

### **3. Check Server Logs**

```bash
# Check for any deployment errors
sudo journalctl -f -u dopply-backend

# Or check application logs
tail -f /var/log/dopply/backend.log

# Look for successful startup messages
```

---

## 📱 FRONTEND VERIFICATION

After deployment, test with Flutter app:

1. **Login dengan doctor account**
2. **Navigate to patient selection screen**  
3. **Verify patients list loads successfully**
4. **Check no more 404 errors in app logs**

---

## 🚨 TROUBLESHOOTING

### **If still getting 404 errors:**

```bash
# 1. Verify file changes deployed
grep -n "get_doctor_patients" /path/to/dopply-backend/app/api/v1/endpoints/doctor_dashboard.py

# 2. Check if router is properly included
grep -n "doctor_dashboard" /path/to/dopply-backend/app/main.py

# 3. Restart service again
sudo systemctl restart dopply-backend

# 4. Check for syntax errors
python -m py_compile app/api/v1/endpoints/doctor_dashboard.py
```

### **If getting 500 errors:**

```bash
# Check detailed logs
sudo journalctl -u dopply-backend --since "1 hour ago"

# Check database connectivity
# Check for import errors
# Verify all dependencies installed
```

### **If authentication fails:**

```bash
# Verify token service is working
curl -X GET "https://dopply.my.id/api/v1/token/verify" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📋 SUCCESS CRITERIA

✅ **Deployment successful when:**
- [ ] `GET /doctors/3/patients` returns 401 (not 404)
- [ ] Server logs show no errors during startup
- [ ] Flutter app can load patients list
- [ ] No more 404 errors in mobile app
- [ ] Doctor monitoring flow works end-to-end

---

## 📞 SUPPORT

**If deployment issues persist:**

1. **Check commit verification**: `git log --oneline -5`
2. **Verify remote sync**: `git status` 
3. **Test local vs production**: Run `python test_endpoints_comparison.py`
4. **Contact DevOps/Backend team** with:
   - Server logs
   - Git commit hash
   - Error details

**Expected Resolution Time**: 5-10 minutes after deployment

---

## 🎯 SUMMARY

**Current Status**:
- ✅ Backend fix developed and tested locally
- ✅ Changes committed and pushed to GitHub  
- 🔄 **AWAITING PRODUCTION DEPLOYMENT**

**Next Action**: Deploy to production server using steps above

**Impact**: Resolves Flutter app 404 error and enables doctor monitoring flow
