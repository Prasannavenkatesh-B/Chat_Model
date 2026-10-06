// ========================
// DOM References
// ========================
const chatForm       = document.getElementById('chatForm');
const chatInput      = document.getElementById('chatInput');
const chatMessages   = document.getElementById('chatMessages');
const resetBtn       = document.getElementById('resetBtn');
const themeToggleBtn = document.getElementById('themeToggleBtn');
const emptyState     = document.getElementById('emptyState');

// ========================
// State
// ========================
let messages = [];
let isGenerating = false;

// ========================
// Theme (Light default, Dark on toggle)
// ========================
if (localStorage.getItem('medcheck-theme') === 'dark') {
    document.body.classList.add('dark-theme');
}

themeToggleBtn.addEventListener('click', () => {
    document.body.classList.toggle('dark-theme');
    localStorage.setItem('medcheck-theme',
        document.body.classList.contains('dark-theme') ? 'dark' : 'light');
});

// ========================
// Reset
// ========================
resetBtn.addEventListener('click', () => {
    messages = [];
    chatMessages.innerHTML = '';
    emptyState.classList.remove('hidden');
    chatInput.value = '';
    chatInput.style.height = 'auto';
    chatInput.disabled = false;
    isGenerating = false;
});

// ========================
// Auto-grow textarea
// ========================
chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = chatInput.scrollHeight + 'px';
});

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

// ========================
// Form Submit
// ========================
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (isGenerating) return;

    const text = chatInput.value.trim();
    if (!text) return;

    chatInput.value = '';
    chatInput.style.height = 'auto';

    // Hide empty state on first message
    emptyState.classList.add('hidden');

    appendMessage('user', text, 'You (Counselor)');
    messages.push({ role: 'user', content: text });

    await getStudentReply();
});

// ========================
// Append Message
// ========================
function appendMessage(role, content, label) {
    const wrapper = document.createElement('div');
    wrapper.classList.add('message-wrapper', role);

    const lbl = document.createElement('div');
    lbl.classList.add('msg-label');
    lbl.textContent = label;

    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    bubble.innerHTML = formatContent(content);

    wrapper.appendChild(lbl);
    wrapper.appendChild(bubble);
    chatMessages.appendChild(wrapper);
    scrollToBottom();
}

// Format: style action descriptors like (Shifts uncomfortably)
function formatContent(text) {
    let safe = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Italicise bracketed actions
    safe = safe.replace(/(\([^)]+\)|\[[^\]]+\])/g,
        '<em style="color:var(--text-secondary);font-style:italic;">$1</em>');

    return safe.replace(/\n/g, '<br>');
}

// ========================
// Typing Indicator
// ========================
function showTyping() {
    if (document.getElementById('typingWrap')) return;
    const wrap = document.createElement('div');
    wrap.classList.add('message-wrapper', 'assistant');
    wrap.id = 'typingWrap';

    const lbl = document.createElement('div');
    lbl.classList.add('msg-label');
    lbl.textContent = 'Alex Miller';

    const bubble = document.createElement('div');
    bubble.classList.add('bubble');

    const ind = document.createElement('div');
    ind.classList.add('typing-indicator');
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('span');
        dot.classList.add('typing-dot');
        ind.appendChild(dot);
    }

    bubble.appendChild(ind);
    wrap.appendChild(lbl);
    wrap.appendChild(bubble);
    chatMessages.appendChild(wrap);
    scrollToBottom();
}

function hideTyping() {
    const el = document.getElementById('typingWrap');
    if (el) el.remove();
}

// ========================
// Ollama Streaming API Call
// ========================
async function getStudentReply() {
    isGenerating = true;
    chatInput.disabled = true;
    showTyping();

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: 'chat',
                messages: messages,
                stream: true
            })
        });

        if (!res.ok) {
            hideTyping();
            appendSystemMsg('⚠️ Server error. Make sure server.py is running.');
            return;
        }

        // Remove typing indicator and create the reply bubble
        hideTyping();
        emptyState.classList.add('hidden');

        // Create streaming bubble
        const wrapper = document.createElement('div');
        wrapper.classList.add('message-wrapper', 'assistant');

        const lbl = document.createElement('div');
        lbl.classList.add('msg-label');
        lbl.textContent = 'Alex Miller';

        const bubble = document.createElement('div');
        bubble.classList.add('bubble');
        bubble.innerHTML = '';

        wrapper.appendChild(lbl);
        wrapper.appendChild(bubble);
        chatMessages.appendChild(wrapper);
        scrollToBottom();

        // Read the SSE stream
        const reader = res.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let fullText = '';
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // keep incomplete line in buffer

            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed.startsWith('data:')) continue;

                try {
                    const json = JSON.parse(trimmed.slice(5).trim());
                    if (json.token) {
                        fullText += json.token;
                        bubble.innerHTML = formatContent(fullText);
                        scrollToBottom();
                    }
                    if (json.done) break;
                } catch (_) {
                    // skip malformed lines
                }
            }
        }

        // Save complete reply to history
        if (fullText.trim()) {
            messages.push({ role: 'assistant', content: fullText });
        }

    } catch (err) {
        hideTyping();
        appendSystemMsg('⚠️ Could not connect. Make sure server.py is running.');
        console.error(err);
    } finally {
        isGenerating = false;
        chatInput.disabled = false;
        chatInput.focus();
        scrollToBottom();
    }
}


// ========================
// System Note
// ========================
function appendSystemMsg(text) {
    const el = document.createElement('div');
    el.style.cssText = 'align-self:center;font-size:12px;color:var(--text-muted);font-style:italic;margin:8px 0;text-align:center;';
    el.textContent = text;
    chatMessages.appendChild(el);
    scrollToBottom();
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
