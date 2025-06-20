document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('summaryForm');
    const generateBtn = document.getElementById('generateBtn');
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');
    const resultContainer = document.getElementById('resultContainer');
    const errorContainer = document.getElementById('errorContainer');
    const videoInfo = document.getElementById('videoInfo');
    const summary = document.getElementById('summary');
    const errorMessage = document.getElementById('errorMessage');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const youtubeUrl = document.getElementById('youtubeUrl').value.trim();
        
        if (!youtubeUrl) {
            showError('Please enter a YouTube URL');
            return;
        }

        // Validate YouTube URL format
        if (!isValidYouTubeUrl(youtubeUrl)) {
            showError('Please enter a valid YouTube URL');
            return;
        }

        // Show loading state
        setLoadingState(true);
        hideResults();

        try {
            const response = await fetch('/api/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: youtubeUrl
                })
            });

            const data = await response.json();

            if (!response.ok) {
                let errorMessage = data.error || 'Failed to generate summary';
                if (data.suggestion) {
                    errorMessage += '\n\n' + data.suggestion;
                }
                if (data.example_url) {
                    errorMessage += '\n\nExample: ' + data.example_url;
                }
                throw new Error(errorMessage);
            }

            showResults(data);
            
        } catch (error) {
            console.error('Error:', error);
            showError(error.message || 'An error occurred while generating the summary');
        } finally {
            setLoadingState(false);
        }
    });

    function isValidYouTubeUrl(url) {
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|embed\/)|youtu\.be\/)[\w-]+/;
        return youtubeRegex.test(url);
    }

    function setLoadingState(isLoading) {
        generateBtn.disabled = isLoading;
        
        if (isLoading) {
            btnText.style.display = 'none';
            loader.style.display = 'block';
        } else {
            btnText.style.display = 'block';
            loader.style.display = 'none';
        }
    }

    function showResults(data) {
        hideError();
        
        // Display video information if available
        if (data.video_info) {
            let analysisInfo = '';
            if (data.analysis_details) {
                // Enhanced analysis info with agent details
                let agentInfo = '';
                if (data.analysis_details.agent_id) {
                    agentInfo = `
                        <div style="background: #f0f9ff; padding: 8px; border-radius: 4px; margin-top: 8px; border-left: 3px solid #0ea5e9;">
                            <strong>🤖 AI Agent Details:</strong><br>
                            • Agent ID: ${data.analysis_details.agent_id}<br>
                            • Actions performed: ${data.analysis_details.agent_actions_count}<br>
                            • Quality score: ${data.analysis_details.quality_score}<br>
                            • Analysis steps: ${data.analysis_details.analysis_steps_completed?.join(', ') || 'N/A'}<br>
                            • Agent reasoning: ${data.analysis_details.agent_reasoning || 'N/A'}
                        </div>
                    `;
                }
                
                analysisInfo = `
                    <div style="background: #e8f4f8; padding: 10px; border-radius: 5px; margin-top: 10px; font-size: 0.9em;">
                        <strong>🎬 Analysis Details:</strong><br>
                        • Visual frames analyzed: ${data.analysis_details.frames_analyzed}<br>
                        • Audio processed: ${data.analysis_details.audio_processed ? 'Yes' : 'No'}<br>
                        • Analysis type: ${data.analysis_details.analysis_type.replace(/_/g, ' ')}<br>
                        • View count: ${data.video_info.view_count}<br>
                        • Upload date: ${data.video_info.upload_date}
                        ${agentInfo}
                    </div>
                `;
            }
            
            videoInfo.innerHTML = `
                <h3>${data.video_info.title || 'Video Title'}</h3>
                <p><strong>Duration:</strong> ${data.video_info.duration || 'N/A'}</p>
                <p><strong>Channel:</strong> ${data.video_info.channel || 'N/A'}</p>
                ${analysisInfo}
            `;
        } else {
            videoInfo.innerHTML = '<p>Video information not available</p>';
        }
        
        // Display summary
        summary.innerHTML = data.summary || 'Summary not available';
        
        resultContainer.style.display = 'block';
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }

    function showError(message) {
        hideResults();
        errorMessage.textContent = message;
        errorContainer.style.display = 'block';
        errorContainer.scrollIntoView({ behavior: 'smooth' });
    }

    function hideResults() {
        resultContainer.style.display = 'none';
    }

    function hideError() {
        errorContainer.style.display = 'none';
    }

    // Agent status functions
    window.loadAgentStatus = async function() {
        try {
            const response = await fetch('/api/agent/status');
            const data = await response.json();
            
            if (response.ok) {
                const statusText = document.querySelector('.status-text');
                const statusIndicator = document.querySelector('.status-indicator');
                
                statusText.textContent = `Agent ${data.agent_info.agent_id.split('_')[1]} - ${data.agent_info.actions_taken} actions`;
                statusIndicator.textContent = '🟢';
                
                // Show detailed status in console
                console.log('🤖 AI Agent Status:', data);
                
                // Optionally show status in UI
                showAgentDetails(data);
            } else {
                console.error('Failed to get agent status:', data.error);
            }
        } catch (error) {
            console.error('Error fetching agent status:', error);
            const statusText = document.querySelector('.status-text');
            const statusIndicator = document.querySelector('.status-indicator');
            statusText.textContent = 'Agent Status Unknown';
            statusIndicator.textContent = '🔴';
        }
    };

    function showAgentDetails(agentData) {
        const details = `
            Agent Information:
            • ID: ${agentData.agent_info.agent_id}
            • Actions Taken: ${agentData.agent_info.actions_taken}
            • Cached Analyses: ${agentData.agent_info.cached_analyses.join(', ') || 'None'}
            • Model: ${agentData.model_name}
            • Capabilities: ${agentData.capabilities.join(', ')}
        `;
        
        alert(details);
    }

    // Load agent status on page load
    window.addEventListener('load', loadAgentStatus);
}); 