# app/services/camera_discovery.py
import socket
import threading
from typing import List, Dict, Any
import time

class CameraDiscoveryService:
    def