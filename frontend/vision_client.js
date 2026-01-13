/**
 * Vision Client - Lógica de WebRTC para streaming de cámara móvil
 */

// Ahora Front y Back viven en el mismo sitio
const API_URL = window.location.origin;

const video = document.getElementById('video');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusOverlay = document.getElementById('statusOverlay');
const errorBox = document.getElementById('errorBox');

let pc = null;

function showError(msg) {
    errorBox.innerHTML = msg;
    errorBox.style.display = 'block';
    statusOverlay.style.display = 'none';
}

// Verificar Seguridad
const isSecure = window.location.protocol === 'https:' ||
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname.includes('.loca.lt');

if (!isSecure) {
    showError(`⚠️ <b>Error de Seguridad</b><br><br>
               Los móviles BLOQUEAN la cámara si no es <b>HTTPS</b>.<br><br>
               Usa el link seguro que te pasó el Agente.`);
}

async function startStreaming() {
    try {
        errorBox.style.display = 'none';
        statusOverlay.style.display = 'block';
        statusOverlay.textContent = "Solicitando permisos...";

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error("Navegador no compatible o bloqueado por falta de HTTPS.");
        }

        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: "environment",
                width: { ideal: 480 },
                height: { ideal: 360 }
            },
            audio: false
        }).catch(err => {
            if (err.name === 'NotAllowedError') {
                throw new Error("Permiso denegado. <br>Debes permitir el acceso a la cámara.");
            }
            throw err;
        });

        video.srcObject = stream;
        statusOverlay.textContent = "Conectando...";

        pc = new RTCPeerConnection({
            iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
        });

        stream.getTracks().forEach(track => pc.addTrack(track, stream));

        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        const response = await fetch(`${API_URL}/api/vision/offer`, {
            method: 'POST',
            body: JSON.stringify({
                sdp: pc.localDescription.sdp,
                type: pc.localDescription.type
            }),
            headers: {
                'Content-Type': 'application/json',
                'Bypass-Tunnel-Reminder': 'true'
            }
        });

        if (!response.ok) throw new Error("El cerebro no responde (Túnel bloqueado).");

        let answer;
        try {
            answer = await response.json();
        } catch (e) {
            throw new Error(`⚠️ <b>Túnel bloqueado</b><br><br>
                1. <a href="${API_URL}" target="_blank" style="color:#fff; font-weight:bold">Haz clic aquí para autorizar</a><br>
                2. Dale a "Click to Continue"<br>
                3. Regresa aquí y dale a "Transmitir Cámara"`);
        }

        await pc.setRemoteDescription(new RTCSessionDescription(answer));

        statusOverlay.textContent = "📡 EN VIVO";
        statusOverlay.style.background = "#10b981";
        startBtn.style.display = "none";
        stopBtn.style.display = "block";

    } catch (err) {
        console.error(err);
        showError(`❌ <b>Error:</b> ${err.message}`);
    }
}

function stopStreaming() {
    if (pc) { pc.close(); pc = null; }
    if (video.srcObject) {
        video.srcObject.getTracks().forEach(track => track.stop());
        video.srcObject = null;
    }
    statusOverlay.textContent = "Detenido";
    statusOverlay.style.background = "rgba(0,0,0,0.5)";
    startBtn.style.display = "block";
    stopBtn.style.display = "none";
}

startBtn.addEventListener('click', startStreaming);
stopBtn.addEventListener('click', stopStreaming);

// Lógica de Anotaciones (Annotator Mode)
const canvas = document.getElementById('annotationLayer');
const ctx = canvas.getContext('2d');
let annotationInterval = null;

function resizeCanvas() {
    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

async function pollAnnotations() {
    try {
        const response = await fetch(`${API_URL}/api/vision/annotations`);
        if (!response.ok) return;
        
        const data = await response.json();
        drawAnnotations(data.annotations);
    } catch (err) {
        console.warn("Error polling annotations:", err);
    }
}

function drawAnnotations(annotations) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (!annotations || annotations.length === 0) return;
    
    annotations.forEach(ann => {
        const x = (ann.x / 100) * canvas.width;
        const y = (ann.y / 100) * canvas.height;
        
        ctx.beginPath();
        ctx.arc(x, y, 15, 0, 2 * Math.PI);
        ctx.strokeStyle = ann.color || "#ff0000";
        ctx.lineWidth = 3;
        ctx.stroke();
        
        // Efecto de pulso (simple)
        ctx.beginPath();
        ctx.arc(x, y, 20, 0, 2 * Math.PI);
        ctx.strokeStyle = (ann.color || "#ff0000") + "44"; // Transparente
        ctx.lineWidth = 2;
        ctx.stroke();

        if (ann.label) {
            ctx.fillStyle = ann.color || "#ff0000";
            ctx.font = "bold 16px Arial";
            ctx.fillText(ann.label, x + 20, y + 5);
        }
    });
}

function startAnnotationPolling() {
    if (annotationInterval) return;
    resizeCanvas();
    annotationInterval = setInterval(pollAnnotations, 1000);
}

function stopAnnotationPolling() {
    if (annotationInterval) {
        clearInterval(annotationInterval);
        annotationInterval = null;
    }
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

// Iniciar polling al conectar
startBtn.addEventListener('click', startAnnotationPolling);
stopBtn.addEventListener('click', stopStreaming);
stopBtn.addEventListener('click', stopAnnotationPolling);
