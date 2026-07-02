import time
import uuid
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

class Session:
    def __init__(self, session_id: str, target: str, module: str, 
                 session_type: str = "shell"):
        self.id = session_id
        self.target = target
        self.module = module
        self.type = session_type
        self.created = datetime.now()
        self.last_checkin = datetime.now()
        self.info = {}
        self.active = True
        self.commands = []
        self.responses = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "target": self.target,
            "module": self.module,
            "type": self.type,
            "created": self.created.isoformat(),
            "last_checkin": self.last_checkin.isoformat(),
            "info": self.info,
            "active": self.active
        }
    
    def checkin(self):
        self.last_checkin = datetime.now()
    
    def add_command(self, cmd: str):
        self.commands.append({
            "time": datetime.now().isoformat(),
            "command": cmd
        })
    
    def add_response(self, resp: str):
        self.responses.append({
            "time": datetime.now().isoformat(),
            "response": resp
        })

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.session_dir = Path(__file__).parent.parent / "sessions"
        self.session_dir.mkdir(exist_ok=True)
    
    def create_session(self, target: str, module: str, 
                       session_type: str = "shell") -> Session:
        """Create new session"""
        session_id = str(uuid.uuid4())[:8]
        session = Session(session_id, target, module, session_type)
        self.sessions[session_id] = session
        self._save_session(session)
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions"""
        return [s.to_dict() for s in self.sessions.values()]
    
    def kill_session(self, session_id: str) -> bool:
        """Terminate session"""
        if session_id in self.sessions:
            self.sessions[session_id].active = False
            self._save_session(self.sessions[session_id])
            return True
        return False
    
    def interact(self, session_id: str, command: str) -> Optional[str]:
        """Send command to session"""
        session = self.get_session(session_id)
        if not session or not session.active:
            return None
        
        session.add_command(command)
        session.checkin()
        self._save_session(session)
        
        # In real implementation, this would communicate with the agent
        return f"Command sent to {session_id}"
    
    def register_activity(self, module: Any):
        """Register module execution as potential session"""
        # Called after exploit execution
        pass
    
    def _save_session(self, session: Session):
        """Persist session to disk"""
        path = self.session_dir / f"{session.id}.json"
        with open(path, "w") as f:
            json.dump(session.to_dict(), f, indent=2)
    
    def load_sessions(self):
        """Load sessions from disk"""
        for path in self.session_dir.glob("*.json"):
            with open(path) as f:
                data = json.load(f)
                # Reconstruct session
                s = Session(data["id"], data["target"], data["module"], data["type"])
                s.created = datetime.fromisoformat(data["created"])
                s.last_checkin = datetime.fromisoformat(data["last_checkin"])
                s.info = data.get("info", {})
                s.active = data.get("active", True)
                self.sessions[s.id] = s
