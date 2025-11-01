import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Calendar } from "@/components/ui/calendar";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Toaster } from "@/components/ui/sonner";
import {
  Users,
  Calendar as CalendarIcon,
  Clock,
  Plus,
  LogOut,
  GitBranch,
} from "lucide-react";

/* ===================== Frontend API Config ===================== */
const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
const API = `${BACKEND_URL}/api`;

// Global axios setup
axios.defaults.baseURL = API;
axios.interceptors.request.use((config) => {
  const token =
    localStorage.getItem("token") || localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

/* ===================== Auth Context ===================== */
const AuthContext = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const { data } = await axios.get("/me");
      setUser(data);
    } catch {
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = (newToken, userData) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
    setUser(userData);
    axios.defaults.headers.common["Authorization"] = `Bearer ${newToken}`;
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common["Authorization"];
  };

  return children({ user, token, login, logout, loading });
};

/* ===================== Landing Page ===================== */
const LandingPage = ({ onShowAuth }) => (
  <div className="landing-page">
    <nav className="landing-nav">
      <div className="nav-content">
        <div className="logo">
          <CalendarIcon className="logo-icon" />
          <span>TimeAlign</span>
        </div>
        <Button onClick={onShowAuth} variant="outline">
          Sign In
        </Button>
      </div>
    </nav>

    <section className="hero-section">
      <div className="hero-content">
        <h1 className="hero-title">Find the Perfect Time for Your Study Group</h1>
        <p className="hero-subtitle">
          Stop the endless back-and-forth. TimeAlign automatically finds when
          everyone's available and creates calendar events in seconds.
        </p>
        <Button onClick={onShowAuth} size="lg" className="cta-button">
          Get Started Free
        </Button>
      </div>
    </section>

    <footer className="landing-footer">
      <p>© 2025 TimeAlign. Making group scheduling effortless.</p>
    </footer>
  </div>
);

/* ===================== Auth Modal ===================== */
const AuthModal = ({ open, onClose, onLogin }) => {
  const [mode, setMode] = useState("login");
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    name: "",
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    const endpoint = mode === "login" ? "/auth/login" : "/auth/signup";
    try {
      const { data } = await axios.post(endpoint, formData);
      onLogin(data.access_token, data.user);
      toast.success(mode === "login" ? "Welcome back!" : "Account created!");
      onClose();
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Authentication failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="auth-modal">
        <DialogHeader>
          <DialogTitle>{mode === "login" ? "Welcome Back" : "Create Account"}</DialogTitle>
          <DialogDescription>
            {mode === "login" ? "Sign in to access your study groups" : "Get started with TimeAlign"}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="auth-form">
          {mode === "signup" && (
            <div className="form-group">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) =>
                  setFormData((s) => ({ ...s, name: e.target.value }))
                }
                required
              />
            </div>
          )}
          <div className="form-group">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) =>
                setFormData((s) => ({ ...s, email: e.target.value }))
              }
              required
            />
          </div>
          <div className="form-group">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={formData.password}
              onChange={(e) =>
                setFormData((s) => ({ ...s, password: e.target.value }))
              }
              required
            />
          </div>
          <Button type="submit" className="w-full" disabled={submitting}>
            {submitting ? "Please wait..." : mode === "login" ? "Sign In" : "Create Account"}
          </Button>
          <p className="auth-switch">
            {mode === "login" ? "Don't have an account? " : "Already have an account? "}
            <button
              type="button"
              onClick={() => setMode((m) => (m === "login" ? "signup" : "login"))}
              className="auth-switch-link"
            >
              {mode === "login" ? "Sign Up" : "Sign In"}
            </button>
          </p>
        </form>
      </DialogContent>
    </Dialog>
  );
};

/* ===================== DevOps Dashboard — Setup Guide only ===================== */
const DevOpsDashboard = () => (
  <div className="devops-dashboard">
    <div className="devops-header">
      <div>
        <h1>DevOps Pipeline</h1>
        <p className="text-gray-500">Setup guide for your pipeline</p>
      </div>
    </div>

    <Card>
      <CardHeader>
        <CardTitle>Setup Guide</CardTitle>
        <CardDescription>Get your DevOps pipeline up and running</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="setup-steps">
          <div className="setup-step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Connect to GitHub</h3>
              <p>Push your TimeAlign code to a GitHub repository</p>
              <code className="code-block">
                git init{"\n"}
                git remote add origin https://github.com/YOUR_USERNAME/timealign.git{"\n"}
                git add .{"\n"}
                git commit -m "Initial commit"{"\n"}
                git push -u origin main
              </code>
            </div>
          </div>

          <div className="setup-step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Configure GitHub Secrets</h3>
              <p>Add these repository secrets (Settings → Secrets → Actions):</p>
              <ul className="setup-list">
                <li><code>DEPLOYMENT_TOKEN</code> — JWT token for API authentication</li>
                <li><code>MONGO_URL</code> — MongoDB connection string</li>
                <li><code>DB_NAME</code> — Database name</li>
              </ul>
            </div>
          </div>

          <div className="setup-step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Set up Environments</h3>
              <p>Create GitHub environments for deployment protection:</p>
              <ul className="setup-list">
                <li><strong>preview</strong> — Auto-deploy from <code>develop</code></li>
                <li><strong>production</strong> — Manual approval required</li>
              </ul>
            </div>
          </div>

          <div className="setup-step">
            <div className="step-number">4</div>
            <div className="step-content">
              <h3>Trigger Your First Deploy</h3>
              <p>Push to develop or main to trigger the pipeline:</p>
              <code className="code-block">
                git checkout -b develop{"\n"}
                git push origin develop
              </code>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
);

/* ===================== Dashboard (keeps Groups + DevOps tabs) ===================== */
const Dashboard = ({ user, onLogout }) => {
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [showCreateGroup, setShowCreateGroup] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState("groups"); // 'groups' or 'devops'

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      const { data } = await axios.get("/groups");
      setGroups(data);
    } catch {
      toast.error("Failed to load groups");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGroup = async (name) => {
    try {
      const { data } = await axios.post("/groups", { name });
      setGroups((s) => [...s, data]);
      toast.success("Group created successfully!");
      setShowCreateGroup(false);
    } catch {
      toast.error("Failed to create group");
    }
  };

  if (loading) return <div className="loading-screen">Loading...</div>;

  return (
    <div className="dashboard">
      <nav className="dashboard-nav">
        <div className="nav-content">
          <div className="logo">
            <CalendarIcon className="logo-icon" />
            <span>TimeAlign</span>
          </div>
          <div className="nav-center">
            <button
              className={`nav-tab ${activeView === "groups" ? "active" : ""}`}
              onClick={() => setActiveView("groups")}
              data-testid="nav-groups-tab"
            >
              <Users className="w-4 h-4" />
              Groups
            </button>
            <button
              className={`nav-tab ${activeView === "devops" ? "active" : ""}`}
              onClick={() => setActiveView("devops")}
              data-testid="nav-devops-tab"
            >
              <GitBranch className="w-4 h-4" />
              DevOps
            </button>
          </div>
          <div className="nav-right">
            <div className="user-info">
              <span>{user.name}</span>
            </div>
            <Button onClick={onLogout} variant="outline" size="sm" data-testid="logout-btn">
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        {activeView === "devops" ? (
          <DevOpsDashboard />
        ) : selectedGroup ? (
          <GroupDetail
            group={selectedGroup}
            onBack={() => setSelectedGroup(null)}
            onUpdate={fetchGroups}
          />
        ) : (
          <div className="groups-container">
            <div className="groups-header">
              <h1>Your Study Groups</h1>
              <Button onClick={() => setShowCreateGroup(true)} data-testid="create-group-btn">
                <Plus className="w-4 h-4 mr-2" />
                Create Group
              </Button>
            </div>

            {groups.length === 0 ? (
              <Card className="empty-state">
                <CardContent>
                  <Users className="empty-icon" />
                  <h3>No groups yet</h3>
                  <p>Create your first study group to get started</p>
                  <Button onClick={() => setShowCreateGroup(true)} data-testid="empty-create-group-btn">
                    Create Group
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="groups-grid">
                {groups.map((g) => (
                  <Card
                    key={g.id}
                    className="group-card"
                    data-testid={`group-card-${g.id}`}
                    onClick={() => setSelectedGroup(g)}
                  >
                    <CardHeader>
                      <CardTitle>{g.name}</CardTitle>
                      <CardDescription>
                        {g.members.length} member{g.members.length !== 1 ? "s" : ""}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="group-members">
                        {g.members.slice(0, 3).map((m) => (
                          <div key={m.id} className="member-avatar" title={m.name}>
                            {m.avatar_url ? (
                              <img src={m.avatar_url} alt={m.name} />
                            ) : (
                              m.name.charAt(0).toUpperCase()
                            )}
                          </div>
                        ))}
                        {g.members.length > 3 && (
                          <div className="member-avatar">+{g.members.length - 3}</div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <CreateGroupModal
        open={showCreateGroup}
        onClose={() => setShowCreateGroup(false)}
        onCreate={handleCreateGroup}
      />
    </div>
  );
};

/* ===================== Create Group Modal ===================== */
const CreateGroupModal = ({ open, onClose, onCreate }) => {
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    await onCreate(name);
    setLoading(false);
    setName("");
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create New Group</DialogTitle>
          <DialogDescription>Give your study group a name</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="group-name">Group Name</Label>
            <Input
              id="group-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., SWE40006 Team A"
              required
              data-testid="group-name-input"
            />
          </div>
          <Button type="submit" className="w-full" disabled={loading} data-testid="create-group-submit-btn">
            {loading ? "Creating..." : "Create Group"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
};

/* ===================== Group Detail ===================== */
const GroupDetail = ({ group: initialGroup, onBack, onUpdate }) => {
  const [group, setGroup] = useState(initialGroup);
  const [activeTab, setActiveTab] = useState("schedule");
  const [inviteEmails, setInviteEmails] = useState("");
  const [dateRange, setDateRange] = useState({ from: new Date(), to: null });
  const [duration, setDuration] = useState(60);
  const [suggestions, setSuggestions] = useState([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [showEventModal, setShowEventModal] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState(null);

  const fetchGroupDetails = async () => {
    try {
      const { data } = await axios.get(`/groups/${group.id}`);
      setGroup(data);
    } catch {
      toast.error("Failed to load group details");
    }
  };

  const handleInvite = async () => {
    const emails = inviteEmails.split(",").map((e) => e.trim()).filter(Boolean);
    if (emails.length === 0) return;

    try {
      await axios.post(`/groups/${group.id}/invite`, { emails });
      toast.success("Invitations sent!");
      setInviteEmails("");
      fetchGroupDetails();
      onUpdate();
    } catch {
      toast.error("Failed to send invitations");
    }
  };

  const handleFindTimes = async () => {
    if (!dateRange.to) {
      toast.error("Please select an end date");
      return;
    }
    setLoadingSuggestions(true);
    try {
      const { data } = await axios.post("/schedule/suggest", {
        group_id: group.id,
        range_start: dateRange.from.toISOString(),
        range_end: dateRange.to.toISOString(),
        duration_mins: duration,
        granularity_mins: 15,
        min_coverage: 0.7,
      });
      setSuggestions(data);
      if (data.length === 0) {
        toast.info("No available time slots found. Try a different date range or lower duration.");
      }
    } catch {
      toast.error("Failed to find available times");
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const handleCreateEvent = async (eventData) => {
    try {
      await axios.post("/schedule/create", {
        group_id: group.id,
        start: selectedSlot.start,
        end: selectedSlot.end,
        title: eventData.title,
        description: eventData.description,
        location: eventData.location,
      });
      toast.success("Event created successfully!");
      setShowEventModal(false);
      setSelectedSlot(null);
    } catch {
      toast.error("Failed to create event");
    }
  };

  const formatDateTime = (isoString) =>
    new Date(isoString).toLocaleString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });

  return (
    <div className="group-detail">
      <div className="group-header">
        <Button onClick={onBack} variant="outline" data-testid="back-to-groups-btn">
          ← Back to Groups
        </Button>
        <h1>{group.name}</h1>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="group-tabs">
        <TabsList>
          <TabsTrigger value="schedule" data-testid="schedule-tab">Schedule</TabsTrigger>
          <TabsTrigger value="members" data-testid="members-tab">Members</TabsTrigger>
        </TabsList>

        <TabsContent value="schedule" className="schedule-tab">
          <div className="schedule-content">
            <Card className="schedule-config">
              <CardHeader>
                <CardTitle>Find Available Times</CardTitle>
                <CardDescription>Select a date range and duration</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Date Range</Label>
                  <Calendar
                    mode="range"
                    selected={dateRange}
                    onSelect={setDateRange}
                    className="calendar-picker"
                    numberOfMonths={2}
                  />
                </div>

                <div>
                  <Label htmlFor="duration">Duration (minutes)</Label>
                  <Input
                    id="duration"
                    type="number"
                    value={duration}
                    onChange={(e) => setDuration(parseInt(e.target.value))}
                    min="15"
                    step="15"
                    data-testid="duration-input"
                  />
                </div>

                <Button
                  onClick={handleFindTimes}
                  className="w-full"
                  disabled={loadingSuggestions || !dateRange.to}
                  data-testid="find-times-btn"
                >
                  {loadingSuggestions ? "Finding times..." : "Find Available Times"}
                </Button>
              </CardContent>
            </Card>

            <div className="suggestions-list">
              <h3>Suggested Time Slots</h3>
              {suggestions.length === 0 ? (
                <Card className="empty-suggestions">
                  <CardContent>
                    <Clock className="empty-icon" />
                    <p>No suggestions yet. Configure and search for available times.</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="suggestions-grid">
                  {suggestions.map((slot, idx) => (
                    <Card key={idx} className="suggestion-card" data-testid={`suggestion-${idx}`}>
                      <CardHeader>
                        <div className="suggestion-header">
                          <CardTitle>{formatDateTime(slot.start)}</CardTitle>
                          <Badge variant={slot.coverage_ratio >= 0.9 ? "default" : "secondary"}>
                            {Math.round(slot.coverage_ratio * 100)}% available
                          </Badge>
                        </div>
                        <CardDescription>
                          Duration: {duration} minutes • {slot.available_members}/{slot.total_members} members
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <Button
                          className="w-full"
                          onClick={() => {
                            setSelectedSlot(slot);
                            setShowEventModal(true);
                          }}
                          data-testid={`create-event-btn-${idx}`}
                        >
                          Create Event
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="members" className="members-tab">
          <Card>
            <CardHeader>
              <CardTitle>Group Members</CardTitle>
              <CardDescription>
                {group.members.length} member{group.members.length !== 1 ? "s" : ""}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="members-list">
                {group.members.map((m) => (
                  <div key={m.id} className="member-item" data-testid={`member-${m.id}`}>
                    <div className="member-avatar-large">
                      {m.avatar_url ? <img src={m.avatar_url} alt={m.name} /> : m.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="member-details">
                      <div className="member-name">{m.name}</div>
                      <div className="member-email">{m.email}</div>
                    </div>
                    {m.id === group.owner_id && <Badge>Owner</Badge>}
                  </div>
                ))}
              </div>

              <div className="invite-section">
                <Label htmlFor="invite-emails">Invite Members</Label>
                <div className="invite-input-group">
                  <Input
                    id="invite-emails"
                    value={inviteEmails}
                    onChange={(e) => setInviteEmails(e.target.value)}
                    placeholder="email1@example.com, email2@example.com"
                    data-testid="invite-emails-input"
                  />
                  <Button onClick={handleInvite} data-testid="send-invites-btn">
                    Send Invites
                  </Button>
                </div>
                <p className="text-sm text-gray-500 mt-2">Separate multiple emails with commas</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <CreateEventModal
        open={showEventModal}
        onClose={() => {
          setShowEventModal(false);
          setSelectedSlot(null);
        }}
        onSubmit={handleCreateEvent}
        slot={selectedSlot}
      />
    </div>
  );
};

/* ===================== Create Event Modal ===================== */
const CreateEventModal = ({ open, onClose, onSubmit, slot }) => {
  const [eventData, setEventData] = useState({
    title: "",
    description: "",
    location: "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(eventData);
    setEventData({ title: "", description: "", location: "" });
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Study Session</DialogTitle>
          <DialogDescription>{slot && new Date(slot.start).toLocaleString()}</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="event-title">Title</Label>
            <Input
              id="event-title"
              value={eventData.title}
              onChange={(e) => setEventData((s) => ({ ...s, title: e.target.value }))}
              placeholder="Study Session"
              required
              data-testid="event-title-input"
            />
          </div>
          <div>
            <Label htmlFor="event-description">Description (optional)</Label>
            <Input
              id="event-description"
              value={eventData.description}
              onChange={(e) => setEventData((s) => ({ ...s, description: e.target.value }))}
              placeholder="What are you studying?"
              data-testid="event-description-input"
            />
          </div>
          <div>
            <Label htmlFor="event-location">Location (optional)</Label>
            <Input
              id="event-location"
              value={eventData.location}
              onChange={(e) => setEventData((s) => ({ ...s, location: e.target.value }))}
              placeholder="Library, Room 101"
              data-testid="event-location-input"
            />
          </div>
          <Button type="submit" className="w-full" data-testid="create-event-submit-btn">
            Create Event
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
};

/* ===================== Main App ===================== */
function App() {
  const [showAuth, setShowAuth] = useState(false);

  return (
    <AuthContext>
      {({ user, login, logout, loading }) => (
        <div className="App">
          <Toaster position="top-right" />
          <BrowserRouter>
            <Routes>
              <Route
                path="/"
                element={
                  loading ? (
                    <div className="loading-screen">Loading...</div>
                  ) : user ? (
                    <Navigate to="/dashboard" />
                  ) : (
                    <LandingPage onShowAuth={() => setShowAuth(true)} />
                  )
                }
              />
              <Route
                path="/dashboard"
                element={user ? <Dashboard user={user} onLogout={logout} /> : <Navigate to="/" />}
              />
            </Routes>
          </BrowserRouter>

          <AuthModal open={showAuth && !user} onClose={() => setShowAuth(false)} onLogin={login} />
        </div>
      )}
    </AuthContext>
  );
}

export default App;
