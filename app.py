#!/usr/bin/env python3
"""
Brane AI - Redis Configuration and Utilities
===========================================

Additional utilities and configuration for the Brane AI backend.
This file contains Redis-specific configurations and helper functions.
"""

import os
import redis
import redis.asyncio as aioredis
from typing import Optional

class RedisConfig:
    """Redis configuration and connection management"""
    
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "redis-19369.c275.us-east-1-4.ec2.redns.redis-cloud.com")
        self.port = int(os.getenv("REDIS_PORT", "19369"))
        self.password = os.getenv("REDIS_PASSWORD", "M2qfJIPr9nSKDKjV8kXv263Is45idDc3")
        
    def get_sync_client(self) -> redis.Redis:
        """Get synchronous Redis client"""
        return redis.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
    
    async def get_async_client(self) -> aioredis.Redis:
        """Get asynchronous Redis client"""
        return aioredis.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )

class BraneAIModules:
    """Brane AI specific Redis module utilities"""
    
    @staticmethod
    def setup_search_index(redis_client: redis.Redis) -> bool:
        """Setup RediSearch index for Brane AI data"""
        try:
            redis_client.execute_command(
                "FT.CREATE", "brane_ai_idx",
                "ON", "JSON",
                "PREFIX", "1", "brane:ai:",
                "SCHEMA",
                "$.user_id", "AS", "user_id", "TAG",
                "$.analysis_type", "AS", "analysis_type", "TAG", 
                "$.model_type", "AS", "model_type", "TAG",
                "$.content.title", "AS", "title", "TEXT", "WEIGHT", "2.0",
                "$.content.description", "AS", "description", "TEXT",
                "$.content.insights", "AS", "insights", "TEXT",
                "$.confidence_score", "AS", "confidence", "NUMERIC", "SORTABLE",
                "$.timestamp", "AS", "timestamp", "NUMERIC", "SORTABLE",
                "$.metadata.priority", "AS", "priority", "TAG"
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def setup_timeseries(redis_client: redis.Redis, user_id: str, metric_type: str) -> bool:
        """Setup Redis TimeSeries for AI metrics"""
        try:
            ts_key = f"brane:ai:ts:{user_id}:{metric_type}"
            redis_client.execute_command(
                "TS.CREATE", ts_key,
                "RETENTION", "2592000000",  # 30 days
                "LABELS", "user_id", user_id, "type", metric_type
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def create_ai_stream(redis_client: redis.Redis) -> bool:
        """Create Redis Stream for AI processing pipeline"""
        try:
            # Create the stream with initial message
            redis_client.xadd("brane:ai:pipeline", {
                "type": "system",
                "message": "AI pipeline initialized",
                "timestamp": "0"
            })
            
            # Create consumer groups for different AI processes
            groups = ["causal_analysis", "predictive_models", "multimodal_processing"]
            for group in groups:
                try:
                    redis_client.xgroup_create("brane:ai:pipeline", group, id="0", mkstream=True)
                except Exception:
                    pass  # Group might already exist
            
            return True
        except Exception:
            return False

# AI Model Simulation Data
AI_MODELS = {
    "causal_inference": {
        "name": "CausalNet-v2",
        "type": "causal_analysis", 
        "confidence_base": 0.85,
        "processing_time": 1.2,
        "capabilities": ["cause_effect", "intervention_analysis", "counterfactual"]
    },
    "federated_learning": {
        "name": "FedBrane-v1",
        "type": "distributed_training",
        "confidence_base": 0.78,
        "processing_time": 3.5,
        "capabilities": ["privacy_preserving", "collaborative_training", "edge_deployment"]
    },
    "multimodal_fusion": {
        "name": "MultiBrane-v3",
        "type": "multimodal_analysis",
        "confidence_base": 0.82,
        "processing_time": 2.1,
        "capabilities": ["text_image", "audio_iot", "cross_modal_reasoning"]
    },
    "reinforcement_optimizer": {
        "name": "ReinforceBrane-v2", 
        "type": "rl_optimization",
        "confidence_base": 0.76,
        "processing_time": 4.2,
        "capabilities": ["policy_optimization", "reward_learning", "adaptive_personalization"]
    },
    "explainable_ai": {
        "name": "ExplainBrane-v1",
        "type": "interpretability",
        "confidence_base": 0.88,
        "processing_time": 0.8,
        "capabilities": ["feature_importance", "decision_paths", "counterfactual_explanations"]
    }
}

# Sample AI Insights Templates
INSIGHT_TEMPLATES = {
    "causal": [
        {
            "pattern": "correlation_to_causation",
            "template": "Strong correlation detected between {var1} and {var2}. Causal analysis suggests {var1} drives {impact}% change in {var2}",
            "confidence_modifier": 0.05
        },
        {
            "pattern": "intervention_effect", 
            "template": "Intervention on {variable} would result in {effect} with {confidence}% certainty",
            "confidence_modifier": 0.03
        }
    ],
    "predictive": [
        {
            "pattern": "trend_forecast",
            "template": "Based on {timeframe} of data, {metric} is predicted to {direction} by {percentage}% in the next {period}",
            "confidence_modifier": -0.02
        },
        {
            "pattern": "anomaly_prediction",
            "template": "Anomaly detection suggests {probability}% chance of unusual {event_type} in {timeframe}",
            "confidence_modifier": 0.01
        }
    ],
    "multimodal": [
        {
            "pattern": "cross_modal_insight",
            "template": "Cross-modal analysis reveals {finding} when combining {modality1} and {modality2} data",
            "confidence_modifier": 0.04
        },
        {
            "pattern": "fusion_enhancement",
            "template": "Multimodal fusion improved {metric} accuracy by {improvement}% compared to single-modal analysis",
            "confidence_modifier": 0.02
        }
    ]
}

def get_redis_config():
    """Get Redis configuration instance"""
    return RedisConfig()

def get_ai_modules():
    """Get AI modules utility instance"""
    return BraneAIModules()