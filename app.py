from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import google.generativeai as genai
import yt_dlp
import cv2
import os
import tempfile
import shutil
from PIL import Image
import base64
import io
from urllib.parse import urlparse, parse_qs
import re
import subprocess
import json
from ai_agent import VideoSummaryAgent

app = Flask(__name__)
CORS(app)

# Configure Gemini AI - Replace with your actual API key
GEMINI_API_KEY = "AIzaSyD02GOyvKp0o5T9dQdWuSaXl54ozzhpVck"  # Replace this with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

# Initialize AI Agent
print("🤖 Initializing AI Video Summary Agent...")
video_agent = VideoSummaryAgent(api_key=GEMINI_API_KEY)
print("✅ AI Agent ready for video analysis tasks")

def extract_video_info(url):
    """Extract video information and download video for analysis"""
    try:
        print(f"📝 Extracting video info from: {url}")
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'best[height<=720]/best',  # Download up to 720p for faster processing
            'outtmpl': '%(title)s.%(ext)s',
            'extract_flat': False,
            'writeinfojson': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info without downloading first
            info = ydl.extract_info(url, download=False)
            
            video_info = {
                'title': info.get('title', 'Unknown Title'),
                'duration': info.get('duration', 0),
                'channel': info.get('uploader', 'Unknown Channel'),
                'description': info.get('description', ''),
                'view_count': info.get('view_count', 0),
                'upload_date': info.get('upload_date', ''),
            }
            
            print(f"✅ Extracted video info: {video_info['title']}")
            return info, video_info
            
    except Exception as e:
        print(f"❌ Error extracting video info: {e}")
        return None, None

def download_video(url, output_dir):
    """Download video for analysis"""
    try:
        print(f"📝 Downloading video from: {url}")
        
        ydl_opts = {
            'format': 'best[height<=720]/best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Find the downloaded file
            video_title = info.get('title', 'video')
            ext = info.get('ext', 'mp4')
            video_path = os.path.join(output_dir, f"{video_title}.{ext}")
            
            print(f"✅ Video downloaded: {video_path}")
            return video_path, info
            
    except Exception as e:
        print(f"❌ Error downloading video: {e}")
        return None, None

def extract_frames(video_path, num_frames=8):
    """Extract key frames from video for visual analysis"""
    try:
        print(f"📝 Extracting frames from: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        print(f"📝 Video stats: {total_frames} frames, {fps} fps, {duration:.2f}s duration")
        
        # Calculate frame intervals to get evenly spaced frames
        frame_interval = max(1, total_frames // num_frames)
        frames = []
        
        for i in range(0, total_frames, frame_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)
                frames.append(pil_image)
                
                if len(frames) >= num_frames:
                    break
        
        cap.release()
        print(f"✅ Extracted {len(frames)} frames")
        return frames
        
    except Exception as e:
        print(f"❌ Error extracting frames: {e}")
        return []

def extract_audio_transcript(video_path):
    """Extract audio and convert to text using Gemini"""
    try:
        print(f"📝 Extracting audio from: {video_path}")
        
        # Extract audio using ffmpeg
        audio_path = video_path.rsplit('.', 1)[0] + '_audio.wav'
        cmd = [
            'ffmpeg', '-i', video_path, 
            '-vn', '-acodec', 'pcm_s16le', 
            '-ar', '16000', '-ac', '1', 
            audio_path, '-y'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ FFmpeg error: {result.stderr}")
            return None
            
        print(f"✅ Audio extracted: {audio_path}")
        
        # For now, return a placeholder - you can integrate Google Speech-to-Text here
        # or use Gemini's audio capabilities when available
        return "Audio transcript would be generated here using speech-to-text"
        
    except Exception as e:
        print(f"❌ Error extracting audio: {e}")
        return None

def analyze_video_content_with_agent(video_path, video_info):
    """Analyze video content using AI Agent with planning and reasoning"""
    try:
        print("🤖 Starting AI Agent-based video analysis...")
        
        # Extract visual frames
        frames = extract_frames(video_path, num_frames=8)
        if not frames:
            print("❌ No frames extracted")
            return None
            
        # Extract audio transcript
        audio_transcript = extract_audio_transcript(video_path)
        
        # Use AI Agent to plan and execute comprehensive analysis
        print("🤖 Agent taking control of analysis task...")
        agent_result = video_agent.execute_analysis(video_info, frames, audio_transcript)
        
        # Get agent status for debugging
        agent_status = video_agent.get_agent_status()
        print(f"🤖 Agent Status: {agent_status['actions_taken']} actions taken")
        
        # Prepare comprehensive result
        return {
            'summary': agent_result['summary'],
            'visual_frames_analyzed': len(frames),
            'audio_processed': audio_transcript is not None,
            'analysis_type': 'ai_agent_comprehensive_analysis',
            'quality_score': agent_result.get('quality_score', 'N/A'),
            'agent_reasoning': agent_result.get('agent_reasoning', ''),
            'analysis_steps_completed': agent_result.get('analysis_steps_completed', []),
            'agent_id': video_agent.agent_id,
            'agent_actions_count': agent_status['actions_taken']
        }
        
    except Exception as e:
        print(f"❌ Error in AI Agent video analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

# Legacy function for backward compatibility
def analyze_video_content(video_path, video_info):
    """Legacy wrapper that redirects to AI Agent analysis"""
    print("🔄 Redirecting to AI Agent analysis...")
    return analyze_video_content_with_agent(video_path, video_info)

@app.route('/')
def index():
    """Serve the main HTML page"""
    try:
        with open('index.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Frontend files not found. Please make sure index.html is in the same directory.", 404

@app.route('/style.css')
def css():
    """Serve CSS file"""
    try:
        with open('style.css', 'r') as f:
            css_content = f.read()
        response = app.response_class(
            response=css_content,
            status=200,
            mimetype='text/css'
        )
        return response
    except FileNotFoundError:
        return "CSS file not found", 404

@app.route('/script.js')
def js():
    """Serve JavaScript file"""
    try:
        with open('script.js', 'r') as f:
            js_content = f.read()
        response = app.response_class(
            response=js_content,
            status=200,
            mimetype='application/javascript'
        )
        return response
    except FileNotFoundError:
        return "JavaScript file not found", 404

@app.route('/api/summarize', methods=['POST'])
def summarize_video():
    """API endpoint to analyze and summarize YouTube videos using AI vision and audio analysis"""
    temp_dir = None
    try:
        print("📝 Received request to /api/summarize")
        data = request.get_json()
        print(f"📝 Request data: {data}")
        
        if not data or 'url' not in data:
            print("❌ No URL provided in request")
            return jsonify({'error': 'YouTube URL is required'}), 400
        
        youtube_url = data['url']
        print(f"📝 Processing YouTube URL: {youtube_url}")
        
        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp()
        print(f"📝 Created temp directory: {temp_dir}")
        
        # Extract video information first (without downloading)
        video_info_raw, video_info = extract_video_info(youtube_url)
        if not video_info:
            print("❌ Could not extract video information")
            return jsonify({'error': 'Invalid YouTube URL or video not accessible'}), 400
        
        print(f"✅ Video info extracted: {video_info['title']}")
        
        # Download video for analysis
        print("📝 Downloading video for analysis...")
        video_path, download_info = download_video(youtube_url, temp_dir)
        
        if not video_path or not os.path.exists(video_path):
            print("❌ Could not download video")
            return jsonify({
                'error': 'Could not download video for analysis. The video may be private or restricted.',
                'suggestion': 'Try a different public YouTube video.'
            }), 400
        
        print(f"✅ Video downloaded successfully: {video_path}")
        
        # Analyze video content
        print("📝 Starting comprehensive video analysis...")
        analysis_result = analyze_video_content(video_path, video_info)
        
        if not analysis_result:
            print("❌ Video analysis failed")
            return jsonify({'error': 'Failed to analyze video content'}), 500
        
        print("✅ Video analysis completed successfully")
        
        # Prepare response
        response_data = {
            'summary': analysis_result['summary'],
            'video_info': {
                'title': video_info['title'],
                'duration': f"{video_info['duration']} seconds" if video_info['duration'] else 'N/A',
                'channel': video_info['channel'],
                'view_count': video_info.get('view_count', 'N/A'),
                'upload_date': video_info.get('upload_date', 'N/A')
            },
            'analysis_details': {
                'frames_analyzed': analysis_result['visual_frames_analyzed'],
                'audio_processed': analysis_result['audio_processed'],
                'analysis_type': analysis_result['analysis_type']
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error in summarize_video: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
        
    finally:
        # Clean up temporary files
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                print(f"🧹 Cleaned up temp directory: {temp_dir}")
            except Exception as e:
                print(f"⚠️ Warning: Could not clean up temp directory: {e}")

# Add a simple test endpoint
@app.route('/api/test', methods=['GET'])
def test_api():
    """Test endpoint to verify API is working"""
    return jsonify({'status': 'API is working!', 'timestamp': str(os.popen('date').read().strip())})

# Add agent status endpoint
@app.route('/api/agent/status', methods=['GET'])
def get_agent_status():
    """Get current AI agent status and capabilities"""
    try:
        agent_status = video_agent.get_agent_status()
        return jsonify({
            'agent_info': agent_status,
            'capabilities': list(video_agent.available_tools.keys()),
            'model_name': video_agent.model_name,
            'status': 'active'
        })
    except Exception as e:
        return jsonify({'error': f'Could not get agent status: {str(e)}'}), 500

# Add agent reset endpoint
@app.route('/api/agent/reset', methods=['POST'])
def reset_agent():
    """Reset the AI agent state and memory"""
    try:
        global video_agent
        video_agent = VideoSummaryAgent(api_key=GEMINI_API_KEY)
        return jsonify({
            'status': 'Agent reset successfully',
            'new_agent_id': video_agent.agent_id
        })
    except Exception as e:
        return jsonify({'error': f'Could not reset agent: {str(e)}'}), 500

if __name__ == '__main__':
    # Check if API key is configured
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        print("⚠️  WARNING: Please replace 'YOUR_GEMINI_API_KEY_HERE' with your actual Gemini API key in app.py")
        print("You can get your API key from: https://makersuite.google.com/app/apikey")
    
    print("🚀 Starting YouTube Summarizer Server...")
    print("📝 Make sure to install required packages:")
    print("   pip install flask flask-cors google-generativeai youtube-transcript-api")
    print("\n🌐 Open your browser and go to: http://localhost:8080")
    
    app.run(debug=True, host='0.0.0.0', port=8080) 