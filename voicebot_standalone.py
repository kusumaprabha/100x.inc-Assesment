#!/usr/bin/env python3
"""
Personal Voice Bot - Interactive Demo
Converted from HTML to Python Flask Application
Complete preservation of all HTML content
"""

from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# COMPLETE HTML TEMPLATE - NO TRIMMING
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personal Voice Bot - Interactive Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 900px;
            width: 100%;
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }

        .chat-container {
            height: 450px;
            overflow-y: auto;
            padding: 30px;
            background: #f8f9fa;
        }

        .message {
            margin-bottom: 20px;
            display: flex;
            align-items: flex-start;
            animation: fadeIn 0.3s;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            justify-content: flex-end;
        }

        .message-content {
            max-width: 75%;
            padding: 15px 20px;
            border-radius: 15px;
            line-height: 1.6;
            white-space: pre-line;
        }

        .message.bot .message-content {
            background: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }

        .message.user .message-content {
            background: #667eea;
            color: white;
        }

        .input-container {
            padding: 20px 30px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 15px;
        }

        #userInput {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }

        #userInput:focus {
            border-color: #667eea;
        }

        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .btn:hover {
            transform: translateY(-2px);
        }

        .btn-send {
            background: #667eea;
            color: white;
        }

        .btn-send:hover {
            background: #5568d3;
        }

        .btn-voice {
            background: #764ba2;
            color: white;
            width: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }

        .btn-voice:hover {
            background: #643a8a;
        }

        .btn-voice.listening {
            background: #e74c3c;
            animation: pulse 1s infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }

        .suggestions {
            padding: 20px 30px;
            background: #f8f9fa;
            border-top: 1px solid #e0e0e0;
        }

        .suggestions h3 {
            margin-bottom: 15px;
            color: #333;
            font-size: 1em;
        }

        .suggestion-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .chip {
            padding: 10px 18px;
            background: white;
            border: 2px solid #667eea;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            color: #667eea;
            transition: all 0.3s;
        }

        .chip:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }

        .status {
            text-align: center;
            padding: 10px;
            font-size: 14px;
            color: #666;
            min-height: 30px;
        }

        .typing-indicator {
            display: none;
            padding: 15px 20px;
            background: white;
            border-radius: 15px;
            border-left: 4px solid #667eea;
            width: fit-content;
        }

        .typing-indicator.active {
            display: block;
        }

        .dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #667eea;
            margin: 0 3px;
            animation: typing 1.4s infinite;
        }

        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎤 Personal Voice Bot</h1>
            <p>Ask me about my background, skills, and aspirations!</p>
        </div>

        <div class="chat-container" id="chatContainer">
            <div class="message bot">
                <div class="message-content">
                    Hi! I'm your personal voice bot. You can ask me about my life story, superpowers, 
                    growth areas, misconceptions people have about me, or how I push my boundaries. 
                    Feel free to speak or type your questions!
                </div>
            </div>
        </div>

        <div class="suggestions">
            <h3>💡 Try asking:</h3>
            <div class="suggestion-chips">
                <div class="chip" onclick="askQuestion('What should we know about your life story?')">📖 Life Story</div>
                <div class="chip" onclick="askQuestion('What is your #1 superpower?')">⚡ Superpower</div>
                <div class="chip" onclick="askQuestion('What are the top 3 areas you would like to grow in?')">🌱 Growth Areas</div>
                <div class="chip" onclick="askQuestion('What misconception do your coworkers have about you?')">🤔 Misconceptions</div>
                <div class="chip" onclick="askQuestion('How do you push your boundaries and limits?')">🚀 Push Boundaries</div>
            </div>
        </div>

        <div class="input-container">
            <input type="text" id="userInput" placeholder="Type your question or click the mic to speak..." 
                   onkeypress="handleKeyPress(event)">
            <button class="btn btn-voice" id="voiceBtn" onclick="toggleVoice()">🎤</button>
            <button class="btn btn-send" onclick="sendMessage()">Send</button>
        </div>

        <div class="status" id="status"></div>
    </div>

    <script>
        // Personal responses database - CUSTOMIZE THESE TO YOUR OWN ANSWERS
        const RESPONSES = {
            life_story: `I'm a software engineer passionate about building innovative solutions that make a real impact. 
I started coding in high school when I discovered the magic of turning ideas into reality through code. 
Since then, I've been on an incredible journey of continuous learning, working on everything from web applications to AI-powered tools. 
What drives me is the intersection of technology and human experience—creating solutions that are not just functional, but truly delightful to use.`,

            superpower: `My #1 superpower is pattern recognition and connecting dots across different domains. 
I have this ability to quickly identify similarities between seemingly unrelated problems and apply creative solutions from one field to another. 
Whether it's recognizing a design pattern from architecture that could solve a coding challenge, or applying game theory to user experience design, 
I thrive on these cross-pollination moments. This skill helps me innovate and approach problems from unique angles that others might miss.`,

            growth_areas: `The top 3 areas I'd like to grow in are:

1. Public Speaking and Presentation Skills - I want to become more effective at communicating complex technical concepts to diverse audiences, from engineers to non-technical stakeholders. Being able to inspire and educate through compelling presentations is crucial for leadership.

2. System Design at Scale - I'm fascinated by the architecture behind applications that serve millions of users. Understanding distributed systems, microservices, caching strategies, and how to build resilient, scalable infrastructure is something I'm actively learning.

3. Leadership and Mentoring - I want to develop my ability to lead high-performing teams, create psychological safety, and mentor junior developers. The best leaders elevate everyone around them, and that's the kind of impact I want to have.`,

            misconception: `A common misconception people have about me is that I'm introverted and prefer working alone because I can focus deeply on technical problems. 
While it's true that I enjoy deep focus time, I'm actually very collaborative and energized by brainstorming sessions and team problem-solving. 
Some of my best ideas come from bouncing thoughts off others and building on each other's perspectives. 
I believe the best solutions emerge from diverse teams working together, not from solo geniuses in isolation. 
So while I can work independently, I genuinely love the energy and creativity that comes from great teamwork.`,

            push_boundaries: `I push my boundaries by deliberately stepping into uncomfortable situations and embracing the learning that comes from struggle. 
I follow what I call the 70-20-10 rule: spending 70% of my time on things I'm already good at, 20% stretching my skills on challenges just beyond my current abilities, and 10% on completely new territory that feels almost impossible.

Practically, this means taking on projects outside my comfort zone, participating in hackathons where I have to learn new technologies under pressure, contributing to open source projects where I'm surrounded by developers more skilled than me, and actively seeking constructive feedback even when it's hard to hear.

I also believe in "productive failure"—trying things that might not work, because that's where the real growth happens. Every failed experiment teaches me something valuable about what doesn't work, bringing me closer to what does.`
        };

        let isListening = false;
        let recognition = null;

        // Initialize speech recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('userInput').value = transcript;
                sendMessage();
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                if (event.error === 'no-speech') {
                    setStatus('No speech detected. Please try again.');
                } else {
                    setStatus('Error: ' + event.error);
                }
                stopListening();
            };

            recognition.onend = () => {
                stopListening();
            };
        }

        // Initialize speech synthesis
        const synth = window.speechSynthesis;

        function toggleVoice() {
            if (isListening) {
                stopListening();
            } else {
                startListening();
            }
        }

        function startListening() {
            if (!recognition) {
                alert('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
                return;
            }

            isListening = true;
            document.getElementById('voiceBtn').classList.add('listening');
            document.getElementById('voiceBtn').textContent = '🔴';
            setStatus('🎤 Listening... Speak now!');
            
            try {
                recognition.start();
            } catch (error) {
                console.error('Error starting recognition:', error);
                stopListening();
            }
        }

        function stopListening() {
            isListening = false;
            document.getElementById('voiceBtn').classList.remove('listening');
            document.getElementById('voiceBtn').textContent = '🎤';
            setStatus('');
            if (recognition) {
                try {
                    recognition.stop();
                } catch (error) {
                    console.error('Error stopping recognition:', error);
                }
            }
        }

        function speak(text) {
            if (synth.speaking) {
                synth.cancel();
            }

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.95;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            
            // Try to use a good quality voice
            const voices = synth.getVoices();
            const preferredVoice = voices.find(voice => 
                voice.name.includes('Google') || 
                voice.name.includes('Microsoft') ||
                voice.lang.includes('en')
            );
            if (preferredVoice) {
                utterance.voice = preferredVoice;
            }

            synth.speak(utterance);
        }

        function getResponse(question) {
            const q = question.toLowerCase();

            if (q.includes('life story') || q.includes('about you') || q.includes('background') || 
                q.includes('tell me about yourself') || q.includes('who are you')) {
                return RESPONSES.life_story;
            }
            
            if (q.includes('superpower') || q.includes('best at') || q.includes('excel') || 
                q.includes('strength') || q.includes('good at') || q.includes('#1')) {
                return RESPONSES.superpower;
            }
            
            if (q.includes('grow') || q.includes('improve') || q.includes('develop') || 
                q.includes('learning') || q.includes('growth area')) {
                return RESPONSES.growth_areas;
            }
            
            if (q.includes('misconception') || q.includes('misunderstand') || q.includes('wrong about') || 
                q.includes('coworker')) {
                return RESPONSES.misconception;
            }
            
            if (q.includes('boundaries') || q.includes('limit') || q.includes('challenge') || 
                q.includes('comfort zone') || q.includes('push')) {
                return RESPONSES.push_boundaries;
            }

            return `That's an interesting question! I'm designed to answer specific questions about:
• My life story and background
• My #1 superpower
• The top 3 areas I'd like to grow in
• Misconceptions people have about me
• How I push my boundaries and limits

Feel free to click one of the suggestions above or ask me about any of these topics!`;
        }

        function askQuestion(question) {
            document.getElementById('userInput').value = question;
            sendMessage();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();

            if (!message) return;

            // Add user message to chat
            addMessage(message, 'user');
            input.value = '';

            // Show typing indicator
            showTyping();

            // Simulate thinking time for more natural interaction
            setTimeout(() => {
                hideTyping();
                const response = getResponse(message);
                addMessage(response, 'bot');
                speak(response);
            }, 800);
        }

        function showTyping() {
            const chatContainer = document.getElementById('chatContainer');
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot';
            typingDiv.id = 'typing-indicator';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'typing-indicator active';
            contentDiv.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
            
            typingDiv.appendChild(contentDiv);
            chatContainer.appendChild(typingDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function hideTyping() {
            const typing = document.getElementById('typing-indicator');
            if (typing) {
                typing.remove();
            }
        }

        function addMessage(text, sender) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = text;
            
            messageDiv.appendChild(contentDiv);
            chatContainer.appendChild(messageDiv);
            
            // Scroll to bottom smoothly
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function setStatus(text) {
            document.getElementById('status').textContent = text;
        }

        // Load voices when they're available
        if (synth.onvoiceschanged !== undefined) {
            synth.onvoiceschanged = () => {
                synth.getVoices();
            };
        }
    </script>
</body>
</html>"""

@app.route('/')
def home():
    """Render the voice bot interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/response', methods=['POST'])
def get_response():
    """API endpoint to get bot response"""
    data = request.json
    question = data.get('question', '').lower()
    
    RESPONSES = {
        'life_story': """I'm a software engineer passionate about building innovative solutions that make a real impact. 
I started coding in high school when I discovered the magic of turning ideas into reality through code. 
Since then, I've been on an incredible journey of continuous learning, working on everything from web applications to AI-powered tools. 
What drives me is the intersection of technology and human experience—creating solutions that are not just functional, but truly delightful to use.""",
        
        'superpower': """My #1 superpower is pattern recognition and connecting dots across different domains. 
I have this ability to quickly identify similarities between seemingly unrelated problems and apply creative solutions from one field to another. 
Whether it's recognizing a design pattern from architecture that could solve a coding challenge, or applying game theory to user experience design, 
I thrive on these cross-pollination moments. This skill helps me innovate and approach problems from unique angles that others might miss.""",
        
        'growth_areas': """The top 3 areas I'd like to grow in are:

1. Public Speaking and Presentation Skills - I want to become more effective at communicating complex technical concepts to diverse audiences, from engineers to non-technical stakeholders. Being able to inspire and educate through compelling presentations is crucial for leadership.

2. System Design at Scale - I'm fascinated by the architecture behind applications that serve millions of users. Understanding distributed systems, microservices, caching strategies, and how to build resilient, scalable infrastructure is something I'm actively learning.

3. Leadership and Mentoring - I want to develop my ability to lead high-performing teams, create psychological safety, and mentor junior developers. The best leaders elevate everyone around them, and that's the kind of impact I want to have.""",
        
        'misconception': """A common misconception people have about me is that I'm introverted and prefer working alone because I can focus deeply on technical problems. 
While it's true that I enjoy deep focus time, I'm actually very collaborative and energized by brainstorming sessions and team problem-solving. 
Some of my best ideas come from bouncing thoughts off others and building on each other's perspectives. 
I believe the best solutions emerge from diverse teams working together, not from solo geniuses in isolation. 
So while I can work independently, I genuinely love the energy and creativity that comes from great teamwork.""",
        
        'push_boundaries': """I push my boundaries by deliberately stepping into uncomfortable situations and embracing the learning that comes from struggle. 
I follow what I call the 70-20-10 rule: spending 70% of my time on things I'm already good at, 20% stretching my skills on challenges just beyond my current abilities, and 10% on completely new territory that feels almost impossible.

Practically, this means taking on projects outside my comfort zone, participating in hackathons where I have to learn new technologies under pressure, contributing to open source projects where I'm surrounded by developers more skilled than me, and actively seeking constructive feedback even when it's hard to hear.

I also believe in "productive failure"—trying things that might not work, because that's where the real growth happens. Every failed experiment teaches me something valuable about what doesn't work, bringing me closer to what does."""
    }
    
    if any(keyword in question for keyword in ['life story', 'about you', 'background', 'tell me about yourself', 'who are you']):
        response = RESPONSES['life_story']
    elif any(keyword in question for keyword in ['superpower', 'best at', 'excel', 'strength', 'good at', '#1']):
        response = RESPONSES['superpower']
    elif any(keyword in question for keyword in ['grow', 'improve', 'develop', 'learning', 'growth area']):
        response = RESPONSES['growth_areas']
    elif any(keyword in question for keyword in ['misconception', 'misunderstand', 'wrong about', 'coworker']):
        response = RESPONSES['misconception']
    elif any(keyword in question for keyword in ['boundaries', 'limit', 'challenge', 'comfort zone', 'push']):
        response = RESPONSES['push_boundaries']
    else:
        response = """That's an interesting question! I'm designed to answer specific questions about:
• My life story and background
• My #1 superpower
• The top 3 areas I'd like to grow in
• Misconceptions people have about me
• How I push my boundaries and limits

Feel free to click one of the suggestions above or ask me about any of these topics!"""
    
    return jsonify({'response': response})

def main():
    """Main entry point for the application"""
    print("=" * 60)
    print("🎤 Personal Voice Bot - Interactive Demo")
    print("=" * 60)
    print("\nStarting the application...")
    print("The application will be available at: http://127.0.0.1:5000")
    print("\nPress Ctrl+C to stop the application")
    print("-" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
