# YouTube Video Summarizer with AI Agent

An advanced web application powered by an intelligent AI agent that plans, executes, and refines comprehensive video summaries using Google's Gemini AI with visual and audio analysis.

## 🌟 Features

### 🤖 **AI Agent Architecture**
- **Autonomous Planning**: AI agent creates custom analysis plans for each video
- **Self-Reflection**: Agent evaluates and improves its own summaries
- **Memory Management**: Persistent context and learning across sessions
- **Task Decomposition**: Breaks complex analysis into manageable steps
- **Quality Assurance**: Built-in quality scoring and refinement processes

### 🎬 **Advanced Video Analysis**
- **Visual Analysis**: Extracts and analyzes key frames using Gemini Vision
- **Audio Processing**: Processes audio content for speech analysis
- **Metadata Intelligence**: Comprehensive video metadata analysis
- **No Transcript Dependency**: Works independently of YouTube's transcript API
- **Multi-Modal Synthesis**: Combines visual, audio, and textual information

### 🎨 **User Experience**
- **Beautiful UI**: Modern, responsive interface with agent status indicators
- **Real-time Monitoring**: Live agent activity and reasoning transparency
- **Agent Insights**: Detailed breakdown of agent's decision-making process
- **Mobile Optimized**: Perfect experience on all device sizes
- **Progress Tracking**: Step-by-step analysis progress visualization

## Setup Instructions

### 1. Install System Dependencies

First, make sure you have **FFmpeg** installed (required for video/audio processing):

**On macOS:**
```bash
brew install ffmpeg
```

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**On Windows:**
Download from [FFmpeg official website](https://ffmpeg.org/download.html)

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 4. Configure API Key

Open `app.py` and replace `YOUR_GEMINI_API_KEY_HERE` with your actual Gemini API key:

```python
GEMINI_API_KEY = "your_actual_api_key_here"
```

### 5. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:8080`

## Usage

1. Open your web browser and navigate to `http://localhost:8080`
2. Enter a YouTube URL in the input field
3. Click "Generate Summary"
4. Watch the AI Agent work:
   - **Plan**: Agent creates a custom analysis strategy
   - **Download**: Retrieves video for local processing
   - **Extract**: Captures visual frames and audio content
   - **Analyze**: Multi-modal content analysis
   - **Synthesize**: Combines all insights
   - **Refine**: Self-evaluates and improves the summary
5. Read your AI agent's comprehensive analysis and summary!

## Supported YouTube URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

## Requirements

- Python 3.7+
- Internet connection
- YouTube videos with available transcripts/captions

## Dependencies

- **Flask**: Web framework for the backend
- **Flask-CORS**: Cross-origin resource sharing
- **google-generativeai**: Google's Gemini AI SDK
- **youtube-transcript-api**: Extract YouTube video transcripts
- **requests**: HTTP library

## File Structure

```
├── app.py              # Flask backend server
├── index.html          # Frontend HTML
├── style.css           # CSS styling
├── script.js           # Frontend JavaScript
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Troubleshooting

### Common Issues

1. **"Could not retrieve video transcript"**
   - The video may not have captions/transcripts available
   - Try with a different video that has captions

2. **"Invalid YouTube URL"**
   - Make sure you're using a valid YouTube URL format
   - Check that the video ID is correct

3. **"Error generating summary"**
   - Check your Gemini API key is correct
   - Ensure you have API quota remaining
   - Check your internet connection

### API Key Issues

- Make sure your API key is valid and active
- Check that you have sufficient quota in Google AI Studio
- Ensure there are no extra spaces or characters in the API key

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements. 