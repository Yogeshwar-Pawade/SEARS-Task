#!/usr/bin/env python3
"""
Debug script for YouTube URL processing issues
Run this to test YouTube URL access and identify specific problems
"""

import yt_dlp
import sys
import traceback
from urllib.parse import urlparse, parse_qs

def test_youtube_url(url):
    """Test YouTube URL access with detailed debugging"""
    print(f"🧪 Testing YouTube URL: {url}")
    print("=" * 50)
    
    # 1. Basic URL validation
    print("1️⃣ Basic URL validation...")
    if not url or not isinstance(url, str):
        print("❌ Invalid URL: URL must be a non-empty string")
        return False
    
    if not any(domain in url.lower() for domain in ['youtube.com', 'youtu.be', 'm.youtube.com']):
        print("❌ Invalid URL: Must be a YouTube URL")
        return False
    
    print("✅ URL format is valid")
    
    # 2. Parse URL components
    print("\n2️⃣ URL parsing...")
    try:
        parsed = urlparse(url)
        print(f"   Domain: {parsed.netloc}")
        print(f"   Path: {parsed.path}")
        
        if 'youtube.com' in parsed.netloc:
            query_params = parse_qs(parsed.query)
            video_id = query_params.get('v', [None])[0]
            if video_id:
                print(f"   Video ID: {video_id}")
        elif 'youtu.be' in parsed.netloc:
            video_id = parsed.path.lstrip('/')
            print(f"   Video ID: {video_id}")
    except Exception as e:
        print(f"   ⚠️ URL parsing issue: {e}")
    
    # 3. Test yt-dlp access
    print("\n3️⃣ Testing yt-dlp access...")
    
    ydl_opts = {
        'quiet': False,
        'verbose': True,
        'no_warnings': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '300',
            'Connection': 'keep-alive',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("   🔍 Extracting video information...")
            info = ydl.extract_info(url, download=False)
            
            if not info:
                print("   ❌ No video information returned")
                return False
            
            print("   ✅ Video information extracted successfully!")
            print(f"   📺 Title: {info.get('title', 'Unknown')}")
            print(f"   ⏱️ Duration: {info.get('duration', 'Unknown')} seconds")
            print(f"   👤 Channel: {info.get('uploader', 'Unknown')}")
            print(f"   👁️ Views: {info.get('view_count', 'Unknown')}")
            print(f"   🌐 Availability: {info.get('availability', 'Unknown')}")
            print(f"   🔞 Age limit: {info.get('age_limit', 0)}")
            
            # Check accessibility
            availability = info.get('availability', '')
            if availability in ['private', 'premium_only', 'subscriber_only']:
                print(f"   ⚠️ Video accessibility issue: {availability}")
                return False
            
            return True
            
    except yt_dlp.DownloadError as e:
        error_msg = str(e)
        print(f"   ❌ yt-dlp Download Error: {error_msg}")
        
        # Provide specific guidance
        if "private video" in error_msg.lower():
            print("   💡 Issue: Video is private")
        elif "video unavailable" in error_msg.lower():
            print("   💡 Issue: Video is unavailable or removed")
        elif "age-restricted" in error_msg.lower() or "sign in" in error_msg.lower():
            print("   💡 Issue: Video is age-restricted or requires sign-in")
        elif "copyright" in error_msg.lower():
            print("   💡 Issue: Video has copyright restrictions")
        elif "region" in error_msg.lower() or "location" in error_msg.lower():
            print("   💡 Issue: Video is region-locked")
        else:
            print(f"   💡 Issue: {error_msg}")
        
        return False
        
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        print(f"   📋 Error type: {type(e).__name__}")
        traceback.print_exc()
        return False

def main():
    """Main function to run URL tests"""
    print("🔧 YouTube URL Debug Tool")
    print("=" * 50)
    
    # Test URLs
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll - known working
        "https://youtu.be/dQw4w9WgXcQ",  # Short format
    ]
    
    if len(sys.argv) > 1:
        # Test user-provided URL
        user_url = sys.argv[1]
        print(f"Testing user-provided URL: {user_url}")
        test_youtube_url(user_url)
    else:
        # Test known working URLs
        print("Testing known working URLs...")
        for url in test_urls:
            print(f"\nTesting: {url}")
            result = test_youtube_url(url)
            print(f"Result: {'✅ PASSED' if result else '❌ FAILED'}")
            print("-" * 50)
    
    print("\n🏁 Debug session complete!")
    print("💡 Usage: python debug_youtube.py [youtube_url]")

if __name__ == "__main__":
    main() 