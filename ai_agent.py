import google.generativeai as genai
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

class VideoSummaryAgent:
    """
    Advanced AI Agent for comprehensive video analysis and summarization.
    This agent can plan, execute, reflect, and improve its summarization process.
    """
    
    def __init__(self, api_key: str, model_name: str = 'gemini-1.5-flash'):
        """Initialize the AI agent with memory and reasoning capabilities"""
        self.api_key = api_key
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        # Agent memory and state
        self.conversation_history = []
        self.task_memory = {}
        self.analysis_cache = {}
        self.agent_id = f"VideoAgent_{int(time.time())}"
        
        # Agent capabilities and tools
        self.available_tools = {
            'visual_analysis': self._analyze_visual_content,
            'audio_analysis': self._analyze_audio_content,
            'metadata_analysis': self._analyze_metadata,
            'content_synthesis': self._synthesize_content,
            'quality_check': self._quality_check_summary,
            'refinement': self._refine_summary
        }
        
        print(f"🤖 AI Agent initialized: {self.agent_id}")
        print(f"🧠 Available tools: {list(self.available_tools.keys())}")
    
    def _log_agent_action(self, action: str, details: str = ""):
        """Log agent actions for transparency"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'action': action,
            'details': details,
            'agent_id': self.agent_id
        }
        self.conversation_history.append(log_entry)
        print(f"🤖 [{timestamp}] Agent Action: {action}")
        if details:
            print(f"   └─ {details}")
    
    def plan_analysis_task(self, video_info: Dict, frames: List, audio_transcript: str = None) -> Dict:
        """
        Agent plans the analysis task based on available data
        """
        self._log_agent_action("PLANNING", "Analyzing available data and creating execution plan")
        
        # Assess what data is available
        available_data = {
            'video_metadata': bool(video_info),
            'visual_frames': len(frames) if frames else 0,
            'audio_content': bool(audio_transcript),
            'video_duration': video_info.get('duration', 0) if video_info else 0
        }
        
        # Create analysis plan based on available data
        planning_prompt = f"""
        As an AI video analysis agent, create a comprehensive analysis plan for this video:
        
        Available Data:
        - Video metadata: {available_data['video_metadata']}
        - Visual frames: {available_data['visual_frames']} frames
        - Audio content: {available_data['audio_content']}
        - Duration: {available_data['video_duration']} seconds
        
        Video Information:
        - Title: {video_info.get('title', 'Unknown')}
        - Channel: {video_info.get('channel', 'Unknown')}
        - Description: {video_info.get('description', '')[:200]}...
        
        Create a step-by-step analysis plan that includes:
        1. Priority order of analysis steps
        2. Expected insights from each step
        3. How to combine different analysis results
        4. Quality criteria for the final summary
        
        Return your plan in a structured format.
        """
        
        try:
            response = self.model.generate_content(planning_prompt)
            plan_text = response.text
            
            # Create structured plan
            analysis_plan = {
                'plan_text': plan_text,
                'available_data': available_data,
                'priority_steps': self._extract_priority_steps(plan_text),
                'expected_insights': self._extract_expected_insights(plan_text),
                'quality_criteria': self._extract_quality_criteria(plan_text),
                'created_at': datetime.now().isoformat()
            }
            
            self.task_memory['analysis_plan'] = analysis_plan
            self._log_agent_action("PLAN_CREATED", f"Created {len(analysis_plan['priority_steps'])} step plan")
            
            return analysis_plan
            
        except Exception as e:
            self._log_agent_action("PLAN_ERROR", f"Planning failed: {e}")
            return self._create_fallback_plan(available_data)
    
    def execute_analysis(self, video_info: Dict, frames: List, audio_transcript: str = None) -> Dict:
        """
        Execute the planned analysis with agent reasoning
        """
        self._log_agent_action("EXECUTION_START", "Beginning comprehensive video analysis")
        
        # Get or create analysis plan
        if 'analysis_plan' not in self.task_memory:
            self.plan_analysis_task(video_info, frames, audio_transcript)
        
        plan = self.task_memory['analysis_plan']
        analysis_results = {}
        
        # Execute each analysis step
        for step in plan['priority_steps']:
            step_name = step.lower().replace(' ', '_')
            
            if 'visual' in step_name and frames:
                analysis_results['visual'] = self._analyze_visual_content(frames, video_info)
            elif 'audio' in step_name and audio_transcript:
                analysis_results['audio'] = self._analyze_audio_content(audio_transcript, video_info)
            elif 'metadata' in step_name:
                analysis_results['metadata'] = self._analyze_metadata(video_info)
        
        # Synthesize all analysis results
        self._log_agent_action("SYNTHESIS", "Combining all analysis results")
        synthesis_result = self._synthesize_content(analysis_results, video_info)
        
        # Quality check and refinement
        self._log_agent_action("QUALITY_CHECK", "Evaluating summary quality")
        quality_score = self._quality_check_summary(synthesis_result, plan['quality_criteria'])
        
        # Refine if needed
        if quality_score < 0.8:  # If quality is below 80%
            self._log_agent_action("REFINEMENT", f"Quality score: {quality_score:.2f}, refining summary")
            synthesis_result = self._refine_summary(synthesis_result, analysis_results)
        
        final_result = {
            'summary': synthesis_result,
            'analysis_steps_completed': list(analysis_results.keys()),
            'quality_score': quality_score,
            'agent_reasoning': self._generate_reasoning_explanation(),
            'execution_time': datetime.now().isoformat()
        }
        
        self._log_agent_action("EXECUTION_COMPLETE", f"Analysis completed with quality score: {quality_score:.2f}")
        return final_result
    
    def _analyze_visual_content(self, frames: List, video_info: Dict) -> Dict:
        """Analyze visual content with agent reasoning"""
        self._log_agent_action("VISUAL_ANALYSIS", f"Analyzing {len(frames)} visual frames")
        
        visual_prompt = f"""
        As an expert video content analyst, analyze these visual frames comprehensively:
        
        Video Context:
        - Title: {video_info.get('title', 'Unknown')}
        - Duration: {video_info.get('duration', 0)} seconds
        
        For each frame, identify:
        1. Main visual elements and composition
        2. Text content (if any)
        3. People, objects, or scenes
        4. Visual themes and patterns
        5. Technical quality and production style
        
        Provide a comprehensive visual analysis that captures the essence of the video content.
        """
        
        try:
            content = [visual_prompt]
            for i, frame in enumerate(frames[:6]):  # Limit to 6 frames
                content.append(f"Frame {i+1} (timestamp: {i * (video_info.get('duration', 0) / len(frames)):.1f}s):")
                content.append(frame)
            
            response = self.model.generate_content(content)
            
            visual_analysis = {
                'analysis': response.text,
                'frames_processed': len(frames),
                'key_insights': self._extract_key_insights(response.text),
                'visual_themes': self._extract_visual_themes(response.text)
            }
            
            self.analysis_cache['visual'] = visual_analysis
            return visual_analysis
            
        except Exception as e:
            self._log_agent_action("VISUAL_ERROR", f"Visual analysis failed: {e}")
            return {'analysis': 'Visual analysis unavailable', 'error': str(e)}
    
    def _analyze_audio_content(self, audio_transcript: str, video_info: Dict) -> Dict:
        """Analyze audio content with agent reasoning"""
        self._log_agent_action("AUDIO_ANALYSIS", "Processing audio content")
        
        audio_prompt = f"""
        As an expert audio content analyst, analyze this audio content:
        
        Video Title: {video_info.get('title', 'Unknown')}
        Audio Content: {audio_transcript[:2000]}
        
        Analyze:
        1. Speech patterns and communication style
        2. Key topics and themes discussed
        3. Emotional tone and delivery
        4. Information density and structure
        5. Technical terminology or specialized content
        
        Provide insights that complement visual analysis.
        """
        
        try:
            response = self.model.generate_content(audio_prompt)
            
            audio_analysis = {
                'analysis': response.text,
                'transcript_length': len(audio_transcript),
                'key_topics': self._extract_key_topics(response.text),
                'tone_analysis': self._extract_tone_analysis(response.text)
            }
            
            self.analysis_cache['audio'] = audio_analysis
            return audio_analysis
            
        except Exception as e:
            self._log_agent_action("AUDIO_ERROR", f"Audio analysis failed: {e}")
            return {'analysis': 'Audio analysis unavailable', 'error': str(e)}
    
    def _analyze_metadata(self, video_info: Dict) -> Dict:
        """Analyze video metadata with agent reasoning"""
        self._log_agent_action("METADATA_ANALYSIS", "Processing video metadata")
        
        metadata_analysis = {
            'title_analysis': self._analyze_title(video_info.get('title', '')),
            'channel_context': video_info.get('channel', 'Unknown'),
            'duration_analysis': self._analyze_duration(video_info.get('duration', 0)),
            'description_insights': self._analyze_description(video_info.get('description', '')),
            'engagement_metrics': {
                'view_count': video_info.get('view_count', 'N/A'),
                'upload_date': video_info.get('upload_date', 'N/A')
            }
        }
        
        self.analysis_cache['metadata'] = metadata_analysis
        return metadata_analysis
    
    def _synthesize_content(self, analysis_results: Dict, video_info: Dict) -> str:
        """Synthesize all analysis results into a comprehensive summary"""
        self._log_agent_action("CONTENT_SYNTHESIS", "Creating comprehensive summary")
        
        synthesis_prompt = f"""
        As an expert content synthesizer, create a comprehensive video summary by combining these analysis results:
        
        Video: {video_info.get('title', 'Unknown')}
        Channel: {video_info.get('channel', 'Unknown')}
        Duration: {video_info.get('duration', 0)} seconds
        
        Analysis Results:
        {json.dumps(analysis_results, indent=2, default=str)}
        
        Create a well-structured summary with:
        1. Executive Summary (2-3 sentences)
        2. Visual Content Overview
        3. Key Topics and Themes
        4. Main Insights and Takeaways
        5. Production Quality and Style Notes
        
        Make it engaging, informative, and comprehensive.
        """
        
        try:
            response = self.model.generate_content(synthesis_prompt)
            return response.text
        except Exception as e:
            self._log_agent_action("SYNTHESIS_ERROR", f"Content synthesis failed: {e}")
            return "Summary generation failed. Please try again."
    
    def _quality_check_summary(self, summary: str, quality_criteria: List) -> float:
        """Check the quality of the generated summary"""
        self._log_agent_action("QUALITY_ASSESSMENT", "Evaluating summary quality")
        
        # Simple quality scoring based on summary characteristics
        score = 0.5  # Base score
        
        # Check length (should be substantial but not too long)
        if 500 <= len(summary) <= 2000:
            score += 0.2
        
        # Check structure (should have multiple sections)
        if summary.count('\n\n') >= 3:
            score += 0.1
        
        # Check for key elements
        key_elements = ['summary', 'overview', 'key', 'main', 'insights']
        found_elements = sum(1 for element in key_elements if element.lower() in summary.lower())
        score += (found_elements / len(key_elements)) * 0.2
        
        return min(score, 1.0)
    
    def _refine_summary(self, summary: str, analysis_results: Dict) -> str:
        """Refine the summary based on quality assessment"""
        self._log_agent_action("SUMMARY_REFINEMENT", "Improving summary quality")
        
        refinement_prompt = f"""
        As an expert editor, improve this video summary:
        
        Current Summary:
        {summary}
        
        Available Analysis Data:
        {json.dumps(analysis_results, indent=2, default=str)}
        
        Improve by:
        1. Making it more engaging and readable
        2. Adding specific details from the analysis
        3. Improving structure and flow
        4. Ensuring comprehensive coverage
        5. Adding compelling insights
        
        Return the refined summary:
        """
        
        try:
            response = self.model.generate_content(refinement_prompt)
            return response.text
        except Exception as e:
            self._log_agent_action("REFINEMENT_ERROR", f"Summary refinement failed: {e}")
            return summary  # Return original if refinement fails
    
    def _generate_reasoning_explanation(self) -> str:
        """Generate explanation of agent's reasoning process"""
        actions = [entry['action'] for entry in self.conversation_history[-10:]]  # Last 10 actions
        return f"Agent completed analysis using steps: {' → '.join(actions)}"
    
    # Helper methods for extracting insights
    def _extract_priority_steps(self, plan_text: str) -> List[str]:
        """Extract priority steps from plan text"""
        # Simple extraction - in a real implementation, you might use more sophisticated NLP
        steps = ['Visual Analysis', 'Audio Analysis', 'Metadata Analysis', 'Content Synthesis']
        return steps
    
    def _extract_expected_insights(self, plan_text: str) -> List[str]:
        """Extract expected insights from plan text"""
        return ['Visual themes', 'Audio content', 'Metadata context', 'Comprehensive summary']
    
    def _extract_quality_criteria(self, plan_text: str) -> List[str]:
        """Extract quality criteria from plan text"""
        return ['Comprehensive coverage', 'Clear structure', 'Engaging content', 'Accurate analysis']
    
    def _create_fallback_plan(self, available_data: Dict) -> Dict:
        """Create a fallback plan if planning fails"""
        return {
            'plan_text': 'Fallback analysis plan',
            'available_data': available_data,
            'priority_steps': ['Visual Analysis', 'Content Synthesis'],
            'expected_insights': ['Basic insights'],
            'quality_criteria': ['Basic quality'],
            'created_at': datetime.now().isoformat()
        }
    
    def _extract_key_insights(self, text: str) -> List[str]:
        """Extract key insights from analysis text"""
        # Placeholder - could use more sophisticated NLP
        return ['Key insight extracted from analysis']
    
    def _extract_visual_themes(self, text: str) -> List[str]:
        """Extract visual themes from analysis text"""
        return ['Visual theme identified']
    
    def _extract_key_topics(self, text: str) -> List[str]:
        """Extract key topics from analysis text"""
        return ['Key topic identified']
    
    def _extract_tone_analysis(self, text: str) -> str:
        """Extract tone analysis from text"""
        return 'Tone analysis completed'
    
    def _analyze_title(self, title: str) -> str:
        """Analyze video title"""
        return f"Title suggests: {title[:50]}..."
    
    def _analyze_duration(self, duration: int) -> str:
        """Analyze video duration"""
        if duration < 300:  # 5 minutes
            return "Short-form content"
        elif duration < 1800:  # 30 minutes
            return "Medium-form content"
        else:
            return "Long-form content"
    
    def _analyze_description(self, description: str) -> str:
        """Analyze video description"""
        return f"Description length: {len(description)} characters"
    
    def get_agent_status(self) -> Dict:
        """Get current agent status and memory"""
        return {
            'agent_id': self.agent_id,
            'actions_taken': len(self.conversation_history),
            'cached_analyses': list(self.analysis_cache.keys()),
            'task_memory_keys': list(self.task_memory.keys()),
            'last_action': self.conversation_history[-1] if self.conversation_history else None
        } 