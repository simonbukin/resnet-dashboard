"""
/_redis.py
Handles database connections to Redis
"""

import redis


def open_redis_connection():
    """Returns an active database connection to Redis."""
    return redis.Redis(
        host='localhost',
        port=6379)
