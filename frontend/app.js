// Configuration
const API_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000';

// State
let currentConversationId = null;
let ws = null;
let conversations = [];
let currentAssistantMessageDiv = null; // Ref al div del mensaje actual del asistente
let isNewAssistantTurn = true; // Rastrea si necesitamos un nuevo bloque de mensaje

// DOM Elements
const messagesContainer = document.getElementById('messagesContainer');
const messageForm = document.getElementById('messageForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const conversationsList = document.getElementById('conversationsList');
const newChatBtn = document.getElementById('newChatBtn');
const clearBtn = document.getElementById('clearBtn');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const chatTitle = document.getElementById('chatTitle');
const chatSubtitle = document.getElementById('chatSubtitle');
const toolIndicator = document.getElementById('toolIndicator');
const toolText = document.getElementById('toolText');
const modelInfo = document.getElementById('modelInfo');

// Vision Elements
const visionBtn = document.getElementById('visionBtn');
const visionModal = document.getElementById('visionModal');
const closeVisionModal = document.getElementById('closeVisionModal');
const closeVisionBtn = document.getElementById('closeVisionBtn');
const qrContainer = document.getElementById('qrContainer');
const visionUrl = document.getElementById('visionUrl');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    loadConversations();
    setupEventListeners();
    autoResizeTextarea();
});

// Load config
async function loadConfig() {
    try {
        const response = await fetch(`${API_URL}/api/config/`);
        const config = await response.json();
        modelInfo.textContent = `${config.llm_provider} ${config.model}`;

        // Set provider selector
        const providerSelect = document.getElementById('providerSelect');
        const modelSelect = document.getElementById('modelSelect');
        if (providerSelect) {
            providerSelect.value = config.llm_provider;

            // Sync models for this provider
            await updateModelSelector(config.llm_provider);

            // Select the current active model
            if (modelSelect) {
                modelSelect.value = config.model;
            }
        }

        // Set autonomy selector
        const autonomySelect = document.getElementById('autonomySelect');
        if (autonomySelect && config.autonomy_level) {
            autonomySelect.value = config.autonomy_level;
        }
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

// Load conversations
async function loadConversations() {
    try {
        const response = await fetch(`${API_URL}/api/conversations/`);


        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        conversations = data.conversations || [];
        renderConversations();

        // Update status
        statusDot.className = 'status-dot connected';
        statusText.textContent = 'Conectado';

    } catch (error) {
        console.error('Error loading conversations:', error);
        conversationsList.innerHTML = `
            <div class="loading" style="color: #ef4444;">
                Error: ${error.message}<br>
                <small>¿Está el backend corriendo en puerto 8000?</small>
            </div>
        `;
        statusDot.className = 'status-dot error';
        statusText.textContent = 'Error de conexión';
    }
}

// Render conversations
function renderConversations() {
    if (!conversations || conversations.length === 0) {
        conversationsList.innerHTML = `
            <div class="loading">
                No hay conversaciones<br>
                <small>Crea una nueva para comenzar</small>
            </div>
        `;
        return;
    }

    conversationsList.innerHTML = conversations.map(conv => `
        <div class="conversation-item ${conv.id === currentConversationId ? 'active' : ''}" 
             data-id="${conv.id}">
            <div class="conversation-info">
                <div class="conversation-title">${conv.title || conv.id}</div>
                <div class="conversation-meta">
                    <span>${conv.message_count} mensajes</span>
                    <span>${formatDate(conv.updated_at)}</span>
                </div>
            </div>
            <button class="btn-delete-conv" title="Eliminar conversación" data-id="${conv.id}">×</button>
        </div>
    `).join('');

    // Event delegation for the whole list
    conversationsList.onclick = (e) => {
        const deleteBtn = e.target.closest('.btn-delete-conv');
        const item = e.target.closest('.conversation-item');

        if (deleteBtn) {
            e.stopPropagation();
            deleteConversation(deleteBtn.dataset.id);
            return;
        }

        if (item) {
            loadConversation(item.dataset.id);
        }
    };
}

// Delete conversation
async function deleteConversation(conversationId) {
    if (!confirm('¿Estás seguro de que quieres eliminar esta conversación?')) return;

    try {
        const response = await fetch(`${API_URL}/api/conversations/${conversationId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            if (currentConversationId === conversationId) {
                newChat();
            }
            loadConversations();
        } else {
            const data = await response.json();
            alert(`Error: ${data.detail || 'No se pudo eliminar la conversación'}`);
        }
    } catch (error) {
        console.error('Error deleting conversation:', error);
        alert('Error conectando con el servidor');
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) return 'Ahora';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`;
    return `${Math.floor(diff / 86400000)}d`;
}

// Load conversation
async function loadConversation(conversationId) {
    try {
        const response = await fetch(`${API_URL}/api/chat/${conversationId}/history`);

        if (!response.ok) {
            console.error('Failed to load conversation:', response.status);
            return;
        }

        const data = await response.json();

        currentConversationId = conversationId;
        chatTitle.textContent = conversationId;
        chatSubtitle.textContent = `${data.total || 0} mensajes`;

        // Clear messages
        messagesContainer.innerHTML = '';

        // Render messages - check if messages array exists
        if (data.messages && Array.isArray(data.messages)) {
            data.messages.forEach(msg => {
                addMessage(msg.role, msg.content);
            });
        } else {
            console.warn('No messages array in response:', data);
        }

        // Update UI
        renderConversations();
        connectWebSocket();

    } catch (error) {
        console.error('Error loading conversation:', error);
        addMessage('assistant', `❌ Error cargando conversación: ${error.message}`);
    }
}

// New chat
function newChat() {
    currentConversationId = `conv_${Date.now()}`;
    chatTitle.textContent = 'Nueva Conversación';
    chatSubtitle.textContent = 'Escribe un mensaje para comenzar';
    messagesContainer.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">🤖</div>
            <h3>¡Hola! Soy tu Agente Autónomo</h3>
            <p>Puedo ayudarte con:</p>
            <ul>
                <li>📁 Gestión de archivos y directorios</li>
                <li>⚙️ Ejecución de comandos</li>
                <li>🔧 Operaciones Git</li>
                <li>💬 Y mucho más...</li>
            </ul>
            <p class="welcome-hint">Escribe un mensaje para comenzar</p>
        </div>
    `;
    renderConversations();
    connectWebSocket();
}

// Connect WebSocket
function connectWebSocket() {
    // Close existing connection
    if (ws) {
        ws.close();
        ws = null;
    }

    if (!currentConversationId) {
        statusDot.className = 'status-dot';
        statusText.textContent = 'Sin conversación';
        return;
    }

    try {
        statusDot.className = 'status-dot';
        statusText.textContent = 'Conectando...';

        ws = new WebSocket(`${WS_URL}/ws/chat/${currentConversationId}`);

        // Timeout de 5 segundos
        const timeout = setTimeout(() => {
            if (ws && ws.readyState !== WebSocket.OPEN) {
                console.warn('WebSocket timeout');
                ws.close();
                statusDot.className = 'status-dot error';
                statusText.textContent = 'WebSocket timeout';
            }
        }, 5000);

        ws.onopen = () => {
            clearTimeout(timeout);
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'WebSocket conectado';
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };

        ws.onerror = (error) => {
            clearTimeout(timeout);
            console.error('WebSocket error:', error);
            statusDot.className = 'status-dot error';
            statusText.textContent = 'WebSocket error';
        };

        ws.onclose = () => {
            clearTimeout(timeout);
            statusDot.className = 'status-dot';
            statusText.textContent = 'Desconectado';
        };

    } catch (error) {
        console.error('Error creating WebSocket:', error);
        statusDot.className = 'status-dot error';
        statusText.textContent = 'Error WebSocket';
    }
}

// Handle WebSocket message
function handleWebSocketMessage(data) {
    const { type } = data;

    switch (type) {
        case 'connected':
            console.log('WebSocket connected');
            break;

        case 'thinking':
            showThinking(data.message, data.content);
            break;

        case 'tool_call':
            showToolExecution(data.tool, data.arguments);
            break;

        case 'approval_required':
            showApprovalRequest(data);
            break;

        case 'tool_result':
            showToolResult(data);
            break;

        case 'message_chunk':
            appendToLastMessage(data.content);
            break;

        case 'done':
            hideThinking();
            hideToolIndicator();
            // Re-enable controls after processing is done
            sendBtn.disabled = false;
            messageInput.disabled = false;
            messageInput.focus();
            break;

        case 'error':
            hideThinking();
            hideToolIndicator();
            const errorMsg = data.error || data.message || 'Error desconocido';
            addMessage('assistant', `❌ Error: ${errorMsg}`);
            // Re-enable controls on error
            sendBtn.disabled = false;
            messageInput.disabled = false;
            messageInput.focus();
            break;

        default:
            console.log('Unknown message type:', type);
    }
}

// Show thinking indicator
function showThinking(message = "Pensando", content = "") {
    let thinkingDiv = document.querySelector('.thinking');

    // Check if we need to create a new assistant message block
    if (isNewAssistantTurn || !currentAssistantMessageDiv) {
        currentAssistantMessageDiv = document.createElement('div');
        currentAssistantMessageDiv.className = 'message assistant';

        currentAssistantMessageDiv.innerHTML = `
            <div class="message-header">
                <div class="message-avatar">🤖</div>
                <span class="message-role">Agente</span>
            </div>
            <div class="message-content">
                <div class="message-text"></div>
            </div>
        `;
        messagesContainer.appendChild(currentAssistantMessageDiv);
        isNewAssistantTurn = false;
    }

    const contentDiv = currentAssistantMessageDiv.querySelector('.message-content');

    // If there is reasoning content, add it as a "thought" block
    if (content) {
        const thoughtDiv = document.createElement('div');
        thoughtDiv.className = 'thought-block';
        thoughtDiv.innerHTML = `
            <details open>
                <summary>🧠 Razonamiento Interno</summary>
                <div class="thought-text">${escapeHtml(content)}</div>
            </details>
        `;
        contentDiv.appendChild(thoughtDiv);
    }

    // Refresh or create the active thinking indicator
    if (!thinkingDiv) {
        thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'thinking';
        thinkingDiv.innerHTML = `
            <span>${escapeHtml(message)}</span>
            <div class="thinking-dots">
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
            </div>
        `;
        contentDiv.appendChild(thinkingDiv);
    } else {
        thinkingDiv.querySelector('span').textContent = escapeHtml(message);
    }

    scrollToBottom();
}

// Hide thinking indicator
function hideThinking() {
    const thinking = document.querySelector('.thinking');
    if (thinking) {
        thinking.remove();
    }
}

// Show approval indicator
function showApprovalRequest(data) {
    if (!currentAssistantMessageDiv) {
        addMessage('assistant', '');
    }

    const contentDiv = currentAssistantMessageDiv.querySelector('.message-content');

    const approvalDiv = document.createElement('div');
    approvalDiv.className = 'approval-request';
    approvalDiv.innerHTML = `
        <div class="approval-header">🛡️ Permiso Requerido</div>
        <div class="approval-message">${escapeHtml(data.message)}</div>
        <div class="approval-details">
            <strong>Herramienta:</strong> <code>${escapeHtml(data.tool)}</code><br>
            <strong>Argumentos:</strong> <pre><code>${escapeHtml(JSON.stringify(data.arguments, null, 2))}</code></pre>
        </div>
        <div class="approval-actions">
            <button class="btn-confirm btn-approve" id="approveBtn">✅ Aprobar Ejecución</button>
            <button class="btn-confirm btn-reject" id="rejectBtn">❌ Rechazar</button>
        </div>
    `;

    contentDiv.appendChild(approvalDiv);

    approvalDiv.querySelector('#approveBtn').onclick = () => {
        sendApprovalResponse(true);
        approvalDiv.innerHTML = '<div class="approval-status approved">✅ Acción aprobada. Continuando...</div>';
    };

    approvalDiv.querySelector('#rejectBtn').onclick = () => {
        sendApprovalResponse(false);
        approvalDiv.innerHTML = '<div class="approval-status rejected">❌ Acción rechazada.</div>';
    };

    scrollToBottom();
}

function sendApprovalResponse(approved) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'approval_response',
            approved: approved
        }));

        // Mostrar indicador de que el agente vuelve a pensar
        showThinking("Procesando tu respuesta...", "");
    }
}

// Show tool execution
function showToolExecution(dataTool, dataArgs) {
    const toolName = dataTool;
    const args = dataArgs || {};

    toolIndicator.style.display = 'flex';
    toolText.textContent = `Ejecutando: ${toolName || 'herramienta'}`;

    if (isNewAssistantTurn || !currentAssistantMessageDiv) {
        addMessage('assistant', '');
        isNewAssistantTurn = false;
    }

    const contentDiv = currentAssistantMessageDiv.querySelector('.message-content');

    // Detectar si parece un comando
    const command = args.command || args.CommandLine || (args.parameters && args.parameters.command);

    if (toolName === 'execute_command' || command) {
        const cmd = command || 'unknown';

        // Intentar reutilizar el último terminal en este mensaje
        let terminalDiv = currentAssistantMessageDiv.querySelector('.terminal-container');
        let terminalId;

        if (terminalDiv) {
            terminalId = terminalDiv.id;
            const terminalContent = terminalDiv.querySelector('.terminal-content');

            // Agregar línea de comando al terminal existente
            const newCmdLine = document.createElement('div');
            newCmdLine.className = 'terminal-line';
            newCmdLine.innerHTML = `
                <span class="terminal-prompt">user@autonomo:~$</span>
                <span class="terminal-command">${escapeHtml(cmd)}</span>
                <span class="terminal-cursor"></span>
                <div class="terminal-output"><span class="terminal-loading">Ejecutando...</span></div>
            `;
            terminalContent.appendChild(newCmdLine);

            // El cursor anterior debería removerse (esto se maneja en showToolResult, pero por si acaso)
            const oldCursors = terminalContent.querySelectorAll('.terminal-cursor');
            if (oldCursors.length > 1) {
                oldCursors[0].remove();
            }
        } else {
            terminalId = `terminal-${Date.now()}`;
            terminalDiv = document.createElement('div');
            terminalDiv.className = 'terminal-container';
            terminalDiv.id = terminalId;
            terminalDiv.innerHTML = `
                <div class="terminal-header">
                    <div class="terminal-dot red"></div>
                    <div class="terminal-dot yellow"></div>
                    <div class="terminal-dot green"></div>
                    <div class="terminal-title">${escapeHtml(toolName)}</div>
                </div>
                <div class="terminal-content">
                    <div class="terminal-line">
                        <span class="terminal-prompt">user@autonomo:~$</span>
                        <span class="terminal-command">${escapeHtml(cmd)}</span>
                        <span class="terminal-cursor"></span>
                        <div class="terminal-output"><span class="terminal-loading">Ejecutando...</span></div>
                    </div>
                </div>
            `;
            contentDiv.appendChild(terminalDiv);
        }

        currentAssistantMessageDiv.dataset.currentTerminal = terminalId;
    } else {
        // Compactar otros tools
        const toolDiv = document.createElement('div');
        toolDiv.className = 'tool-execution-compact';
        toolDiv.innerHTML = `
            <div class="tool-header-compact">
                <span class="tool-icon">🔧</span>
                <span class="tool-name">${escapeHtml(toolName)}</span>
                <span class="tool-summary">${escapeHtml(JSON.stringify(args).substring(0, 100))}${JSON.stringify(args).length > 100 ? '...' : ''}</span>
            </div>
        `;
        contentDiv.appendChild(toolDiv);
    }

    scrollToBottom();
}

// Show tool result (output)
function showToolResult(data) {
    if (!currentAssistantMessageDiv) return;

    hideThinking();
    hideToolIndicator();

    const terminalId = currentAssistantMessageDiv.dataset.currentTerminal;
    const contentDiv = currentAssistantMessageDiv.querySelector('.message-content');

    // Update Sidebar Status based on tool results
    updateSidebarStatus(data);

    if (terminalId) {
        // ... (terminal logic remains same)
        const terminal = document.getElementById(terminalId);
        if (terminal) {
            const outputs = terminal.querySelectorAll('.terminal-output');
            const outputDiv = outputs[outputs.length - 1];
            const cursors = terminal.querySelectorAll('.terminal-cursor');
            cursors.forEach(c => c.remove());

            let resultText = '';
            if (data.success) {
                const res = data.result;
                if (res && typeof res === 'object') {
                    if (res.stdout !== undefined || res.stderr !== undefined) {
                        resultText = res.stdout || '';
                        if (res.stderr) resultText += `\nError:\n${res.stderr}`;
                    } else {
                        resultText = JSON.stringify(res, null, 2);
                    }
                } else {
                    resultText = typeof res === 'string' ? res : JSON.stringify(res, null, 2);
                }
            } else {
                resultText = `Error: ${data.error || 'Unknown error'}`;
            }
            if (outputDiv) outputDiv.textContent = resultText;
            scrollToBottom();
            return;
        }
    }

    // Special handling for Infrastructure Analysis or Data Queries
    if (data.tool === 'analyze_cloud_resources' && data.success) {
        const reportDiv = createAnalysisReport(data.result);
        contentDiv.appendChild(reportDiv);
        scrollToBottom();
        return;
    }

    if (data.tool === 'dremio_query' && data.success) {
        const tableDiv = createDremioResultsTable(data.result);
        contentDiv.appendChild(tableDiv);
        scrollToBottom();
        return;
    }

    if (data.tool === 'nagios_get_alerts' && data.success) {
        const reportDiv = createNagiosReport(data.result);
        contentDiv.appendChild(reportDiv);
        scrollToBottom();
        return;
    }

    // Fallback if not a terminal tool or specialized tool
    const resultDiv = document.createElement('div');
    resultDiv.className = `tool-result ${data.success ? 'success' : 'error'}`;

    let content = '';
    if (data.success) {
        content = typeof data.result === 'string' ? data.result : JSON.stringify(data.result, null, 2);
    } else {
        content = data.error || 'Error desconocido';
    }

    resultDiv.innerHTML = `
        <div class="result-header">
            <span>${data.success ? '📊 Resultado de' : '❌ Error en'} ${data.tool || 'herramienta'}</span>
        </div>
        <pre class="result-content"><code>${escapeHtml(content.substring(0, 500))}${content.length > 500 ? '...' : ''}</code></pre>
        ${content.length > 500 ? `<div class="btn-view-result" id="viewFullResult">🔍 Ver resultado completo en detalle</div>` : ''}
    `;

    if (content.length > 500) {
        resultDiv.querySelector('#viewFullResult').onclick = () => {
            openResultModal(`Resultado: ${data.tool || 'Herramienta'}`, content);
        };
    }

    contentDiv.appendChild(resultDiv);
    scrollToBottom();
}

// Helper to update sidebar status indicators
function updateSidebarStatus(data) {
    if (!data.success) return;

    if (data.tool === 'zabbix_get_alerts') {
        const zabbixVal = document.querySelector('#statusZabbix .status-value');
        if (zabbixVal) {
            const count = data.result.count || 0;
            zabbixVal.textContent = count > 0 ? `${count} Alertas` : 'OK';
            zabbixVal.style.color = count > 0 ? 'var(--danger)' : 'var(--success)';
        }
    } else if (data.tool === 'nagios_get_alerts') {
        const nagiosVal = document.querySelector('#statusNagios .status-value');
        if (nagiosVal) {
            const count = data.result.count || 0;
            nagiosVal.textContent = count > 0 ? `${count} Alertas` : 'OK';
            nagiosVal.style.color = count > 0 ? 'var(--danger)' : 'var(--success)';
        }
    } else if (data.tool === 'checkmk_get_alerts') {
        const checkVal = document.querySelector('#statusCheckmk .status-value');
        if (checkVal) {
            const count = data.result.count || 0;
            checkVal.textContent = count > 0 ? `${count} Alertas` : 'OK';
            checkVal.style.color = count > 0 ? 'var(--danger)' : 'var(--success)';
        }
    } else if (data.tool === 'oci_list_instances') {
        const ociVal = document.querySelector('#statusOCI .status-value');
        if (ociVal) ociVal.textContent = 'CONECTADO';
    } else if (data.tool === 'aws_list_instances' || (data.tool === 'execute_command' && (data.arguments.command || '').includes('aws'))) {
        const awsVal = document.querySelector('#statusAWS .status-value');
        if (awsVal) awsVal.textContent = 'ACTIVO';
    } else if (data.tool === 'dremio_query' || data.tool === 'dremio_list_catalog') {
        const dremioVal = document.querySelector('#statusDremio .status-value');
        if (dremioVal) dremioVal.textContent = 'CONECTADO';
    }
}

// Create Visual Analysis Report
function createAnalysisReport(res) {
    const div = document.createElement('div');
    div.className = 'analysis-report';

    const recommendations = res.recommendations || [];
    const summary = res.summary || {};

    let rowsHtml = recommendations.map(rec => `
        <tr>
            <td>${escapeHtml(rec.resource_id)}</td>
            <td>${escapeHtml(rec.issue)}</td>
            <td>${escapeHtml(rec.recommendation)}</td>
            <td><span class="severity-${rec.severity}">${escapeHtml(rec.severity)}</span></td>
        </tr>
    `).join('');

    if (recommendations.length === 0) {
        rowsHtml = '<tr><td colspan="4" style="text-align:center; padding: 20px;">Súper! No se encontraron problemas de optimización.</td></tr>';
    }

    div.innerHTML = `
        <div class="analysis-header">
            <span class="analysis-title">📊 Reporte de Optimización (${res.provider.toUpperCase()})</span>
            <div class="analysis-summary">
                <div class="summary-stat">
                    <span class="summary-value">${summary.total_resources || 0}</span>
                    <span class="summary-label">Recursos</span>
                </div>
                <div class="summary-stat" style="color: ${summary.optimizable > 0 ? 'var(--warning)' : 'var(--success)'}">
                    <span class="summary-value">${summary.optimizable || 0}</span>
                    <span class="summary-label">Optimizables</span>
                </div>
            </div>
        </div>
        <table class="analysis-table">
            <thead>
                <tr>
                    <th>Recurso</th>
                    <th>Hallazgo</th>
                    <th>Recomendación</th>
                    <th>Prioridad</th>
                </tr>
            </thead>
            <tbody>
                ${rowsHtml}
            </tbody>
        </table>
    `;
    return div;
}

// Create Nagios Alerts Report
function createNagiosReport(res) {
    const div = document.createElement('div');
    div.className = 'analysis-report nagios-report';

    const summary = res.summary || {};
    const problems = res.problems || [];

    let rowsHtml = problems.map(prob => {
        const statusClass = prob.status === 2 ? 'severity-High' : (prob.status === 1 ? 'severity-Medium' : 'severity-Low');
        const statusText = prob.status === 2 ? 'CRITICAL' : (prob.status === 1 ? 'WARNING' : 'UNKNOWN');
        return `
            <tr>
                <td>${escapeHtml(prob.host)}</td>
                <td>${escapeHtml(prob.service)}</td>
                <td><span class="${statusClass}">${statusText}</span></td>
                <td><small>${escapeHtml(prob.output)}</small></td>
            </tr>
        `;
    }).join('');

    if (problems.length === 0) {
        rowsHtml = '<tr><td colspan="4" style="text-align:center; padding: 20px;">✅ Todos los servicios están en estado OK.</td></tr>';
    }

    div.innerHTML = `
        <div class="analysis-header">
            <span class="analysis-title">🔍 Alertado de Nagios</span>
            <div class="analysis-summary">
                <div class="summary-stat">
                    <span class="summary-value">${summary.ok || 0}</span>
                    <span class="summary-label">OK</span>
                </div>
                <div class="summary-stat" style="color: var(--warning)">
                    <span class="summary-value">${summary.warning || 0}</span>
                    <span class="summary-label">Warn</span>
                </div>
                <div class="summary-stat" style="color: var(--danger)">
                    <span class="summary-value">${summary.critical || 0}</span>
                    <span class="summary-label">Crit</span>
                </div>
            </div>
        </div>
        <table class="analysis-table">
            <thead>
                <tr>
                    <th>Host</th>
                    <th>Servicio</th>
                    <th>Estado</th>
                    <th>Información</th>
                </tr>
            </thead>
            <tbody>
                ${rowsHtml}
            </tbody>
        </table>
    `;
    return div;
}

// Create Dremio Results Table
function createDremioResultsTable(res) {
    const div = document.createElement('div');
    div.className = 'analysis-report dremio-results';

    const rows = res.data || [];
    if (rows.length === 0) {
        div.innerHTML = '<div class="analysis-header"><span class="analysis-title">📊 Dremio: Sin resultados</span></div>';
        return div;
    }

    const headers = Object.keys(rows[0]);
    const headerHtml = headers.map(h => `<th>${escapeHtml(h)}</th>`).join('');
    const rowsHtml = rows.map(row => `
        <tr>
            ${headers.map(h => `<td>${escapeHtml(String(row[h]))}</td>`).join('')}
        </tr>
    `).join('');

    div.innerHTML = `
        <div class="analysis-header">
            <span class="analysis-title">📊 Resultados Dremio (Job: ${res.job_id.substring(0, 8)}...)</span>
        </div>
        <div style="overflow-x: auto;">
            <table class="analysis-table">
                <thead><tr>${headerHtml}</tr></thead>
                <tbody>${rowsHtml}</tbody>
            </table>
        </div>
    `;
    return div;
}


// Global modal handlers
function openResultModal(title, content) {
    const modal = document.getElementById('resultModal');
    const titleEl = document.getElementById('resultModalTitle');
    const codeEl = document.getElementById('resultModalCode');

    titleEl.textContent = title;
    codeEl.textContent = content;
    modal.style.display = 'block';
}

function closeResultModal() {
    document.getElementById('resultModal').style.display = 'none';
}

// Copy result to clipboard
function copyResultToClipboard() {
    const content = document.getElementById('resultModalCode').textContent;
    navigator.clipboard.writeText(content).then(() => {
        const btn = document.getElementById('copyResultBtn');
        const originalText = btn.textContent;
        btn.textContent = '✅ ¡Copiado!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    });
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Hide tool indicator
function hideToolIndicator() {
    toolIndicator.style.display = 'none';
}

// Add message
function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = role === 'user' ? '👤' : '🤖';
    const roleName = role === 'user' ? 'Tú' : 'Agente';

    messageDiv.innerHTML = `
        <div class="message-header">
            <div class="message-avatar">${avatar}</div>
            <span class="message-role">${roleName}</span>
        </div>
        <div class="message-content">
            <div class="message-text">${formatMessage(content)}</div>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);

    // Update current assistant message reference
    if (role === 'assistant') {
        currentAssistantMessageDiv = messageDiv;
    }

    scrollToBottom();
}

// Append to last message (for streaming)
function appendToLastMessage(content) {
    // If we don't have a current assistant message or it's a new turn, create one
    if (isNewAssistantTurn || !currentAssistantMessageDiv) {
        addMessage('assistant', content);
        isNewAssistantTurn = false;
        return;
    }

    const textDiv = currentAssistantMessageDiv.querySelector('.message-text');
    const contentDiv = currentAssistantMessageDiv.querySelector('.message-content');

    if (textDiv) {
        // Remove thinking if it exists before appending
        const thinking = contentDiv.querySelector('.thinking');
        if (thinking) thinking.remove();

        const currentText = textDiv.innerText || '';
        const newText = currentText.trim() ? currentText + content : content;
        textDiv.innerHTML = formatMessage(newText);
        scrollToBottom();
    }
}

// Format message (simple markdown-like)
function formatMessage(text) {
    // Code blocks
    text = text.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
    // Inline code
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    // Line breaks
    text = text.replace(/\n/g, '<br>');
    return text;
}

// Scroll to bottom
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Send message
async function sendMessage(message) {
    if (!message.trim()) return;

    // Add user message
    addMessage('user', message);

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // Disable input
    sendBtn.disabled = true;
    messageInput.disabled = true;

    // Set turn state
    isNewAssistantTurn = true;
    currentAssistantMessageDiv = null;

    try {
        if (ws && ws.readyState === WebSocket.OPEN) {
            // Send via WebSocket
            ws.send(JSON.stringify({ message }));
            // Don't re-enable here - wait for 'done' event from WebSocket
        } else {
            // Fallback to REST API
            const response = await fetch(`${API_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message,
                    conversation_id: currentConversationId
                })
            });

            const data = await response.json();
            addMessage('assistant', data.message);

            if (data.tool_calls) {
                data.tool_calls.forEach(tc => {
                    showToolExecution(tc.name, tc.arguments);
                });
            }

            // Refresh conversations list to show new conversation
            setTimeout(() => loadConversations(), 1000);

            // Re-enable controls for REST fallback
            sendBtn.disabled = false;
            messageInput.disabled = false;
            messageInput.focus();
        }
    } catch (error) {
        console.error('Error sending message:', error);
        addMessage('assistant', 'Error al enviar mensaje. Por favor, intenta de nuevo.');
        // Re-enable on error
        sendBtn.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
    }
}

function setupEventListeners() {
    messageForm.addEventListener('submit', (e) => {
        e.preventDefault();
        sendMessage(messageInput.value);
    });

    newChatBtn.addEventListener('click', newChat);

    clearBtn.addEventListener('click', () => {
        if (confirm('¿Limpiar esta conversación?')) {
            messagesContainer.innerHTML = '';
            newChat();
        }
    });

    // Event Listeners para Visión
    if (visionBtn) {
        visionBtn.addEventListener('click', openVisionModal);
    }
    if (closeVisionModal) {
        closeVisionModal.addEventListener('click', () => visionModal.style.display = 'none');
    }
    if (closeVisionBtn) {
        closeVisionBtn.addEventListener('click', () => visionModal.style.display = 'none');
    }

    // Enter to send, Shift+Enter for new line
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            messageForm.dispatchEvent(new Event('submit'));
        }
    });

    // Event Listeners para el Modal de Resultados
    const closeResultModalBtn = document.getElementById('closeResultModal');
    const closeResultBtn = document.getElementById('closeResultBtn');
    const copyResultBtn = document.getElementById('copyResultBtn');
    const resultModal = document.getElementById('resultModal');

    if (closeResultModalBtn) closeResultModalBtn.addEventListener('click', closeResultModal);
    if (closeResultBtn) closeResultBtn.addEventListener('click', closeResultModal);
    if (copyResultBtn) copyResultBtn.addEventListener('click', copyResultToClipboard);

    if (resultModal) {
        resultModal.addEventListener('click', (e) => {
            if (e.target === resultModal) closeResultModal();
        });
    }
}

// Auto-resize textarea
function autoResizeTextarea() {
    messageInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 200) + 'px';
    });
}

async function openVisionModal() {
    visionModal.style.display = 'flex';
    qrContainer.innerHTML = '<div class="loading">Generando código QR...</div>';
    visionUrl.textContent = 'Cargando...';

    try {
        const response = await fetch(`${API_URL}/api/vision/connection-info`);
        const data = await response.json();

        qrContainer.innerHTML = `<img src="${data.qr_url}" alt="QR Code" width="200" height="200">`;
        visionUrl.textContent = data.url;
    } catch (err) {
        console.error("Error al obtener info de conexión:", err);
        qrContainer.innerHTML = '<div class="error">Error al conectar con el servidor</div>';
    }
}

// Start with new chat
newChat();

// Provider selector change handler
const providerSelect = document.getElementById('providerSelect');
if (providerSelect) {
    providerSelect.addEventListener('change', async (e) => {
        const newProvider = e.target.value;

        // Update model selector options for new provider
        updateModelSelector(newProvider);

        try {
            const response = await fetch(`${API_URL}/api/config/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ llm_provider: newProvider })
            });

            if (response.ok) {
                await loadConfig();
                addMessage('system', `✅ Provider cambiado a ${newProvider}`);
            } else {
                throw new Error('Error en la respuesta');
            }
        } catch (error) {
            console.error('Error changing provider:', error);
            addMessage('system', `❌ Error cambiando provider: ${error.message}`);
            // Revert selector
            await loadConfig();
        }
    });
}

// Autonomy selector change handler
const autonomySelect = document.getElementById('autonomySelect');
if (autonomySelect) {
    autonomySelect.addEventListener('change', async (e) => {
        const newLevel = e.target.value;
        console.log('Cambiando nivel de autonomía a:', newLevel);

        try {
            const response = await fetch(`${API_URL}/api/config/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ autonomy_level: newLevel })
            });

            if (response.ok) {
                addMessage('system', `⚙️ Modo de Autonomía: ${newLevel === 'full' ? 'Total (Sin permisos)' : 'Semi (Pide permiso)'}`);
            } else {
                throw new Error('Error en la respuesta');
            }
        } catch (error) {
            console.error('Error changing autonomy level:', error);
            addMessage('system', `❌ Error al cambiar nivel de autonomía: ${error.message}`);
            await loadConfig();
        }
    });
}

// API Key Modal Handlers
const apiKeyModal = document.getElementById('apiKeyModal');
const apiKeyBtn = document.getElementById('apiKeyBtn');
const closeModal = document.getElementById('closeModal');
const cancelModal = document.getElementById('cancelModal');
const saveApiKeys = document.getElementById('saveApiKeys');

// Load saved API keys from localStorage
function loadApiKeys() {
    document.getElementById('openaiKey').value = localStorage.getItem('openai_api_key') || '';
    document.getElementById('anthropicKey').value = localStorage.getItem('anthropic_api_key') || '';
    document.getElementById('deepseekKey').value = localStorage.getItem('deepseek_api_key') || '';
}

// Open modal
apiKeyBtn.addEventListener('click', () => {
    loadApiKeys();
    apiKeyModal.style.display = 'flex';
});

// Close modal
closeModal.addEventListener('click', () => {
    apiKeyModal.style.display = 'none';
});

cancelModal.addEventListener('click', () => {
    apiKeyModal.style.display = 'none';
});

// Close on outside click
apiKeyModal.addEventListener('click', (e) => {
    if (e.target === apiKeyModal) {
        apiKeyModal.style.display = 'none';
    }
});

// Save API keys
saveApiKeys.addEventListener('click', async () => {
    const openaiKey = document.getElementById('openaiKey').value.trim();
    const anthropicKey = document.getElementById('anthropicKey').value.trim();
    const deepseekKey = document.getElementById('deepseekKey').value.trim();

    // Save to localStorage
    if (openaiKey) localStorage.setItem('openai_api_key', openaiKey);
    if (anthropicKey) localStorage.setItem('anthropic_api_key', anthropicKey);
    if (deepseekKey) localStorage.setItem('deepseek_api_key', deepseekKey);

    // Send to backend
    try {
        const response = await fetch(`${API_URL}/api/config/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                api_keys: {
                    openai: openaiKey,
                    anthropic: anthropicKey,
                    deepseek: deepseekKey
                }
            })
        });

        if (response.ok) {
            addMessage('system', '✅ API Keys guardadas correctamente');
            apiKeyModal.style.display = 'none';
        } else {
            throw new Error('Error guardando keys');
        }
    } catch (error) {
        console.error('Error saving API keys:', error);
        addMessage('system', `❌ Error guardando API keys: ${error.message}`);
    }
});

// Model options for each provider
const modelOptions = {
    ollama: [
        'llama3.2:latest',
        'llama2',
        'codellama',
        'mistral',
        'mixtral',
        'neural-chat',
        'starling-lm'
    ],
    openai: [
        'gpt-4',
        'gpt-4-turbo',
        'gpt-3.5-turbo',
        'gpt-4o',
        'gpt-4o-mini'
    ],
    anthropic: [
        'claude-3-opus-20240229',
        'claude-3-sonnet-20240229',
        'claude-3-haiku-20240307',
        'claude-2.1',
        'claude-2.0'
    ],
    deepseek: [
        'deepseek-chat',
        'deepseek-coder'
    ]
};

// Update model selector based on provider
// Update model selector based on provider
async function updateModelSelector(provider) {
    const modelSelect = document.getElementById('modelSelect');
    let models = modelOptions[provider] || [];

    if (provider === 'ollama') {
        try {
            const response = await fetch(`${API_URL}/api/config/ollama-models`);
            const data = await response.json();
            if (data.models && data.models.length > 0) {
                models = data.models;
            }
        } catch (error) {
            console.error('Error fetching dynamic models:', error);
            models = modelOptions.ollama; // Fallback to hardcoded
        }
    }

    // Clear current options
    modelSelect.innerHTML = '';

    // Add new options
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
    });

    // Select first option by default
    if (models.length > 0) {
        modelSelect.value = models[0];
    }
}

// Model selector change handler
const modelSelect = document.getElementById('modelSelect');
if (modelSelect) {
    modelSelect.addEventListener('change', async (e) => {
        const newModel = e.target.value;
        const currentProvider = document.getElementById('providerSelect').value;

        try {
            const response = await fetch(`${API_URL}/api/config/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    llm_provider: currentProvider,
                    model: newModel
                })
            });

            if (response.ok) {
                await loadConfig();
                addMessage('system', `✅ Modelo cambiado a ${newModel}`);
            } else {
                throw new Error('Error en la respuesta');
            }
        } catch (error) {
            console.error('Error changing model:', error);
            addMessage('system', `❌ Error cambiando modelo: ${error.message}`);
        }
    });
}

// Vision Preview Polling
let visionPollingInterval = null;
const visionPreviewContainer = document.getElementById('visionPreviewContainer');
const visionPreviewImg = document.getElementById('visionPreviewImg');
const visionTimestamp = document.getElementById('visionTimestamp');
const closeVisionPreview = document.getElementById('closeVisionPreview');

async function updateVisionPreview() {
    try {
        const response = await fetch(`${API_URL}/api/vision/snapshot`);
        if (!response.ok) return;

        const data = await response.json();
        if (data.image_b64) {
            visionPreviewImg.src = `data:image/jpeg;base64,${data.image_b64}`;
            visionPreviewContainer.style.display = 'block';

            const time = new Date();
            visionTimestamp.textContent = `Actualizado: ${time.getHours()}:${time.getMinutes()}:${time.getSeconds()}`;
        }
    } catch (err) {
        console.warn("Error polling vision preview:", err);
    }
}

function startVisionPolling() {
    if (visionPollingInterval) return;
    updateVisionPreview(); // First call
    visionPollingInterval = setInterval(updateVisionPreview, 2000); // Every 2 seconds
}

function stopVisionPolling() {
    if (visionPollingInterval) {
        clearInterval(visionPollingInterval);
        visionPollingInterval = null;
    }
    if (visionPreviewContainer) {
        visionPreviewContainer.style.display = 'none';
    }
}

if (closeVisionPreview) {
    closeVisionPreview.addEventListener('click', stopVisionPolling);
}

// Start polling if we are in vision mode or if a snapshot is available
// For now, let's start it and let the backend decide if there's data
startVisionPolling();

// Interacción para el Preview de Visión
const toggleMaximize = document.getElementById('toggleMaximize');
if (toggleMaximize && visionPreviewContainer) {
    toggleMaximize.addEventListener('click', () => {
        visionPreviewContainer.classList.toggle('maximized');
        toggleMaximize.textContent = visionPreviewContainer.classList.contains('maximized') ? '🗗' : '🗖';
    });
}
