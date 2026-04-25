import os
import json
import inspect

import ollama

from dotenv import load_dotenv
from pathlib import Path
from typing import Any, Dict, List, Tuple

from constants import *

load_dotenv()

ollama_client = ollama.Client()
