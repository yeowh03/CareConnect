"""
Pytest configuration file to set up Python path and common fixtures
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))