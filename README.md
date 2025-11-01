#                TimeAlign - Group Study Scheduler

<div align="center">
  <h3>🎯 Find the Perfect Time for Your Study Group</h3>
  <p>Stop the endless back-and-forth. TimeAlign automatically finds when everyone's available.</p>
  
  [![Live Demo](https://img.shields.io/badge/demo-live-green)](https://timealign.preview.emergentagent.com)
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
</div>

## 🚀 Features

### Core Functionality
- ✅ **Smart Scheduling** - AI-powered algorithm finds optimal meeting times
- ✅ **Group Management** - Create and manage multiple study groups
- ✅ **Member Invitations** - Invite teammates via email
- ✅ **Calendar Integration** - Beautiful date picker with range selection
- ✅ **Event Creation** - One-click event creation for all members
- ✅ **Time Zone Support** - Automatic timezone normalization

### DevOps Pipeline
- ✅ **CI/CD Integration** - GitHub Actions workflows included
- ✅ **Automated Testing** - Unit, integration, and E2E tests
- ✅ **Deployment Tracking** - Built-in deployment monitoring
- ✅ **Environment Management** - Preview and production environments
- ✅ **Health Monitoring** - API health checks and status tracking

## 🏗️ Tech Stack

### Frontend
- **React** - Modern UI library
- **shadcn/ui** - Beautiful, accessible components
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client
- **React Router** - Client-side routing

### Backend
- **FastAPI** - High-performance Python API framework
- **MongoDB** - NoSQL database with Motor (async driver)
- **JWT** - Token-based authentication
- **Pydantic** - Data validation

### DevOps
- **GitHub Actions** - CI/CD automation
- **Docker** - Containerization (optional)
- **Supervisor** - Process management

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/timealign.git
cd timealign

# Backend setup
cd backend
pip install -r requirements.txt
cp .env.example .env  # Configure your environment variables

# Frontend setup
cd ../frontend
yarn install
cp .env.example .env  # Configure your environment variables

# Start services (using supervisor)
sudo supervisorctl start all

# Or manually:
# Terminal 1 - Backend
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001

# Terminal 2 - Frontend
cd frontend
yarn start
```

## 🔧 Configuration

### Backend Environment Variables (`backend/.env`)

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=timealign_db
CORS_ORIGINS=*
JWT_SECRET=your-secret-key-change-in-production

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback
```

### Frontend Environment Variables (`frontend/.env`)

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=.

# Frontend tests
cd frontend
yarn test

# E2E tests
cd frontend
npx playwright test
```

## 🚀 Deployment

### Option 1: GitHub Actions (Recommended)

See [DEVOPS_SETUP.md](DEVOPS_SETUP.md) for complete CI/CD setup.

1. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/timealign.git
   git push -u origin main
   ```

2. **Configure GitHub Secrets**
   - `DEPLOYMENT_TOKEN`
   - `MONGO_URL`
   - `DB_NAME`

3. **Set up Environments**
   - `preview` - Auto-deploy from `develop` branch
   - `production` - Manual approval from `main` branch

4. **Deploy**
   ```bash
   # Deploy to preview
   git checkout develop
   git push origin develop
   
   # Deploy to production
   git checkout main
   git merge develop
   git push origin main
   ```

### Option 2: Manual Deployment

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for manual deployment instructions.

## 📊 Project Structure

```
timealign/
├── .github/
│   └── workflows/          # GitHub Actions CI/CD
│       ├── ci.yml
│       ├── test.yml
│       ├── deploy-preview.yml
│       └── deploy-production.yml
├── backend/
│   ├── server.py          # Main FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js        # Main React component
│   │   ├── App.css       # Styles
│   │   └── components/   # UI components
│   ├── package.json      # Node dependencies
│   └── .env             # Environment variables
├── tests/                # Test files
├── DEVOPS_SETUP.md      # DevOps setup guide
├── SETUP_GUIDE.md       # General setup guide
└── README.md            # This file
```

## 🎯 Usage

### For Students

1. **Sign Up** - Create an account with your email
2. **Create Group** - Start a new study group
3. **Invite Members** - Add teammates by email
4. **Find Times** - Select date range and duration
5. **Create Event** - Choose a suggested time slot and create event

### For Developers

1. **Groups Tab** - Manage study groups and scheduling
2. **DevOps Tab** - Monitor CI/CD pipeline and deployments
   - **Overview** - Environment status and pipeline health
   - **Deployment History** - View past deployments
   - **Setup Guide** - Step-by-step DevOps configuration

## 📖 API Documentation

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Login
- `GET /api/auth/google/start` - Initiate Google OAuth
- `GET /api/me` - Get current user

### Groups
- `GET /api/groups` - List user's groups
- `POST /api/groups` - Create group
- `GET /api/groups/:id` - Get group details
- `POST /api/groups/:id/invite` - Invite members

### Scheduling
- `POST /api/schedule/suggest` - Get time suggestions
- `POST /api/schedule/create` - Create calendar event

### DevOps
- `GET /api/health` - Health check
- `GET /api/deployments` - Deployment history
- `POST /api/deployments` - Create deployment record

## 🔐 Security

- JWT-based authentication
- Password hashing with SHA256
- CORS protection
- Input validation with Pydantic
- Environment variable management
- Secret management via GitHub Secrets

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Emergent](https://emergent.sh)
- UI components from [shadcn/ui](https://ui.shadcn.com)
- Icons from [Lucide](https://lucide.dev)

## 📞 Support

- 📧 Email: support@timealign.app
- 🐛 Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/timealign/issues)
- 📚 Docs: [Setup Guide](SETUP_GUIDE.md) | [DevOps Guide](DEVOPS_SETUP.md)

---

<div align="center">
  <p>Made with ❤️ by students, for students</p>
  <p>⭐ Star us on GitHub if this helped you!</p>
</div>
