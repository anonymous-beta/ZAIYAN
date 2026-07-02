import os
import sys
import json
import threading
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.framework import ZaiyanFramework
from core.termux_compat import TermuxCompat

app = Flask(__name__, 
    template_folder="templates",
    static_folder="static"
)
app.config['SECRET_KEY'] = 'zaiyan-secret-key-2026'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global framework instance
framework = None

def init_framework():
    global framework
    framework = ZaiyanFramework()
    print(f"[+] Loaded {len(framework.modules)} modules")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/modules')
def get_modules():
    """Get all modules"""
    if not framework:
        return jsonify({"error": "Framework not initialized"}), 500
    
    modules = []
    for name, module in framework.modules.items():
        modules.append({
            "name": name,
            "type": getattr(module, "MODULE_TYPE", "unknown"),
            "description": getattr(module, "DESCRIPTION", ""),
            "author": getattr(module, "AUTHOR", "Anonymous-beta"),
            "platform": getattr(module, "PLATFORM", ["generic"])
        })
    
    return jsonify({"modules": modules, "count": len(modules)})

@app.route('/api/modules/<path:module_name>')
def get_module(module_name):
    """Get specific module details"""
    if not framework:
        return jsonify({"error": "Framework not initialized"}), 500
    
    if module_name not in framework.modules:
        return jsonify({"error": "Module not found"}), 404
    
    module = framework.modules[module_name]
    return jsonify({
        "name": module_name,
        "type": getattr(module, "MODULE_TYPE", "unknown"),
        "description": getattr(module, "DESCRIPTION", ""),
        "author": getattr(module, "AUTHOR", "Anonymous-beta"),
        "platform": getattr(module, "PLATFORM", ["generic"]),
        "options": getattr(module, "options", {})
    })

@app.route('/api/modules/<path:module_name>/execute', methods=['POST'])
def execute_module(module_name):
    """Execute a module"""
    if not framework:
        return jsonify({"error": "Framework not initialized"}), 500
    
    if module_name not in framework.modules:
        return jsonify({"error": "Module not found"}), 404
    
    data = request.json or {}
    
    # Set options
    framework.use_module(module_name)
    for key, value in data.get("options", {}).items():
        framework.set_option(key, str(value))
    
    # Execute
    try:
        result = framework.run_module()
        return jsonify({
            "success": True,
            "result": str(result) if result else "Module executed"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/sessions')
def get_sessions():
    """Get active sessions"""
    if not framework:
        return jsonify({"error": "Framework not initialized"}), 500
    
    return jsonify({
        "sessions": framework.sessions.list_sessions()
    })

@app.route('/api/payloads/generate', methods=['POST'])
def generate_payload():
    """Generate payload"""
    if not framework:
        return jsonify({"error": "Framework not initialized"}), 500
    
    data = request.json or {}
    
    try:
        payload = framework.generate_payload(
            data.get("type", "reverse_tcp"),
            data.get("format", "raw"),
            lhost=data.get("lhost", "127.0.0.1"),
            lport=int(data.get("lport", 4444)),
            arch=data.get("arch", "x64"),
            evade=data.get("evade", False),
            evasion_type=data.get("evasion_type", "xor")
        )
        
        # Save to file
        output_name = f"zaiyan_{data.get('type')}_{data.get('format')}"
        output_path = Path(__file__).parent.parent / output_name
        with open(output_path, "wb") as f:
            f.write(payload)
        
        return jsonify({
            "success": True,
            "size": len(payload),
            "file": str(output_path),
            "format": data.get("format")
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/search')
def search_modules():
    """Search modules"""
    if not framework:
        return jsonify({"error": "Framework not initialized"}), 500
    
    keyword = request.args.get("q", "")
    results = framework.search_modules(keyword)
    
    modules = []
    for name in results:
        module = framework.modules[name]
        modules.append({
            "name": name,
            "type": getattr(module, "MODULE_TYPE", "unknown"),
            "description": getattr(module, "DESCRIPTION", "")
        })
    
    return jsonify({"results": modules})

@socketio.on('connect')
def handle_connect():
    emit('status', {'message': 'Connected to ZAIYAN'})

@socketio.on('execute')
def handle_execute(data):
    """Execute module via WebSocket"""
    module_name = data.get('module')
    options = data.get('options', {})
    
    if not framework or module_name not in framework.modules:
        emit('error', {'message': 'Module not found'})
        return
    
    framework.use_module(module_name)
    for key, value in options.items():
        framework.set_option(key, str(value))
    
    emit('output', {'message': f'Executing {module_name}...'})
    
    try:
        result = framework.run_module()
        emit('complete', {
            'success': True,
            'result': str(result) if result else 'Complete'
        })
    except Exception as e:
        emit('error', {'message': str(e)})

def start_web_server(host="0.0.0.0", port=5000):
    """Start the web server"""
    init_framework()
    
    termux = TermuxCompat()
    if termux.is_termux():
        print("[*] Termux detected — binding to 127.0.0.1")
        host = "127.0.0.1"
    
    print(f"[*] Starting ZAIYAN Web Interface on http://{host}:{port}")
    print(f"[*] Loaded {len(framework.modules)} modules")
    
    socketio.run(app, host=host, port=port, debug=False)

if __name__ == '__main__':
    start_web_server()
