from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
from passlib.context import CryptContext
import hashlib
import httpx
from urllib.parse import urlencode

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# JWT Secret
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
# Use a simpler approach for password hashing to avoid bcrypt issues
def hash_password(password: str) -> str:
    """Simple password hashing using SHA256 with salt"""
    salt = "timealign_salt_2025"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

# Google OAuth Config (placeholder - user will add later)
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'placeholder-client-id')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'placeholder-secret')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:3000/auth/callback')

# ===== Models =====
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    google_id: Optional[str] = None
    email: EmailStr
    name: str
    timezone: str = "UTC"
    avatar_url: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    timezone: str
    avatar_url: Optional[str] = None

class OAuthToken(BaseModel):
    user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    expiry: str
    token_type: str = "Bearer"

class Group(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    owner_id: str
    member_ids: List[str] = []
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class GroupCreate(BaseModel):
    name: str

class GroupInvite(BaseModel):
    emails: List[EmailStr]

class GroupResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    member_ids: List[str]
    members: List[UserResponse] = []
    created_at: str

class ScheduleSuggestRequest(BaseModel):
    group_id: str
    range_start: str  # ISO format
    range_end: str    # ISO format
    duration_mins: int = 60
    granularity_mins: int = 15
    min_coverage: float = 0.8

class TimeSlot(BaseModel):
    start: str
    end: str
    score: float
    available_members: int
    total_members: int
    coverage_ratio: float

class CreateEventRequest(BaseModel):
    group_id: str
    start: str
    end: str
    title: str
    description: Optional[str] = None
    location: Optional[str] = None

class DeploymentRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    environment: str  # preview, production
    branch: str
    commit: str
    status: str  # success, failure, in_progress
    deployed_by: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    duration_seconds: Optional[int] = None

class DeploymentCreate(BaseModel):
    environment: str
    branch: str
    commit: str
    status: str
    deployed_by: str
    duration_seconds: Optional[int] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    timezone: str = "UTC"

# ===== Helper Functions =====
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_user_calendar_busy_times(user_id: str, time_min: str, time_max: str) -> List[Dict]:
    """Mock implementation - will be replaced with actual Google Calendar API"""
    # For demo purposes, return some sample busy blocks
    token_doc = await db.oauth_tokens.find_one({"user_id": user_id})
    if not token_doc:
        return []
    
    # In production, this would call Google Calendar FreeBusy API
    # For now, return mock data
    import random
    busy_blocks = []
    
    # Simulate some random busy times
    start_dt = datetime.fromisoformat(time_min.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(time_max.replace('Z', '+00:00'))
    
    current = start_dt
    while current < end_dt:
        if random.random() < 0.3:  # 30% chance of being busy
            busy_start = current
            busy_end = current + timedelta(hours=random.randint(1, 3))
            busy_blocks.append({
                "start": busy_start.isoformat(),
                "end": min(busy_end, end_dt).isoformat()
            })
            current = busy_end
        else:
            current += timedelta(hours=1)
    
    return busy_blocks

def find_available_slots(all_busy_times: Dict[str, List[Dict]], 
                         range_start: str, 
                         range_end: str,
                         duration_mins: int,
                         granularity_mins: int,
                         min_coverage: float,
                         total_members: int) -> List[TimeSlot]:
    """Algorithm to find best meeting times"""
    
    start_dt = datetime.fromisoformat(range_start.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(range_end.replace('Z', '+00:00'))
    duration_delta = timedelta(minutes=duration_mins)
    granularity_delta = timedelta(minutes=granularity_mins)
    
    candidates = []
    current = start_dt
    
    while current + duration_delta <= end_dt:
        slot_start = current
        slot_end = current + duration_delta
        
        # Count how many members are available
        available_count = 0
        for user_id, busy_blocks in all_busy_times.items():
            is_available = True
            for busy in busy_blocks:
                busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                
                # Check if slot overlaps with busy time
                if not (slot_end <= busy_start or slot_start >= busy_end):
                    is_available = False
                    break
            
            if is_available:
                available_count += 1
        
        coverage_ratio = available_count / total_members if total_members > 0 else 0
        
        # Only consider slots meeting minimum coverage
        if coverage_ratio >= min_coverage:
            # Calculate score based on coverage and time preferences
            # Prefer afternoon times (14:00-17:00) slightly
            hour = slot_start.hour
            time_pref_score = 1.0
            if 14 <= hour <= 17:
                time_pref_score = 1.2
            elif hour < 9 or hour > 20:
                time_pref_score = 0.5
            
            score = coverage_ratio * 0.7 + (time_pref_score / 1.2) * 0.3
            
            candidates.append(TimeSlot(
                start=slot_start.isoformat(),
                end=slot_end.isoformat(),
                score=score,
                available_members=available_count,
                total_members=total_members,
                coverage_ratio=coverage_ratio
            ))
        
        current += granularity_delta
    
    # Sort by score and return top slots
    candidates.sort(key=lambda x: x.score, reverse=True)
    return candidates[:10]  # Return top 10

# ===== Auth Routes =====
@api_router.post("/auth/signup")
async def signup(signup_data: SignupRequest):
    # Check if user exists
    existing = await db.users.find_one({"email": signup_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=signup_data.email,
        name=signup_data.name,
        timezone=signup_data.timezone
    )
    
    # Hash password and store separately
    hashed_password = hash_password(signup_data.password)
    await db.users.insert_one(user.dict())
    await db.passwords.insert_one({"user_id": user.id, "hashed_password": hashed_password})
    
    # Create token
    access_token = create_access_token({"user_id": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user.dict())
    }

@api_router.post("/auth/login")
async def login(login_data: LoginRequest):
    # Find user
    user = await db.users.find_one({"email": login_data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    password_doc = await db.passwords.find_one({"user_id": user["id"]})
    if not password_doc or not verify_password(login_data.password, password_doc["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    access_token = create_access_token({"user_id": user["id"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user)
    }

@api_router.get("/auth/google/start")
async def google_auth_start():
    """Returns Google OAuth URL"""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/calendar.events",
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return {"auth_url": auth_url}

@api_router.get("/auth/google/callback")
async def google_auth_callback(code: str):
    """Handle Google OAuth callback"""
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in", 3600)
        
        # Get user info
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_info_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        user_info = user_info_response.json()
        
        # Find or create user
        google_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name")
        avatar_url = user_info.get("picture")
        
        user = await db.users.find_one({"google_id": google_id})
        
        if not user:
            # Create new user
            new_user = User(
                google_id=google_id,
                email=email,
                name=name,
                avatar_url=avatar_url
            )
            await db.users.insert_one(new_user.dict())
            user = new_user.dict()
        
        # Store tokens
        expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        oauth_token = OAuthToken(
            user_id=user["id"],
            access_token=access_token,
            refresh_token=refresh_token,
            expiry=expiry.isoformat()
        )
        
        await db.oauth_tokens.update_one(
            {"user_id": user["id"]},
            {"$set": oauth_token.dict()},
            upsert=True
        )
        
        # Create JWT
        jwt_token = create_access_token({"user_id": user["id"]})
        
        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": UserResponse(**user)
        }

@api_router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

# ===== Group Routes =====
@api_router.get("/groups", response_model=List[GroupResponse])
async def get_groups(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    # Find groups where user is owner or member
    groups = await db.groups.find({
        "$or": [
            {"owner_id": user_id},
            {"member_ids": user_id}
        ]
    }).to_list(1000)
    
    # Populate members
    result = []
    for group in groups:
        member_ids = [group["owner_id"]] + group.get("member_ids", [])
        members = await db.users.find({"id": {"$in": member_ids}}).to_list(1000)
        
        group["members"] = [UserResponse(**m) for m in members]
        result.append(GroupResponse(**group))
    
    return result

@api_router.post("/groups", response_model=GroupResponse)
async def create_group(group_data: GroupCreate, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    group = Group(
        name=group_data.name,
        owner_id=user_id,
        member_ids=[user_id]  # Owner is also a member
    )
    
    await db.groups.insert_one(group.dict())
    
    # Get owner info
    owner = await db.users.find_one({"id": user_id})
    
    return GroupResponse(
        **group.dict(),
        members=[UserResponse(**owner)]
    )

@api_router.get("/groups/{group_id}", response_model=GroupResponse)
async def get_group(group_id: str, current_user: dict = Depends(get_current_user)):
    group = await db.groups.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user is member
    user_id = current_user["id"]
    if user_id != group["owner_id"] and user_id not in group.get("member_ids", []):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    # Get members
    member_ids = [group["owner_id"]] + group.get("member_ids", [])
    members = await db.users.find({"id": {"$in": list(set(member_ids))}}).to_list(1000)
    
    return GroupResponse(
        **group,
        members=[UserResponse(**m) for m in members]
    )

@api_router.post("/groups/{group_id}/invite")
async def invite_to_group(group_id: str, invite_data: GroupInvite, current_user: dict = Depends(get_current_user)):
    group = await db.groups.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user is owner
    if current_user["id"] != group["owner_id"]:
        raise HTTPException(status_code=403, detail="Only group owner can invite members")
    
    # Find users by email and add to group
    invited_users = []
    for email in invite_data.emails:
        user = await db.users.find_one({"email": email})
        if user and user["id"] not in group.get("member_ids", []):
            await db.groups.update_one(
                {"id": group_id},
                {"$addToSet": {"member_ids": user["id"]}}
            )
            invited_users.append(user["email"])
    
    return {"message": f"Invited {len(invited_users)} users", "invited": invited_users}

# ===== Schedule Routes =====
@api_router.post("/schedule/suggest", response_model=List[TimeSlot])
async def suggest_times(request: ScheduleSuggestRequest, current_user: dict = Depends(get_current_user)):
    # Get group
    group = await db.groups.find_one({"id": request.group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Get all members
    member_ids = list(set([group["owner_id"]] + group.get("member_ids", [])))
    
    # Get busy times for each member
    all_busy_times = {}
    for member_id in member_ids:
        busy_times = await get_user_calendar_busy_times(
            member_id,
            request.range_start,
            request.range_end
        )
        all_busy_times[member_id] = busy_times
    
    # Find available slots
    slots = find_available_slots(
        all_busy_times,
        request.range_start,
        request.range_end,
        request.duration_mins,
        request.granularity_mins,
        request.min_coverage,
        len(member_ids)
    )
    
    return slots

@api_router.post("/schedule/create")
async def create_event(request: CreateEventRequest, current_user: dict = Depends(get_current_user)):
    # Get group
    group = await db.groups.find_one({"id": request.group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Get all members
    member_ids = list(set([group["owner_id"]] + group.get("member_ids", [])))
    members = await db.users.find({"id": {"$in": member_ids}}).to_list(1000)
    
    # In production, this would create a Google Calendar event
    # For demo, just store in database
    event = {
        "id": str(uuid.uuid4()),
        "group_id": request.group_id,
        "title": request.title,
        "description": request.description,
        "location": request.location,
        "start": request.start,
        "end": request.end,
        "attendees": [m.get("email", "") for m in members if m.get("email")],
        "created_by": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.events.insert_one(event)
    
    return {
        "message": "Event created successfully",
        "event_id": event["id"]
    }

# ===== DevOps / Deployment Routes =====
@api_router.post("/deployments")
async def create_deployment_record(deployment: DeploymentCreate):
    """Create a deployment record (called by CI/CD pipeline)"""
    record = DeploymentRecord(**deployment.dict())
    await db.deployments.insert_one(record.dict())
    return {"message": "Deployment recorded", "id": record.id}

@api_router.get("/deployments")
async def get_deployments(limit: int = 20, environment: Optional[str] = None):
    """Get deployment history"""
    query = {}
    if environment:
        query["environment"] = environment
    
    deployments = await db.deployments.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    return [DeploymentRecord(**d) for d in deployments]

@api_router.get("/deployments/latest")
async def get_latest_deployments():
    """Get latest deployment for each environment"""
    preview = await db.deployments.find_one({"environment": "preview"}, sort=[("created_at", -1)])
    production = await db.deployments.find_one({"environment": "production"}, sort=[("created_at", -1)])
    
    return {
        "preview": DeploymentRecord(**preview) if preview else None,
        "production": DeploymentRecord(**production) if production else None
    }

@api_router.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        await db.command("ping")
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# ===== Health Check =====
@api_router.get("/")
async def root():
    return {"message": "Group Study Scheduler API", "version": "1.0.0"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
