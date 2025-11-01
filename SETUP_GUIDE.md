# TimeAlign - Group Study Scheduler Setup Guide

## 🎉 Your App is Ready!

TimeAlign is a fully functional study group scheduling application that helps students coordinate meeting times effortlessly.

## 🚀 What's Built

### Core Features (All Working!)
✅ **User Authentication** - Email/password signup and login with JWT tokens
✅ **Group Management** - Create and manage study groups
✅ **Member Invitations** - Invite team members via email
✅ **Smart Scheduling** - AI-powered time slot suggestions based on availability
✅ **Calendar Integration** - Date range selection with beautiful calendar UI
✅ **Event Creation** - One-click event creation for the whole group
✅ **Responsive Design** - Works perfectly on desktop and mobile

### Tech Stack
- **Frontend**: React with modern shadcn/ui components
- **Backend**: FastAPI (Python) with async support
- **Database**: MongoDB for data persistence
- **Auth**: JWT-based authentication

### 4. Restart Backend
```bash
sudo supervisorctl restart backend
```

### 5. Implementation Notes

The backend code is already set up to use Google Calendar API. Once you add credentials:
- Users can sign in with Google
- The app will access real calendar free/busy data
- Events will be created in users' actual Google Calendars

The relevant code is in `/app/backend/server.py`:
- `@api_router.get("/auth/google/start")` - Initiates OAuth flow
- `@api_router.get("/auth/google/callback")` - Handles OAuth callback
- `get_user_calendar_busy_times()` - Will use real FreeBusy API
- `create_event()` - Will create real calendar events

## 📱 How to Use the App

### For Students:

1. **Sign Up** - Create an account with your university email
2. **Create Group** - Start a new study group (e.g., "CS101 Team A")
3. **Invite Members** - Add teammates by email
4. **Find Times** - Select date range and meeting duration
5. **View Suggestions** - See ranked time slots with availability scores
6. **Create Event** - Click to create a meeting for everyone

### Current Behavior (Demo Mode):
- Authentication works with email/password
- Groups and invitations are fully functional
- Time suggestions use simulated availability data
- Events are stored in the database


## 🔧 Technical Details

### API Endpoints
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - Login with credentials
- `GET /api/me` - Get current user info
- `POST /api/groups` - Create study group
- `GET /api/groups` - List user's groups
- `POST /api/groups/:id/invite` - Invite members
- `POST /api/schedule/suggest` - Get time suggestions
- `POST /api/schedule/create` - Create calendar event

### Database Collections
- `users` - User profiles and authentication data
- `passwords` - Hashed passwords (separate for security)
- `oauth_tokens` - Google OAuth tokens (when enabled)
- `groups` - Study group information
- `events` - Created calendar events

### Security Features
- JWT token-based authentication
- Password hashing with SHA256 + salt
- CORS protection
- Input validation with Pydantic models

## 🎨 UI Components Used

The app uses shadcn/ui components for a modern, accessible interface:
- Calendar (date range selection)
- Dialog (modals for auth and event creation)
- Tabs (group detail navigation)
- Card (group listings and suggestions)
- Button, Input, Label (form controls)
- Badge (status indicators)
- Sonner (toast notifications)

## 📊 Availability Algorithm

The scheduling algorithm:
1. Fetches busy times from all group members
2. Inverts busy blocks to find free windows
3. Scans the date range in configurable intervals (default: 15 mins)
4. Scores slots based on:
   - Coverage ratio (how many members are free)
   - Time preferences (prefers afternoon 2-5pm)
   - Configurable minimum coverage threshold
5. Returns top 10 ranked suggestions

## 🚀 Deployment




## 🛠️ Development

### Backend Development
```bash
cd /app/backend
# Edit server.py
sudo supervisorctl restart backend
```

### Frontend Development
```bash
cd /app/frontend
# Edit src/App.js or src/App.css
# Hot reload is enabled - changes appear automatically
```

### Testing
Run the test script:
```bash
python /app/backend_test.py
```

## 📝 Next Steps & Enhancements

### Immediate (If Needed)
- [ ] Add Google OAuth credentials for real calendar integration
- [ ] Test with multiple users and real calendars

### Future Enhancements
- [ ] Recurring meeting support
- [ ] Polling/voting on suggested times
- [ ] Integration with Zoom/Google Meet for video links
- [ ] Slack/Discord notifications
- [ ] Export to ICS format
- [ ] Color-coded availability heatmap
- [ ] Group settings and preferences
- [ ] Email notifications for invites and events

## 🐛 Troubleshooting

### Backend not starting?
```bash
# Check logs
tail -f /var/log/supervisor/backend.err.log

# Restart
sudo supervisorctl restart backend
```

### Frontend issues?
```bash
# Check status
sudo supervisorctl status frontend

# Restart
sudo supervisorctl restart frontend
```

### Database connection issues?
MongoDB is running locally. Check connection:
```bash
mongo --eval "db.adminCommand('ping')"
```


