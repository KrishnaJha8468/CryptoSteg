import os
import json
from datetime import datetime


class ActivityLogger:
    
    def __init__(self, log_file="logs/activity.log"):
        self.log_file = log_file
        
        
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    def log_encode(self, image_name: str, output_name: str, message_length: int, status: str):
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': 'ENCODE',
            'input_image': image_name,
            'output_image': output_name,
            'message_length': message_length,
            'status': status
        }
        self._write_log(log_entry)
    
    def log_decode(self, image_name: str, status: str, message_length: int = 0):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': 'DECODE',
            'input_image': image_name,
            'message_length': message_length,
            'status': status
        }
        self._write_log(log_entry)
    
    def _write_log(self, log_entry: dict):
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_logs(self, limit: int = 50) -> list:
        if not os.path.exists(self.log_file):
            return []
        
        logs = []
        with open(self.log_file, 'r') as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
        
        return logs[-limit:]
    
    def clear_logs(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)


if __name__ == "__main__":
    logger = ActivityLogger()
    logger.log_encode("test.png", "output.png", 50, "SUCCESS")
    logger.log_decode("output.png", "SUCCESS", 50)
    
    logs = logger.get_logs()
    print(f"Logs: {logs}")