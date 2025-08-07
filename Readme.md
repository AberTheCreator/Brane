# Redis-Powered Real-Time Analytics & AI Assistant

> **A comprehensive full-stack application showcasing Redis's powerful features through real-time chat, intelligent search, live analytics, and AI-powered insights.**

## 🎯 **Live Demo**
- **App**: [https://your-app-url.vercel.app](https://your-app-url.vercel.app)
- **API**: [https://your-api-url.railway.app](https://your-api-url.railway.app)

---

## **Redis Features Implemented**

###  **Core Redis Modules Used:**
- **RedisJSON** - Complex user profiles, chat messages, and application state
- **RediSearch** - Full-text search across messages, users, and content
- **Redis Streams** - Real-time message streaming and event sourcing
- **Redis Pub/Sub** - Live notifications and instant updates
- **Redis TimeSeries** - Analytics, metrics, and performance tracking
- **Redis Sets/Sorted Sets** - User rankings, leaderboards, and trending topics

###  **Key Features:**
1. **Real-Time Chat System** - Powered by Redis Streams + Pub/Sub
2. **Intelligent Search** - RediSearch with autocomplete and filtering
3. **AI Assistant** - Searches Redis data to answer user questions
4. **Live Analytics Dashboard** - Real-time metrics with Redis TimeSeries
5. **User Management** - Complex profiles stored in RedisJSON
6. **Performance Monitoring** - System health and Redis metrics

---

## 🛠️ **Technology Stack**

### **Backend:**
- Node.js + Express.js
- Redis Cloud with multiple modules
- WebSocket for real-time communication
- OpenAI API integration (optional)

### **Frontend:**
- React.js / Vanilla HTML/CSS/JS
- Chart.js for analytics visualization
- Socket.io client for real-time updates
- Responsive design with modern UI

### **Infrastructure:**
- Redis Cloud (Free 30MB database)
- Railway/Render (Backend hosting)
- Vercel/Netlify (Frontend hosting)

---

##  **Quick Start**

### **Prerequisites:**
- Node.js 16+
- Redis Cloud account
- Git

### **1. Clone Repository:**
```bash
git clone https://github.com/yourusername/redis-hackathon-project.git
cd redis-hackathon-project
```

### **2. Set Up Redis Cloud:**
1. Create free account at [redis.com/try-free](https://redis.com/try-free)
2. Create new database with modules: JSON, Search, TimeSeries
3. Copy connection details

### **3. Configure Environment:**
```bash
# Create .env file
cp .env.example .env

# Add your Redis credentials:
REDIS_HOST=your-redis-host.cloud.redislabs.com
REDIS_PORT=12345
REDIS_PASSWORD=your-redis-password
PORT=3001
```

### **4. Install & Run:**

**Option A: Single Deployment**
```bash
npm install
npm start
# Visit http://localhost:3001
```

**Option B: Separate Frontend/Backend**
```bash
# Backend
cd backend
npm install
npm start

# Frontend (new terminal)
cd frontend
npm install
npm start
```

---

## 🎮 **How to Use**

### **1. User Registration & Login**
- Create account (stored in RedisJSON)
- User profiles with preferences and history
- Automatic indexing for search

### **2. Real-Time Chat**
- Send messages (Redis Streams)
- Live updates (Redis Pub/Sub)  
- Message history and persistence

### **3. Intelligent Search**
- Search messages, users, topics
- Auto-complete and suggestions
- Advanced filtering options

### **4. AI Assistant**
- Ask questions about your data
- AI searches Redis and provides insights
- Natural language queries

### **5. Analytics Dashboard**
- Real-time user activity
- System performance metrics
- Interactive charts and graphs

---

## 📊 **Redis Implementation Details**

### **Data Models:**

**Users (RedisJSON):**
```json
{
  "id": "user:123",
  "name": "John Doe",
  "email": "john@example.com",
  "preferences": {...},
  "joinedAt": "2024-01-01T00:00:00Z"
}
```

**Messages (Redis Streams):**
```bash
XADD messages:stream * user "john" message "Hello!" timestamp "1234567890"
```

**Search Index (RediSearch):**
```bash
FT.CREATE messages_idx ON JSON PREFIX 1 message: SCHEMA 
  $.content AS content TEXT 
  $.user AS user TAG 
  $.timestamp AS timestamp NUMERIC
```

**Analytics (TimeSeries):**
```bash
TS.ADD user_activity:hourly * 1  # Track hourly activity
TS.ADD system_memory * 85.6     # Monitor system metrics
```

### **Key Redis Commands Used:**
- `JSON.SET` / `JSON.GET` - Store and retrieve complex data
- `FT.SEARCH` - Full-text search with filters
- `XADD` / `XREAD` - Stream message handling
- `PUBLISH` / `SUBSCRIBE` - Real-time notifications
- `TS.ADD` / `TS.RANGE` - Time-series data operations
- `ZADD` / `ZRANGE` - Sorted sets for rankings

---

## 🎥 **Demo Scenarios**

### **Scenario 1: Real-Time Communication**
1. User joins chat room
2. Messages stored in Redis Streams
3. Real-time delivery via Pub/Sub
4. Search through message history

### **Scenario 2: AI-Powered Insights**
1. Ask AI: "What are users talking about?"
2. AI searches Redis data using RediSearch
3. Provides intelligent summary and insights
4. All powered by your Redis data

### **Scenario 3: Live Analytics**
1. View real-time user activity
2. System performance metrics
3. Interactive charts with TimeSeries data
4. Historical trends and patterns

---

## 📈 **Performance & Scale**

### **Redis Optimization:**
- Connection pooling for high throughput
- Efficient data structures and indexing
- Minimal latency with strategic caching
- Real-time processing without delays

### **Scalability Features:**
- Horizontal scaling ready
- Redis Cluster support
- Load balancing capable
- Production deployment ready

---

## 🏗️ **Architecture**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │◄──►│   Backend   │◄──►│ Redis Cloud │
│   (React)   │    │  (Node.js)  │    │  (Database) │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
   User Interface    API Server &         Data Storage
   • Real-time UI    WebSocket Server     • RedisJSON
   • Charts/Graphs   • REST Endpoints     • RediSearch  
   • Search Box      • Authentication     • Streams
   • Chat Interface  • Business Logic     • Pub/Sub
                                         • TimeSeries
```

---

## 🚀 **Deployment**

### **Production URLs:**
- **Frontend**: Deployed on Vercel/Netlify
- **Backend**: Deployed on Railway/Render  
- **Database**: Redis Cloud (30MB free tier)

### **Environment Variables:**
```bash
REDIS_HOST=your-redis-endpoint.cloud.redislabs.com
REDIS_PORT=12345
REDIS_PASSWORD=your-secure-password
NODE_ENV=production
PORT=3001
```

---

## 🎯 **Hackathon Highlights**

### **Innovation:**
- **Unique AI Integration** - Assistant powered by Redis data
- **Real-time Everything** - Chat, analytics, notifications
- **Comprehensive Redis Usage** - 6+ modules working together
- **Production Ready** - Fully deployed and functional

### **Technical Excellence:**
- **Clean Architecture** - Well-organized, scalable codebase
- **Error Handling** - Robust error management and recovery
- **Performance** - Optimized Redis usage and queries
- **Documentation** - Complete setup and deployment guides

### **Business Value:**
- **Real-world Application** - Solves actual communication needs
- **Scalable Solution** - Ready for production deployment  
- **User Experience** - Intuitive interface with powerful features
- **Data Insights** - AI-powered analytics and recommendations

---

##  **Contributing**

This is a hackathon project, but contributions are welcome!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

##  **Acknowledgments**

- **Redis** - For the amazing database and hackathon opportunity
- **Open Source Libraries** - All the fantastic tools that made this possible

---

## 📧 **Contact**

**Developer**: Aber
**Email**: PaulAber68@gmail.com  
---

## 🔗 **Links**

- **Live Demo**: [https://your-app.vercel.app](https://your-app.vercel.app)
- **API Docs**: [https://your-api.railway.app/docs](https://your-api.railway.app/docs)
- **Demo Video**: [YouTube Link](https://youtube.com/watch?v=your-demo-video)
- **Slides**: [Presentation](https://slides.com/your-presentation)

---

**Built with ❤️ and Redis for the Redis Hackathon 2025**
