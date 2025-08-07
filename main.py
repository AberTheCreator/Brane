#!/usr/bin/env python3
"""
Brane AI - Redis-Powered Data Analysis Backend
=============================================

Run Instructions:
1. Install dependencies: pip install -r requirements.txt
2. Set Redis environment variables (REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)
3. Start server: python main.py
4. Access at http://localhost:8000

Features:
- RedisJSON for document storage
- RediSearch for intelligent querying
- Redis Streams for real-time data processing
- Redis Pub/Sub for WebSocket communications
- Redis TimeSeries for analytics metrics
- AI-powered insights simulation
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

import redis
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis connection configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# Pydantic models
class DataPoint(BaseModel):
    id: Optional[str] = None
    user_id: str
    data_type: str  # "text", "image", "audio", "iot"
    content: Dict[str, Any]
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = {}

class SearchQuery(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = {}
    limit: int = 10

class InsightRequest(BaseModel):
    user_id: str
    data_range: Optional[str] = "7d"  # 1d, 7d, 30d
    analysis_type: str = "causal"  # causal, predictive, descriptive

# Global Redis connections
redis_client: redis.Redis = None
redis_async: aioredis.Redis = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup Redis connections"""
    global redis_client, redis_async
    
    # Initialize Redis connections
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=10,
        socket_timeout=10
    )
    
    redis_async = aioredis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=10,
        socket_timeout=10
    )
    
    # Test connections
    try:
        await redis_async.ping()
        redis_client.ping()
        logger.info("Successfully connected to Redis")
        
        # Initialize Redis modules and sample data
        await initialize_redis_modules()
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    
    yield
    
    # Cleanup
    if redis_async:
        await redis_async.close()
    if redis_client:
        redis_client.close()

# Initialize FastAPI app
app = FastAPI(
    title="Brane AI Backend",
    description="Redis-powered AI data analysis platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections.remove(websocket)
        if user_id in self.user_connections:
            self.user_connections[user_id].remove(websocket)

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

async def initialize_redis_modules():
    """Initialize Redis modules and create sample data"""
    try:
        # Try to create RediSearch index for data analysis
        try:
            redis_client.execute_command(
                "FT.CREATE", "brane_data_idx",
                "ON", "JSON",
                "PREFIX", "1", "brane:data:",
                "SCHEMA",
                "$.user_id", "AS", "user_id", "TAG",
                "$.data_type", "AS", "data_type", "TAG", 
                "$.content.title", "AS", "title", "TEXT",
                "$.content.description", "AS", "description", "TEXT",
                "$.timestamp", "AS", "timestamp", "NUMERIC", "SORTABLE"
            )
            logger.info("Created RediSearch index")
        except Exception as e:
            logger.warning(f"RediSearch index creation failed (may not be supported): {e}")

        # Create sample data
        await create_sample_data()
        
        # Start background tasks
        asyncio.create_task(redis_stream_processor())
        asyncio.create_task(redis_pubsub_listener())
        
    except Exception as e:
        logger.error(f"Redis initialization error: {e}")

async def create_sample_data():
    """Create sample data for demonstration"""
    sample_data = [
        {
            "id": "data_1",
            "user_id": "user_123",
            "data_type": "text",
            "content": {
                "title": "Q4 Sales Analysis",
                "description": "Revenue increased 25% due to new marketing campaigns",
                "value": 125000,
                "category": "sales"
            },
            "timestamp": datetime.now().timestamp(),
            "metadata": {"source": "sales_dashboard", "confidence": 0.95}
        },
        {
            "id": "data_2", 
            "user_id": "user_123",
            "data_type": "iot",
            "content": {
                "title": "Temperature Sensor Data",
                "description": "Factory floor temperature monitoring",
                "value": 23.5,
                "unit": "celsius",
                "sensor_id": "temp_001"
            },
            "timestamp": datetime.now().timestamp(),
            "metadata": {"location": "factory_floor_1", "device_type": "temperature"}
        },
        {
            "id": "data_3",
            "user_id": "user_456", 
            "data_type": "image",
            "content": {
                "title": "Product Quality Analysis",
                "description": "AI-detected defects in manufacturing line",
                "defect_count": 3,
                "quality_score": 0.87
            },
            "timestamp": datetime.now().timestamp(),
            "metadata": {"ai_model": "yolo_v5", "processing_time": 0.23}
        }
    ]
    
    for data in sample_data:
        redis_client.json().set(f"brane:data:{data['id']}", "$", data)
        
        # Add to TimeSeries for analytics
        ts_key = f"brane:ts:{data['user_id']}:{data['data_type']}"
        try:
            redis_client.execute_command("TS.CREATE", ts_key, "RETENTION", 86400000)
        except:
            pass  # Key might already exist
        
        value = data['content'].get('value', 1)
        redis_client.execute_command("TS.ADD", ts_key, int(data['timestamp'] * 1000), value)
    
    logger.info("Created sample data")

async def redis_stream_processor():
    """Process Redis Streams for real-time data"""
    try:
        # Create consumer group
        try:
            await redis_async.xgroup_create("brane:stream", "processors", id="0", mkstream=True)
        except:
            pass  # Group might already exist
            
        while True:
            try:
                messages = await redis_async.xreadgroup(
                    "processors", "worker1", {"brane:stream": ">"}, count=1, block=1000
                )
                
                for stream, msgs in messages:
                    for msg_id, fields in msgs:
                        # Process the message
                        data = {k.decode() if isinstance(k, bytes) else k: 
                               v.decode() if isinstance(v, bytes) else v 
                               for k, v in fields.items()}
                        
                        # Broadcast to WebSocket clients
                        await manager.broadcast({
                            "type": "stream_data",
                            "data": data,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        # Acknowledge message
                        await redis_async.xack("brane:stream", "processors", msg_id)
                        
            except Exception as e:
                logger.error(f"Stream processing error: {e}")
                await asyncio.sleep(5)
                
    except Exception as e:
        logger.error(f"Stream processor setup error: {e}")

async def redis_pubsub_listener():
    """Listen to Redis Pub/Sub for real-time updates"""
    try:
        pubsub = redis_async.pubsub()
        await pubsub.subscribe("brane:insights", "brane:alerts")
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    await manager.broadcast({
                        "type": "pubsub_message",
                        "channel": message['channel'],
                        "data": data
                    })
                except Exception as e:
                    logger.error(f"PubSub message processing error: {e}")
                    
    except Exception as e:
        logger.error(f"PubSub listener error: {e}")

# API Endpoints

@app.get("/")
async def root():
    """Health check and API info"""
    return {
        "service": "Brane AI Backend",
        "status": "running",
        "redis_connected": True,
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "data": "/api/data",
            "search": "/api/search", 
            "analytics": "/api/analytics",
            "insights": "/api/insights",
            "websocket": "/ws/{user_id}"
        }
    }

@app.post("/api/data")
async def save_data(data: DataPoint, background_tasks: BackgroundTasks):
    """Save analysis data using RedisJSON"""
    try:
        # Generate ID if not provided
        if not data.id:
            data.id = f"data_{int(datetime.now().timestamp() * 1000)}"
        
        # Set timestamp if not provided
        if not data.timestamp:
            data.timestamp = datetime.now()
        
        # Convert to dict for Redis
        data_dict = data.dict()
        data_dict['timestamp'] = data_dict['timestamp'].timestamp()
        
        # Save to RedisJSON
        redis_client.json().set(f"brane:data:{data.id}", "$", data_dict)
        
        # Add to TimeSeries for analytics
        ts_key = f"brane:ts:{data.user_id}:{data.data_type}"
        try:
            redis_client.execute_command("TS.CREATE", ts_key, "RETENTION", 86400000)
        except:
            pass
        
        value = data.content.get('value', 1)
        redis_client.execute_command("TS.ADD", ts_key, int(data_dict['timestamp'] * 1000), value)
        
        # Add to Stream for real-time processing
        await redis_async.xadd("brane:stream", {
            "type": "new_data",
            "user_id": data.user_id,
            "data_type": data.data_type,
            "data_id": data.id
        })
        
        # Trigger insights generation in background
        background_tasks.add_task(trigger_insights, data.user_id)
        
        return {"success": True, "id": data.id, "timestamp": data_dict['timestamp']}
        
    except Exception as e:
        logger.error(f"Data save error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data")
async def get_data(user_id: str, limit: int = 10):
    """Retrieve user/session data"""
    try:
        # Search for user data using RediSearch
        query = f"@user_id:{user_id}"
        result = redis_client.execute_command(
            "FT.SEARCH", "brane_data_idx", query, 
            "LIMIT", "0", str(limit),
            "SORTBY", "timestamp", "DESC"
        )
        
        # Parse results
        data = []
        if len(result) > 1:
            for i in range(1, len(result), 2):
                key = result[i]
                doc = redis_client.json().get(key)
                if doc:
                    data.append(doc)
        
        return {"data": data, "total": len(data)}
        
    except Exception as e:
        logger.error(f"Data retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search_data(query: SearchQuery):
    """Query using RediSearch with autocomplete/filter"""
    try:
        # Build search query
        search_terms = []
        
        if query.query:
            search_terms.append(f"(@title:{query.query}*) | (@description:{query.query}*)")
        
        if query.filters:
            for key, value in query.filters.items():
                if key == "data_type":
                    search_terms.append(f"@data_type:{value}")
                elif key == "user_id":
                    search_terms.append(f"@user_id:{value}")
        
        search_query = " ".join(search_terms) if search_terms else "*"
        
        # Execute search
        result = redis_client.execute_command(
            "FT.SEARCH", "brane_data_idx", search_query,
            "LIMIT", "0", str(query.limit),
            "SORTBY", "timestamp", "DESC"
        )
        
        # Parse results
        results = []
        if len(result) > 1:
            for i in range(1, len(result), 2):
                key = result[i]
                doc = redis_client.json().get(key)
                if doc:
                    results.append(doc)
        
        return {
            "results": results,
            "total": result[0] if result else 0,
            "query": search_query
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
async def get_analytics(user_id: str, time_range: str = "1h"):
    """Return RedisTimeSeries metrics"""
    try:
        # Convert time range to milliseconds
        range_ms = {
            "1h": 3600000,
            "1d": 86400000,
            "7d": 604800000,
            "30d": 2592000000
        }.get(time_range, 3600000)
        
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = end_time - range_ms
        
        analytics = {}
        
        # Get data for different types
        data_types = ["text", "image", "audio", "iot"]
        for data_type in data_types:
            ts_key = f"brane:ts:{user_id}:{data_type}"
            try:
                result = redis_client.execute_command(
                    "TS.RANGE", ts_key, start_time, end_time, "AGGREGATION", "avg", 3600000
                )
                
                analytics[data_type] = {
                    "points": len(result),
                    "data": result[-10:],  # Last 10 points
                    "avg": sum(point[1] for point in result) / len(result) if result else 0
                }
            except:
                analytics[data_type] = {"points": 0, "data": [], "avg": 0}
        
        # Calculate trends and insights
        total_points = sum(v["points"] for v in analytics.values())
        most_active_type = max(analytics.keys(), key=lambda k: analytics[k]["points"]) if total_points > 0 else None
        
        return {
            "user_id": user_id,
            "time_range": time_range,
            "analytics": analytics,
            "summary": {
                "total_data_points": total_points,
                "most_active_type": most_active_type,
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/insights")
async def get_insights(request: InsightRequest):
    """Return AI-powered insights (simulated Brane AI)"""
    try:
        # Get user data for analysis
        user_data_result = await get_data(request.user_id, limit=50)
        user_data = user_data_result["data"]
        
        # Simulate AI analysis based on data patterns
        insights = {
            "user_id": request.user_id,
            "analysis_type": request.analysis_type,
            "data_range": request.data_range,
            "insights": [],
            "confidence_score": 0.85,
            "generated_at": datetime.now().isoformat()
        }
        
        if request.analysis_type == "causal":
            insights["insights"] = [
                {
                    "type": "causal_relationship",
                    "title": "Temperature Impact on Quality",
                    "description": "Higher factory temperatures correlate with 15% decrease in product quality scores",
                    "confidence": 0.89,
                    "data_sources": ["iot", "image"],
                    "recommendation": "Implement temperature control alerts when readings exceed 25°C"
                },
                {
                    "type": "trend_analysis", 
                    "title": "Sales Performance Driver",
                    "description": "Marketing campaign mentions directly caused 25% revenue increase",
                    "confidence": 0.92,
                    "data_sources": ["text"],
                    "recommendation": "Increase marketing budget allocation by 30%"
                }
            ]
        elif request.analysis_type == "predictive":
            insights["insights"] = [
                {
                    "type": "forecast",
                    "title": "Next Week Quality Prediction",
                    "description": "Quality scores expected to improve by 8% based on temperature trends",
                    "confidence": 0.78,
                    "prediction_window": "7 days",
                    "recommendation": "Maintain current operational parameters"
                }
            ]
        else:  # descriptive
            insights["insights"] = [
                {
                    "type": "summary",
                    "title": "Data Overview",
                    "description": f"Analyzed {len(user_data)} data points across multiple modalities",
                    "confidence": 1.0,
                    "metrics": {
                        "total_points": len(user_data),
                        "data_types": len(set(d.get("data_type") for d in user_data)),
                        "time_span": request.data_range
                    }
                }
            ]
        
        # Publish insights to Redis Pub/Sub
        await redis_async.publish("brane:insights", json.dumps(insights))
        
        return insights
        
    except Exception as e:
        logger.error(f"Insights generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sample-data")
async def generate_sample_data():
    """Generate more sample data for testing"""
    try:
        await create_sample_data()
        return {"message": "Sample data generated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Echo message back or handle specific commands
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
            else:
                await manager.send_personal_message(
                    {"type": "echo", "data": message, "timestamp": datetime.now().isoformat()},
                    user_id
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)

async def trigger_insights(user_id: str):
    """Background task to trigger insights generation"""
    try:
        # Simulate AI processing delay
        await asyncio.sleep(2)
        
        # Publish alert about new insights
        await redis_async.publish("brane:alerts", json.dumps({
            "type": "new_insights_available",
            "user_id": user_id,
            "message": "New AI insights generated based on your latest data",
            "timestamp": datetime.now().isoformat()
        }))
        
    except Exception as e:
        logger.error(f"Background insights task error: {e}")

# Serve static files (if needed)
# app.mount("/public", StaticFiles(directory="public"), name="public")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )