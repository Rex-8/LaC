const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

// Generate a unique session ID for this browser session
const sessionId = 'session_' + Date.now();
const userId = 1; // Default user ID

// Send message function
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');
    userInput.value = '';

    // Show typing indicator
    const typingDiv = addMessage('Thinking...', 'assistant');
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: userId,
                session_id: sessionId
            })
        });

        const data = await response.json();
        
        // Remove typing indicator
        typingDiv.remove();

        if (data.error) {
            addMessage('Error: ' + data.error, 'assistant');
        } else {
            // Add assistant's text response
            if (data.message) {
                addMessage(data.message, 'assistant');
            }
            
            // Add HTML content if present
            if (data.html) {
                addHTMLContent(data.html);
            }
        }
    } catch (error) {
        typingDiv.remove();
        addMessage('Error connecting to server: ' + error.message, 'assistant');
    }
}

// Add text message to chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageDiv;
}

// Add HTML content to chat
function addHTMLContent(html) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.style.maxWidth = '90%';
    contentDiv.innerHTML = html;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Add welcome message on load
window.addEventListener('load', () => {
    addMessage('Hi! I can help you shop. Try asking me to "show me products" or "show me red shoes"!', 'assistant');
});