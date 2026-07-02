// ZAIYAN Web Frontend — Made by Anonymous-beta for Zaiyan

const socket = io();

// State
let currentPage = 'dashboard';
let modules = [];
let sessions = [];
let currentModule = null;

// Navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const page = item.dataset.page;
        navigateTo(page);

        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        item.classList.add('active');
    });
});

function navigateTo(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(`page-${page}`).classList.add('active');
    currentPage = page;

    if (page === 'modules') loadModules();
    if (page === 'sessions') loadSessions();
}

// Socket.IO Events
socket.on('connect', () => {
    console.log('[ZAIYAN] Connected to framework');
    updateStatus(true);
});

socket.on('disconnect', () => {
    console.log('[ZAIYAN] Disconnected');
    updateStatus(false);
});

socket.on('status', (data) => {
    console.log('[ZAIYAN]', data.message);
});

socket.on('output', (data) => {
    appendTerminalOutput(data.message, 'info');
});

socket.on('complete', (data) => {
    appendTerminalOutput(`Complete: ${data.result}`, 'success');
});

socket.on('error', (data) => {
    appendTerminalOutput(`Error: ${data.message}`, 'error');
});

function updateStatus(online) {
    const dot = document.querySelector('.status-dot');
    const text = document.querySelector('.status-text');

    if (online) {
        dot.classList.add('online');
        dot.style.background = 'var(--success)';
        dot.style.boxShadow = '0 0 8px var(--success)';
        text.textContent = 'Framework Active';
    } else {
        dot.classList.remove('online');
        dot.style.background = 'var(--error)';
        dot.style.boxShadow = '0 0 8px var(--error)';
        text.textContent = 'Framework Offline';
    }
}

// Module Loading
async function loadModules() {
    try {
        const response = await fetch('/api/modules');
        const data = await response.json();
        modules = data.modules;

        document.getElementById('stat-modules').textContent = data.count;
        renderModules(modules);
    } catch (e) {
        console.error('Failed to load modules:', e);
    }
}

function renderModules(moduleList) {
    const grid = document.getElementById('modules-grid');
    grid.innerHTML = '';

    moduleList.forEach(mod => {
        const card = document.createElement('div');
        card.className = 'module-card';
        card.innerHTML = `
            <div class="module-card-header">
                <span class="module-name">${mod.name.split('/').pop()}</span>
                <span class="module-badge ${mod.type}">${mod.type}</span>
            </div>
            <p class="module-description">${mod.description || 'No description'}</p>
            <div class="module-meta">
                <span>${mod.platform.join(', ')}</span>
                <span>${mod.author}</span>
            </div>
        `;

        card.addEventListener('click', () => openModuleModal(mod.name));
        grid.appendChild(card);
    });
}

// Module Filtering
document.querySelectorAll('.filter-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        const filter = tab.dataset.filter;
        if (filter === 'all') {
            renderModules(modules);
        } else {
            renderModules(modules.filter(m => m.type === filter));
        }
    });
});

// Module Search
document.getElementById('module-search').addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = modules.filter(m =>
        m.name.toLowerCase().includes(query) ||
        m.description.toLowerCase().includes(query)
    );
    renderModules(filtered);
});

// Global Search
document.getElementById('global-search').addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    if (query.length < 2) return;

    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(r => r.json())
        .then(data => {
            if (currentPage !== 'modules') navigateTo('modules');
            renderModules(data.results);
        });
});

// Module Modal
async function openModuleModal(moduleName) {
    try {
        const response = await fetch(`/api/modules/${encodeURIComponent(moduleName)}`);
        const mod = await response.json();
        currentModule = mod;

        document.getElementById('modal-title').textContent = mod.name;
        document.getElementById('modal-description').textContent = mod.description || 'No description';
        document.getElementById('modal-type').textContent = mod.type;
        document.getElementById('modal-author').textContent = mod.author;
        document.getElementById('modal-platform').textContent = mod.platform.join(', ');

        // Build options form
        const optionsForm = document.getElementById('modal-options');
        optionsForm.innerHTML = '';

        if (mod.options) {
            Object.entries(mod.options).forEach(([key, config]) => {
                const group = document.createElement('div');
                group.className = 'form-group';

                const label = document.createElement('label');
                label.textContent = `${key} ${config.required ? '*' : ''}`;
                group.appendChild(label);

                const input = document.createElement('input');
                input.type = 'text';
                input.value = config.value || '';
                input.placeholder = config.description || '';
                input.dataset.option = key;
                group.appendChild(input);

                optionsForm.appendChild(group);
            });
        }

        document.getElementById('module-modal').classList.add('active');
    } catch (e) {
        console.error('Failed to load module details:', e);
    }
}

// Close Modal
document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', () => {
        document.getElementById('module-modal').classList.remove('active');
    });
});

document.getElementById('module-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
        e.target.classList.remove('active');
    }
});

// Execute Module
document.getElementById('modal-execute').addEventListener('click', async () => {
    if (!currentModule) return;

    const options = {};
    document.querySelectorAll('#modal-options input').forEach(input => {
        options[input.dataset.option] = input.value;
    });

    try {
        const response = await fetch(`/api/modules/${encodeURIComponent(currentModule.name)}/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ options })
        });

        const result = await response.json();

        if (result.success) {
            appendTerminalOutput(`[+] ${currentModule.name} executed successfully`, 'success');
            appendTerminalOutput(result.result, 'info');
        } else {
            appendTerminalOutput(`[-] Execution failed: ${result.error}`, 'error');
        }

        document.getElementById('module-modal').classList.remove('active');
    } catch (e) {
        appendTerminalOutput(`[-] Request failed: ${e.message}`, 'error');
    }
});

// Payload Generation
document.getElementById('generate-payload').addEventListener('click', async () => {
    const type = document.getElementById('payload-type').value;
    const arch = document.getElementById('payload-arch').value;
    const format = document.getElementById('payload-format').value;
    const lhost = document.getElementById('payload-lhost').value;
    const lport = document.getElementById('payload-lport').value;
    const evade = document.getElementById('payload-evade').checked;
    const evasionType = document.getElementById('evasion-type').value;

    const output = document.getElementById('payload-output');
    output.innerHTML = '<code class="placeholder">Generating payload...</code>';

    try {
        const response = await fetch('/api/payloads/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type, arch, format, lhost, lport,
                evade, evasion_type: evasionType
            })
        });

        const result = await response.json();

        if (result.success) {
            output.innerHTML = `<code>[+] Payload generated: ${result.file}
[+] Size: ${result.size} bytes
[+] Format: ${result.format}
[+] Architecture: ${arch}

[*] Start listener: nc -lvnp ${lport}
[*] Deliver payload to target</code>`;

            document.getElementById('stat-payloads').textContent =
                parseInt(document.getElementById('stat-payloads').textContent) + 1;
        } else {
            output.innerHTML = `<code class="error">[-] Generation failed: ${result.error}</code>`;
        }
    } catch (e) {
        output.innerHTML = `<code class="error">[-] Request failed: ${e.message}</code>`;
    }
});

// Evasion toggle
document.getElementById('payload-evade').addEventListener('change', (e) => {
    document.getElementById('evasion-options').style.display =
        e.target.checked ? 'block' : 'none';
});

// Copy output
document.getElementById('copy-output').addEventListener('click', () => {
    const text = document.getElementById('payload-output').textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copy-output');
        const original = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => btn.textContent = original, 1500);
    });
});

// Sessions
async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        const data = await response.json();
        sessions = data.sessions;

        document.getElementById('stat-sessions').textContent = sessions.length;
        renderSessions();
    } catch (e) {
        console.error('Failed to load sessions:', e);
    }
}

function renderSessions() {
    const tbody = document.getElementById('sessions-tbody');
    tbody.innerHTML = '';

    sessions.forEach(s => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="session-id">${s.id}</td>
            <td><span class="badge" style="background: rgba(5,217,232,0.15);color:var(--accent-tertiary)">${s.type}</span></td>
            <td>${s.target}</td>
            <td>${s.module}</td>
            <td>${new Date(s.created).toLocaleString()}</td>
            <td>${new Date(s.last_checkin).toLocaleString()}</td>
            <td><span class="badge" style="background: rgba(0,230,118,0.15);color:var(--success)">${s.active ? 'Active' : 'Dead'}</span></td>
            <td>
                <button class="btn btn-sm" onclick="interactSession('${s.id}')">Interact</button>
                <button class="btn btn-sm btn-secondary" onclick="killSession('${s.id}')">Kill</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function interactSession(id) {
    navigateTo('terminal');
    appendTerminalOutput(`[*] Interacting with session ${id}...`, 'info');
}

function killSession(id) {
    fetch(`/api/sessions/${id}/kill`, { method: 'POST' })
        .then(() => loadSessions());
}

// Terminal
const terminalInput = document.getElementById('terminal-input');
const terminalOutput = document.getElementById('terminal-output');

terminalInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        const cmd = terminalInput.value.trim();
        if (cmd) {
            appendTerminalOutput(cmd, 'command');
            executeTerminalCommand(cmd);
            terminalInput.value = '';
        }
    }
});

function appendTerminalOutput(text, type = 'info') {
    const line = document.createElement('div');
    line.className = 'terminal-line';

    const prompt = document.createElement('span');
    prompt.className = 'terminal-prompt';
    prompt.textContent = type === 'command' ? 'zaiyan >' : '      >';

    const content = document.createElement('span');
    content.className = 'terminal-text';

    if (type === 'error') {
        content.style.color = 'var(--error)';
    } else if (type === 'success') {
        content.style.color = 'var(--success)';
    } else if (type === 'command') {
        content.style.color = 'var(--accent-secondary)';
    }

    content.textContent = text;
    line.appendChild(prompt);
    line.appendChild(content);
    terminalOutput.appendChild(line);
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function executeTerminalCommand(cmd) {
    if (cmd === 'help') {
        appendTerminalOutput('Available commands:', 'info');
        appendTerminalOutput('  help        - Show this help', 'info');
        appendTerminalOutput('  modules     - List loaded modules', 'info');
        appendTerminalOutput('  sessions    - List active sessions', 'info');
        appendTerminalOutput('  payload     - Generate payload', 'info');
        appendTerminalOutput('  clear       - Clear terminal', 'info');
    } else if (cmd === 'clear') {
        terminalOutput.innerHTML = '';
    } else if (cmd === 'modules') {
        navigateTo('modules');
    } else if (cmd === 'sessions') {
        navigateTo('sessions');
    } else if (cmd === 'payload') {
        navigateTo('payloads');
    } else {
        // Send to backend via SocketIO
        socket.emit('execute', { module: 'console', command: cmd });
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadModules();
    loadSessions();

    // Simulate some initial stats
    document.getElementById('stat-targets').textContent = '3';
    document.getElementById('stat-payloads').textContent = '7';
});
