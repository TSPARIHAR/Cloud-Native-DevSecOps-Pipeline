import os
import redis
from flask import Flask, jsonify

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Initialize Redis connection with fallback resilience
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=2)
except Exception as e:
    r = None

@app.route('/health', methods=['GET'])
def health_check():
    """Liveness/Readiness probe endpoint for Kubernetes."""
    return jsonify({"status": "healthy", "service": "flask-redis-api"}), 200

@app.route('/', methods=['GET'])
def index():
    """Main route tracking hit count in Redis."""
    if not r:
        return jsonify({"message": "API online, Redis unavailable"}), 200
    try:
        visits = r.incr("page_views")
        return jsonify({
            "message": "Welcome to Cloud-Native Flask API",
            "page_views": visits
        }), 200
    except redis.RedisError:
        return jsonify({"message": "API online, Redis connection failed"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
