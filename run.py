#!/usr/bin/env python3
"""Startup script for Vedic Astro web application"""
import sys
import os

# Add Python site-packages to path
sys.path.insert(0, '/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages')

from app import app

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════╗
    ║         🕉️  VEDIC ASTRO  🕉️               ║
    ║    Authentic Birth Chart Analysis         ║
    ╠═══════════════════════════════════════════╣
    ║  Running at: http://localhost:8080        ║
    ║  API: http://localhost:8080/api/calculate ║
    ╚═══════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=8080)
