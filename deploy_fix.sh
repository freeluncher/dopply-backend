#!/usr/bin/env bash

# DEPLOYMENT SCRIPT untuk Dopply Backend
# Untuk mengatasi error 404 pada endpoint /doctors/{doctor_id}/patients

echo "🚀 DOPPLY BACKEND DEPLOYMENT SCRIPT"
echo "=================================="
echo "Target: Resolve 404 error for /doctors/{doctor_id}/patients endpoint"
echo ""

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Not in Dopply backend directory"
    echo "Please run this script from the dopply-backend root directory"
    exit 1
fi

echo "📁 Current directory: $(pwd)"
echo ""

# Step 1: Verify local changes
echo "1️⃣ Verifying local changes..."
if grep -q "get_doctor_patients" app/api/v1/endpoints/doctor_dashboard.py; then
    echo "✅ Local changes confirmed: get_doctor_patients endpoint exists"
else
    echo "❌ Local changes missing: get_doctor_patients endpoint not found"
    exit 1
fi

# Step 2: Check if we're on the main branch
echo ""
echo "2️⃣ Checking git status..."
BRANCH=$(git branch --show-current)
echo "Current branch: $BRANCH"

if [ "$BRANCH" != "main" ]; then
    echo "⚠️  Warning: Not on main branch. Switching to main..."
    git checkout main
fi

# Step 3: Add and commit changes
echo ""
echo "3️⃣ Committing changes..."
git add app/api/v1/endpoints/doctor_dashboard.py
git commit -m "fix: Add missing GET /doctors/{doctor_id}/patients endpoint

- Resolves 404 error when Flutter app requests doctor's patient list
- Adds DoctorPatientsResponse and PatientAssignmentInfo models
- Implements proper authentication and authorization
- Supports search, filtering, and pagination
- Fixes doctor monitoring flow integration issue"

# Step 4: Push to remote
echo ""
echo "4️⃣ Pushing to remote repository..."
git push origin main

echo ""
echo "✅ DEPLOYMENT COMMANDS COMPLETED"
echo ""
echo "📋 NEXT STEPS FOR PRODUCTION DEPLOYMENT:"
echo "1. SSH to production server:"
echo "   ssh user@dopply.my.id"
echo ""
echo "2. Navigate to backend directory:"
echo "   cd /path/to/dopply-backend"
echo ""
echo "3. Pull latest changes:"
echo "   git pull origin main"
echo ""
echo "4. Restart backend service:"
echo "   sudo systemctl restart dopply-backend"
echo "   # OR"
echo "   supervisorctl restart dopply-backend"
echo "   # OR"
echo "   pm2 restart dopply-backend"
echo ""
echo "5. Verify deployment:"
echo "   curl -X GET \"https://dopply.my.id/api/v1/doctors/3/patients\" \\"
echo "        -H \"Authorization: Bearer test_token\""
echo ""
echo "Expected result: 401 Unauthorized (not 404 Not Found)"
echo ""
echo "🎯 ISSUE RESOLUTION:"
echo "After deployment, the Flutter app should successfully load doctor's patients"
echo "without receiving 404 errors."
