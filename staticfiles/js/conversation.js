document.addEventListener('DOMContentLoaded', function() {
    const conversationContainer = document.getElementById('messageContainer');
    const messageForm = document.getElementById('messageForm');
    const endConversationBtn = document.getElementById('endConversationBtn');
    const feedbackForm = document.getElementById('feedbackForm');
    
    // Scroll to bottom of messages
    if (conversationContainer) {
        conversationContainer.scrollTop = conversationContainer.scrollHeight;
    }
    
    // Handle message submission
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const messageContent = document.getElementById('messageContent');
            
            if (messageContent.value.trim() === '') return;
            
            // Disable form during submission
            const submitBtn = messageForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Sending...';
            
            // Get conversation ID from URL
            const conversationId = window.location.pathname.split('/').filter(Boolean).pop();
            
            // Send message to server
            fetch(`/api/conversations/${conversationId}/send_message/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    content: messageContent.value
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    // Append messages to conversation
                    appendMessage(data.user_message);
                    appendMessage(data.ai_message);
                    
                    // Clear input
                    messageContent.value = '';
                    
                    // Scroll to bottom
                    conversationContainer.scrollTop = conversationContainer.scrollHeight;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while sending your message');
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-send"></i> Send';
            });
        });
    }
    
    // Handle end conversation button
    if (endConversationBtn) {
        endConversationBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to end this conversation? You won\'t be able to send more messages.')) {
                const conversationId = window.location.pathname.split('/').filter(Boolean).pop();
                
                fetch(`/api/conversations/${conversationId}/end_conversation/`, 
                    {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        window.location.reload();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while ending the conversation');
                });
            }
        });
    }
    
    // Handle feedback submission
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(feedbackForm);
            const conversationId = window.location.pathname.split('/').filter(Boolean).pop();
            
            fetch(`/api/conversations/${conversationId}/provide_feedback/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    rating: formData.get('rating'),
                    helpful: formData.get('helpful'),
                    comments: formData.get('comments')
                })
            })
            .then(response => response.json())
            .then(data => {
                alert('Thank you for your feedback!');
                feedbackForm.reset();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while submitting your feedback');
            });
        });
    }
    
    // Helper function to append a message to the conversation
    function appendMessage(messageData) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${messageData.message_type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = messageData.content.replace(/\n/g, '<br>');
        
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        
        const timeSmall = document.createElement('small');
        timeSmall.className = 'text-muted';
        timeSmall.textContent = new Date(messageData.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        metaDiv.appendChild(timeSmall);
        
        if (messageData.flagged_content) {
            const flagSpan = document.createElement('span');
            flagSpan.className = 'text-danger ms-2';
            flagSpan.title = messageData.flag_reason;
            flagSpan.innerHTML = '<i class="bi bi-exclamation-triangle-fill"></i> Flagged';
            metaDiv.appendChild(flagSpan);
        }
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(metaDiv);
        
        conversationContainer.appendChild(messageDiv);
    }
});

// Get CSRF token (repeated from main.js for standalone functionality)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}