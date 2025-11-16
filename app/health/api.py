from flask import jsonify
from . import health
from .. import db
import shutil
import psutil

def get_disk_usage():
    """Returns disk usage statistics."""
    total, used, free = shutil.disk_usage("/")
    return {
        "total": f"{total // (2**30)} GB",
        "used": f"{used // (2**30)} GB",
        "free": f"{free // (2**30)} GB",
        "percent_used": f"{(used / total) * 100:.2f}%"
    }

def get_memory_usage():
    """Returns memory usage statistics."""
    memory = psutil.virtual_memory()
    return {
        "total": f"{memory.total // (2**30)} GB",
        "available": f"{memory.available // (2**30)} GB",
        "percent_used": f"{memory.percent}%"
    }

@health.route('/api/health', methods=['GET'])
def health_check():
    """
    Checks the health of the application and its dependencies.
    """
    health_status = {
        "application_status": "ok",
        "dependencies": {
            "database": "ok",
            "disk_space": "ok",
            "memory": "ok",
            "cache": "ok" # Placeholder for cache check
        }
    }
    
    # Check database connection
    try:
        db.session.execute('SELECT 1')
    except Exception as e:
        health_status["dependencies"]["database"] = "error"
        health_status["application_status"] = "error"
        return jsonify(health_status), 500
        
    # Check disk space
    try:
        health_status["dependencies"]["disk_space"] = get_disk_usage()
    except Exception as e:
        health_status["dependencies"]["disk_space"] = "error"
        health_status["application_status"] = "error"
        return jsonify(health_status), 500

    # Check memory usage
    try:
        health_status["dependencies"]["memory"] = get_memory_usage()
    except Exception as e:
        health_status["dependencies"]["memory"] = "error"
        health_status["application_status"] = "error"
        return jsonify(health_status), 500

    return jsonify(health_status)
