#!/usr/bin/env python3
"""
Download the video's transcript in its original language, translate to Arabic
using OpenAI GPT (if not already Arabic), and save as plain text.

Usage:
    python downsub.py <YouTube_URL> [--output <output_file.txt>]

Dependencies:
    pip install youtube-transcript-api openai python-dotenv

Setup:
    Copy .env.example to .env and set OPENAI_API_KEY to your API key.
"""

import os
import re
import sys
import argparse

from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from dotenv import load_dotenv

load_dotenv()

# Load API key from environment


client = OpenAI()

def get_video_id(url):
    pattern = r'(?:v=|youtu\.be/|youtube\.com/embed/)([\w-]+)'
    match = re.search(pattern, url)
    if not match:
        raise ValueError(f'Could not extract video ID from URL: {url}')
    return match.group(1)

def is_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF\u0750-\u077F]', text))
