/**
 * Smart Classroom & Student Engagement AI Suite (Kaggle Edition)
 * Ultra-Vibrant Frontend Controller with English Detection Labels & Audio Alerts
 */

document.addEventListener('DOMContentLoaded', () => {
    // State
    let webcamStream = null;
    let scanInterval = null;
    let isAnalyzing = false;
    let studentsCache = [];
    let audioAlertsEnabled = true;
    let audioCtx = null;

    // Clean English Label Mapping for Camera Recognition
    const englishBehaviorLabels = {
        'handrise': 'HAND RAISED',
        'look_forward': 'ATTENTIVE',
        'read': 'READING',
        'sleep': 'DROWSY / ASLEEP [ALERT]',
        'stand': 'STANDING',
        'turn_head': 'DISTRACTED',
        'using_device': 'PHONE USAGE [ALERT]',
        'write': 'WRITING'
    };

    const classColors = {
        'handrise': '#a855f7',
        'look_forward': '#10b981',
        'read': '#06b6d4',
        'sleep': '#ef4444',
        'stand': '#3b82f6',
        'turn_head': '#f59e0b',
        'using_device': '#ef4444',
        'write': '#10b981'
    };

    // Soft Cyber Notification Chime
    function playAlertChime() {
        if (!audioAlertsEnabled) return;
        try {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            osc.type = 'sine';
            const now = audioCtx.currentTime;
            osc.frequency.setValueAtTime(587.33, now); // D5
            osc.frequency.exponentialRampToValueAtTime(880, now + 0.12); // A5
            gain.gain.setValueAtTime(0.08, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);

            osc.start(now);
            osc.stop(now + 0.3);
        } catch (e) {
            // AudioContext policy fallback
        }
    }

    // =========================================================================
    // 1. NAVIGATION & TAB SWITCHING
    // =========================================================================
    const navItems = document.querySelectorAll('.nav-item');
    const tabPanels = document.querySelectorAll('.tab-panel');
    const pageTitle = document.getElementById('page-title');

    const tabTitles = {
        'tab-overview': 'Classroom Analytics & Monitoring Suite',
        'tab-webcam': 'Live Computer Vision & Student Engagement (Kaggle Model)',
        'tab-ml': 'Machine Learning Academic Predictor',
        'tab-nlp': 'Natural Language Feedback & Sentiment Engine',
        'tab-database': 'SQLite Classroom Student Directory'
    };

    function switchTab(tabId) {
        navItems.forEach(item => {
            if (item.getAttribute('data-tab') === tabId) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        tabPanels.forEach(panel => {
            if (panel.id === tabId) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });

        if (tabTitles[tabId]) {
            pageTitle.textContent = tabTitles[tabId];
        }

        if (tabId === 'tab-database') {
            loadStudentsTable();
        } else if (tabId === 'tab-nlp') {
            loadFeedbackFeed();
        } else if (tabId === 'tab-overview') {
            loadDashboardStats();
            loadDashboardCharts();
        } else if (tabId === 'tab-webcam') {
            loadKaggleSampleGallery();
            loadAttendanceHistory();
        }
    }

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });

    document.getElementById('btn-quick-attendance')?.addEventListener('click', () => {
        switchTab('tab-webcam');
        startCameraStream();
    });

    document.getElementById('btn-refresh-data')?.addEventListener('click', () => {
        showToast('Refreshing all classroom analytics...');
        loadDashboardStats();
        loadDashboardCharts();
        loadAttendanceHistory();
    });

    // =========================================================================
    // 2. DASHBOARD & VISUAL ANALYTICS
    // =========================================================================
    async function loadDashboardStats() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();

            document.getElementById('kpi-total-students').textContent = data.total_students || 0;
            document.getElementById('kpi-avg-attendance').textContent = `${data.avg_attendance || 0}%`;
            document.getElementById('kpi-engagement').textContent = `${data.average_engagement || 88.5}%`;
            
            const posSentiment = data.sentiment ? Math.round((data.sentiment.positive / (data.sentiment.total || 1)) * 100) : 0;
            document.getElementById('kpi-sentiment').textContent = `${posSentiment}% Pos`;

            if (data.sentiment) {
                document.getElementById('val-pos').textContent = data.sentiment.positive;
                document.getElementById('val-neu').textContent = data.sentiment.neutral;
                document.getElementById('val-neg').textContent = data.sentiment.negative;
                renderSentimentDonut(data.sentiment.positive, data.sentiment.neutral, data.sentiment.negative);
            }
        } catch (err) {
            console.error('Error loading stats:', err);
        }
    }

    async function loadDashboardCharts() {
        try {
            const res = await fetch('/api/dashboard/chart-data');
            const data = await res.json();
            if (data.scatter_points) {
                renderScatterChart(data.scatter_points);
            }
        } catch (err) {
            console.error('Error loading chart data:', err);
        }
        refreshWordCloud();
    }

    function refreshWordCloud() {
        const wcImg = document.getElementById('dashboard-wordcloud-img');
        if (wcImg) {
            wcImg.src = `/api/feedback/wordcloud?t=${Date.now()}`;
        }
    }

    document.getElementById('btn-refresh-wc')?.addEventListener('click', () => {
        refreshWordCloud();
        showToast('Feedback WordCloud regenerated!');
    });

    function renderScatterChart(points) {
        const canvas = document.getElementById('canvas-scatter');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        ctx.clearRect(0, 0, W, H);

        const padLeft = 45;
        const padBottom = 35;
        const padTop = 20;
        const padRight = 20;

        const graphW = W - padLeft - padRight;
        const graphH = H - padTop - padBottom;

        ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
        ctx.lineWidth = 1;

        for (let score = 20; score <= 100; score += 20) {
            const y = padTop + graphH - (score / 100) * graphH;
            ctx.beginPath();
            ctx.moveTo(padLeft, y);
            ctx.lineTo(W - padRight, y);
            ctx.stroke();

            ctx.fillStyle = '#64748b';
            ctx.font = '10px JetBrains Mono';
            ctx.textAlign = 'right';
            ctx.fillText(score, padLeft - 8, y + 4);
        }

        for (let hours = 2; hours <= 10; hours += 2) {
            const x = padLeft + (hours / 10) * graphW;
            ctx.beginPath();
            ctx.moveTo(x, padTop);
            ctx.lineTo(x, H - padBottom);
            ctx.stroke();

            ctx.fillStyle = '#64748b';
            ctx.font = '10px JetBrains Mono';
            ctx.textAlign = 'center';
            ctx.fillText(hours + 'h', x, H - padBottom + 16);
        }

        ctx.fillStyle = '#94a3b8';
        ctx.font = '11px Outfit';
        ctx.textAlign = 'center';
        ctx.fillText('Weekly Study Hours →', padLeft + graphW / 2, H - 6);

        points.forEach(pt => {
            const x = padLeft + (Math.min(Math.max(pt.hours, 0), 10) / 10) * graphW;
            const y = padTop + graphH - (Math.min(Math.max(pt.score, 0), 100) / 100) * graphH;

            ctx.beginPath();
            ctx.arc(x, y, 6, 0, Math.PI * 2);
            if (pt.passed) {
                ctx.fillStyle = '#10b981';
                ctx.shadowColor = 'rgba(16, 185, 129, 0.7)';
            } else {
                ctx.fillStyle = '#ef4444';
                ctx.shadowColor = 'rgba(239, 68, 68, 0.7)';
            }
            ctx.shadowBlur = 10;
            ctx.fill();
            ctx.shadowBlur = 0;
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 1.5;
            ctx.stroke();
        });
    }

    function renderSentimentDonut(pos = 1, neu = 1, neg = 1) {
        const canvas = document.getElementById('canvas-sentiment');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;
        ctx.clearRect(0, 0, W, H);

        const total = pos + neu + neg;
        if (total === 0) return;

        const data = [
            { count: pos, color: '#10b981' },
            { count: neu, color: '#f59e0b' },
            { count: neg, color: '#ef4444' }
        ];

        let startAngle = -Math.PI / 2;
        const centerX = W / 2;
        const centerY = H / 2;
        const outerRadius = 70;
        const innerRadius = 45;

        data.forEach(slice => {
            const sliceAngle = (slice.count / total) * 2 * Math.PI;
            ctx.beginPath();
            ctx.arc(centerX, centerY, outerRadius, startAngle, startAngle + sliceAngle);
            ctx.arc(centerX, centerY, innerRadius, startAngle + sliceAngle, startAngle, true);
            ctx.closePath();
            ctx.fillStyle = slice.color;
            ctx.fill();
            startAngle += sliceAngle;
        });

        ctx.fillStyle = '#fff';
        ctx.font = 'bold 16px JetBrains Mono';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`${total}`, centerX, centerY - 6);
        ctx.font = '10px Outfit';
        ctx.fillStyle = '#94a3b8';
        ctx.fillText('Responses', centerX, centerY + 12);
    }

    // =========================================================================
    // 3. WEBCAM & KAGGLE BEHAVIOR RECOGNITION
    // =========================================================================
    const videoElem = document.getElementById('webcam-video');
    const visionCanvas = document.getElementById('vision-canvas');
    const camPlaceholder = document.getElementById('cam-placeholder');
    const camIndicator = document.getElementById('cam-indicator');
    const btnStartCamera = document.getElementById('btn-start-camera');
    const btnStopCamera = document.getElementById('btn-stop-camera');
    const btnSimulateFrame = document.getElementById('btn-simulate-frame');
    const btnLogAttendance = document.getElementById('btn-log-attendance');
    const chkAutoScan = document.getElementById('chk-auto-scan');
    const liveHeadcountVal = document.getElementById('live-headcount-val');
    const liveEngagementVal = document.getElementById('live-engagement-val');
    const processedSnapshot = document.getElementById('processed-snapshot');
    const alertBanner = document.getElementById('live-alert-banner');
    const alertText = document.getElementById('live-alert-text');
    const btnTriggerUpload = document.getElementById('btn-trigger-upload');
    const inputUploadImage = document.getElementById('input-upload-image');
    const scannerLaser = document.getElementById('scanner-laser');
    const btnToggleSound = document.getElementById('btn-toggle-sound');
    const soundStatusText = document.getElementById('sound-status-text');
    const soundIcon = document.getElementById('sound-icon');
    const btnDownloadFrame = document.getElementById('btn-download-frame');

    btnToggleSound?.addEventListener('click', () => {
        audioAlertsEnabled = !audioAlertsEnabled;
        if (audioAlertsEnabled) {
            soundIcon.textContent = '🔊';
            soundStatusText.textContent = 'Audio Alerts: ON';
            showToast('Audio alert chimes enabled.');
        } else {
            soundIcon.textContent = '🔇';
            soundStatusText.textContent = 'Audio Alerts: OFF';
            showToast('Audio alerts muted.');
        }
    });

    btnDownloadFrame?.addEventListener('click', () => {
        const activeSrc = processedSnapshot.style.display !== 'none' ? processedSnapshot.src : null;
        if (activeSrc) {
            const a = document.createElement('a');
            a.href = activeSrc;
            a.download = `SmartClass_Recognition_${Date.now()}.jpg`;
            a.click();
            showToast('Snapshot downloaded successfully!');
        } else if (webcamStream) {
            const saveCanvas = document.createElement('canvas');
            saveCanvas.width = videoElem.videoWidth || 640;
            saveCanvas.height = videoElem.videoHeight || 480;
            const sCtx = saveCanvas.getContext('2d');
            sCtx.drawImage(videoElem, 0, 0);
            sCtx.drawImage(visionCanvas, 0, 0);
            const a = document.createElement('a');
            a.href = saveCanvas.toDataURL('image/jpeg', 0.95);
            a.download = `SmartClass_LiveDetection_${Date.now()}.jpg`;
            a.click();
            showToast('Live detection frame downloaded!');
        } else {
            showToast('No active camera frame to download.', true);
        }
    });

    async function startCameraStream() {
        try {
            webcamStream = await navigator.mediaDevices.getUserMedia({
                video: { width: { ideal: 640 }, height: { ideal: 480 } },
                audio: false
            });

            videoElem.srcObject = webcamStream;
            videoElem.style.display = 'block';
            processedSnapshot.style.display = 'none';
            camPlaceholder.style.display = 'none';
            camIndicator.classList.add('active');
            btnStopCamera.disabled = false;
            scannerLaser.style.display = 'block';

            showToast('Live webcam stream started.');

            videoElem.onloadedmetadata = () => {
                visionCanvas.width = videoElem.videoWidth;
                visionCanvas.height = videoElem.videoHeight;
            };

            if (scanInterval) clearInterval(scanInterval);
            scanInterval = setInterval(() => {
                if (chkAutoScan.checked && !isAnalyzing) {
                    captureAndAnalyzeFrame(false);
                }
            }, 2000);

        } catch (err) {
            console.error('Camera access error:', err);
            showToast('Webcam not detected. Use "Test Demo Scene" or choose a Kaggle scene below.', true);
        }
    }

    function stopCameraStream() {
        if (webcamStream) {
            webcamStream.getTracks().forEach(track => track.stop());
            webcamStream = null;
        }
        if (scanInterval) {
            clearInterval(scanInterval);
            scanInterval = null;
        }
        videoElem.srcObject = null;
        camPlaceholder.style.display = 'flex';
        camIndicator.classList.remove('active');
        btnStopCamera.disabled = true;
        scannerLaser.style.display = 'none';

        const ctx = visionCanvas.getContext('2d');
        ctx.clearRect(0, 0, visionCanvas.width, visionCanvas.height);
        liveHeadcountVal.textContent = '0';
        liveEngagementVal.textContent = '--%';
        alertBanner.style.display = 'none';
        showToast('Webcam stream stopped.');
    }

    btnStartCamera?.addEventListener('click', startCameraStream);
    btnStopCamera?.addEventListener('click', stopCameraStream);

    async function captureAndAnalyzeFrame(saveSession = false) {
        if (!webcamStream || videoElem.readyState < 2) return;

        isAnalyzing = true;
        const offCanvas = document.createElement('canvas');
        offCanvas.width = videoElem.videoWidth || 640;
        offCanvas.height = videoElem.videoHeight || 480;
        const offCtx = offCanvas.getContext('2d');
        offCtx.drawImage(videoElem, 0, 0, offCanvas.width, offCanvas.height);

        const base64Data = offCanvas.toDataURL('image/jpeg', 0.85);

        try {
            const res = await fetch('/api/vision/analyze-frame', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: base64Data,
                    save_session: saveSession,
                    room: 'Lab-A1'
                })
            });

            const result = await res.json();
            if (result.success) {
                applyVisionResults(result, offCanvas.width, offCanvas.height);
                if (saveSession) {
                    showToast(`Logged attendance for ${result.headcount} students in SQLite!`);
                    loadAttendanceHistory();
                }
            }
        } catch (err) {
            console.error('Vision analysis error:', err);
        } finally {
            isAnalyzing = false;
        }
    }

    function applyVisionResults(data, width = 640, height = 480) {
        liveHeadcountVal.textContent = data.headcount;
        const eng = data.engagement_score || 85.0;
        liveEngagementVal.textContent = `${eng}%`;

        // Update 8 Behavior Cards
        const counts = data.behavior_counts || {};
        document.getElementById('cnt-lookforward').textContent = counts.look_forward || 0;
        document.getElementById('cnt-handrise').textContent = counts.handrise || 0;
        document.getElementById('cnt-read').textContent = counts.read || 0;
        document.getElementById('cnt-write').textContent = counts.write || 0;
        document.getElementById('cnt-stand').textContent = counts.stand || 0;
        document.getElementById('cnt-turnhead').textContent = counts.turn_head || 0;
        document.getElementById('cnt-sleep').textContent = counts.sleep || 0;
        document.getElementById('cnt-device').textContent = counts.using_device || 0;

        // Alerts Banner in Pure English
        if (data.alerts && data.alerts.length > 0) {
            alertBanner.style.display = 'flex';
            alertText.textContent = data.alerts.join('  •  ');
            playAlertChime();
        } else {
            alertBanner.style.display = 'none';
        }

        // Draw Bounding Boxes with English Labels
        drawVisionOverlay(data.detections || [], width, height);
    }

    // Draw English Bounding Boxes on Overlay Canvas
    function drawVisionOverlay(detections, videoW, videoH) {
        visionCanvas.width = videoW;
        visionCanvas.height = videoH;
        const ctx = visionCanvas.getContext('2d');
        ctx.clearRect(0, 0, videoW, videoH);

        detections.forEach(d => {
            const [x, y, w, h] = d.box;
            const beh = d.behavior;
            const color = classColors[beh] || '#06b6d4';

            // Glowing bounding box
            ctx.strokeStyle = color;
            ctx.lineWidth = 2.5;
            ctx.shadowColor = color;
            ctx.shadowBlur = 10;
            ctx.strokeRect(x, y, w, h);

            // High-tech corner reticle brackets
            const corner = Math.min(16, w / 4, h / 4);
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 3.5;
            ctx.beginPath(); ctx.moveTo(x, y + corner); ctx.lineTo(x, y); ctx.lineTo(x + corner, y); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(x + w - corner, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + corner); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(x, y + h - corner); ctx.lineTo(x, y + h); ctx.lineTo(x + corner, y + h); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(x + w - corner, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w, y + h - corner); ctx.stroke();

            // English Label Badge
            ctx.shadowBlur = 0;
            const englishName = englishBehaviorLabels[beh] || (d.label || beh).toUpperCase();
            const confPercent = Math.round((d.confidence || 0.85) * 100);
            const labelText = `${englishName} ${confPercent}%`;

            ctx.font = 'bold 11px JetBrains Mono';
            const textWidth = ctx.measureText(labelText).width;
            const badgeW = textWidth + 14;
            const badgeH = 22;
            const badgeY = Math.max(0, y - badgeH);

            ctx.fillStyle = color;
            ctx.fillRect(x, badgeY, badgeW, badgeH);

            // White text inside badge
            ctx.fillStyle = '#ffffff';
            ctx.fillText(labelText, x + 7, badgeY + 15);
        });
    }

    // Demo Scene Click
    btnSimulateFrame?.addEventListener('click', async () => {
        showToast('Running inference on simulated classroom scene...');
        try {
            const res = await fetch('/api/vision/analyze-frame', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP...', 
                    save_session: true,
                    room: 'Demo Classroom Scene'
                })
            });
            const data = await res.json();
            processedSnapshot.src = data.annotated_image;
            processedSnapshot.style.display = 'block';
            videoElem.style.display = 'none';
            camPlaceholder.style.display = 'none';
            scannerLaser.style.display = 'block';
            applyVisionResults(data);
            showToast(`Scene Evaluated: ${data.headcount} students, ${data.engagement_score}% engagement.`);
            loadAttendanceHistory();
        } catch (e) {
            console.error(e);
        }
    });

    btnLogAttendance?.addEventListener('click', () => {
        captureAndAnalyzeFrame(true);
    });

    // Image Upload
    btnTriggerUpload?.addEventListener('click', () => inputUploadImage.click());
    inputUploadImage?.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async (evt) => {
            const b64 = evt.target.result;
            showToast('Analyzing uploaded classroom photo with Kaggle AI model...');
            try {
                const res = await fetch('/api/vision/analyze-frame', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: b64, save_session: true, room: file.name })
                });
                const data = await res.json();
                processedSnapshot.src = data.annotated_image;
                processedSnapshot.style.display = 'block';
                videoElem.style.display = 'none';
                camPlaceholder.style.display = 'none';
                scannerLaser.style.display = 'block';
                applyVisionResults(data);
                showToast(`Evaluated: ${data.headcount} students detected (${data.engagement_score}% engagement)!`);
                loadAttendanceHistory();
            } catch (err) {
                console.error(err);
            }
        };
        reader.readAsDataURL(file);
    });

    // Load Kaggle Dataset Sample Gallery
    async function loadKaggleSampleGallery() {
        const grid = document.getElementById('sample-gallery-grid');
        if (!grid) return;

        try {
            const res = await fetch('/api/dataset/sample-images');
            const data = await res.json();
            const samples = data.samples || [];

            if (samples.length === 0) {
                grid.innerHTML = '<div class="loading-samples">No sample images found in dataset.</div>';
                return;
            }

            grid.innerHTML = samples.map(s => `
                <div class="sample-card" data-filename="${s.filename}" title="Click to test with trained Kaggle model">
                    <img src="${s.url}" alt="${s.title}" class="sample-thumb" loading="lazy">
                    <div class="sample-title">${s.title}</div>
                </div>
            `).join('');

            grid.querySelectorAll('.sample-card').forEach(card => {
                card.addEventListener('click', async () => {
                    const filename = card.getAttribute('data-filename');
                    showToast(`Evaluating Kaggle scene: ${filename}...`);
                    try {
                        const res = await fetch('/api/dataset/analyze-sample', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ filename, save_session: true })
                        });
                        const data = await res.json();

                        processedSnapshot.src = data.annotated_image;
                        processedSnapshot.style.display = 'block';
                        videoElem.style.display = 'none';
                        camPlaceholder.style.display = 'none';
                        scannerLaser.style.display = 'block';
                        applyVisionResults(data);

                        showToast(`Analysis Complete: ${data.headcount} students recognized!`);
                        loadAttendanceHistory();
                    } catch (err) {
                        console.error('Error analyzing sample:', err);
                    }
                });
            });

        } catch (err) {
            console.error('Error loading Kaggle samples:', err);
        }
    }

    // Attendance History Fetch
    async function loadAttendanceHistory() {
        const list = document.getElementById('attendance-history-list');
        if (!list) return;

        try {
            const res = await fetch('/api/attendance/sessions');
            const data = await res.json();

            if (!data.sessions || data.sessions.length === 0) {
                list.innerHTML = '<div class="empty-state">No attendance sessions logged yet today.</div>';
                return;
            }

            list.innerHTML = data.sessions.map(s => `
                <div class="session-card">
                    <div>
                        <div style="font-weight: 700; color: #fff; font-size: 0.88rem;">${s.room_id || 'Classroom 101'}</div>
                        <span class="session-time">${s.timestamp}</span>
                        ${s.alerts ? `<div style="font-size: 0.72rem; color: #f87171; font-weight: 600; margin-top: 2px;">⚠️ ${s.alerts}</div>` : ''}
                    </div>
                    <div>
                        <div class="session-count">${s.headcount} Present</div>
                        <span class="session-eng">${s.engagement_score || 85}% Engaged</span>
                    </div>
                </div>
            `).join('');
        } catch (err) {
            console.error('Error fetching attendance ledger:', err);
        }
    }

    // =========================================================================
    // 4. MACHINE LEARNING OUTCOME PREDICTOR
    // =========================================================================
    const inputHours = document.getElementById('input-study-hours');
    const inputAttendance = document.getElementById('input-attendance');
    const inputAssignments = document.getElementById('input-assignments');
    const lblHours = document.getElementById('lbl-study-hours');
    const lblAttendance = document.getElementById('lbl-attendance');
    const lblAssignments = document.getElementById('lbl-assignments');
    const formPredictor = document.getElementById('form-predictor');

    function updateSliderLabels() {
        lblHours.textContent = `${parseFloat(inputHours.value).toFixed(1)} hrs`;
        lblAttendance.textContent = `${inputAttendance.value} %`;
        lblAssignments.textContent = inputAssignments.value;
    }

    [inputHours, inputAttendance, inputAssignments].forEach(slider => {
        slider?.addEventListener('input', () => {
            updateSliderLabels();
            runInference();
        });
    });

    document.querySelectorAll('.btn-preset').forEach(btn => {
        btn.addEventListener('click', () => {
            inputHours.value = btn.getAttribute('data-h');
            inputAttendance.value = btn.getAttribute('data-a');
            inputAssignments.value = btn.getAttribute('data-as');
            updateSliderLabels();
            runInference();
        });
    });

    formPredictor?.addEventListener('submit', (e) => {
        e.preventDefault();
        runInference();
    });

    async function runInference() {
        const payload = {
            study_hours: parseFloat(inputHours.value),
            attendance: parseFloat(inputAttendance.value),
            assignments_completed: parseInt(inputAssignments.value, 10)
        };

        try {
            const res = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            const gaugeFill = document.getElementById('gauge-fill');
            const gaugeText = document.getElementById('gauge-text');
            const prob = data.pass_probability || 0;

            if (gaugeFill && gaugeText) {
                gaugeFill.setAttribute('stroke-dasharray', `${prob}, 100`);
                gaugeText.textContent = `${prob}%`;
                gaugeFill.style.stroke = data.prediction_binary === 1 ? '#10b981' : '#ef4444';
            }

            const outResult = document.getElementById('out-result');
            outResult.textContent = data.prediction_text;
            outResult.className = `box-value ${data.prediction_binary === 1 ? 'pass' : 'fail'}`;

            document.getElementById('out-score').textContent = `${data.predicted_exam_score} / 100`;
            document.getElementById('out-cluster').textContent = data.cluster_profile || 'Standard';

            document.getElementById('recommendation-text').innerHTML = `
                <strong>AI Guidance:</strong> ${data.recommendation}
            `;
        } catch (err) {
            console.error('Inference error:', err);
        }
    }

    // =========================================================================
    // 5. NLP SENTIMENT & VOICE ANALYZER
    // =========================================================================
    const fbCommentInput = document.getElementById('fb-comment');
    const formFeedback = document.getElementById('form-feedback');

    fbCommentInput?.addEventListener('input', () => {
        const text = fbCommentInput.value.toLowerCase();
        let polarity = 0;
        let subjectivity = 0.2;

        const positives = ['good', 'great', 'love', 'loved', 'awesome', 'excellent', 'clear', 'helpful', 'engaging', 'best'];
        const negatives = ['bad', 'poor', 'hard', 'difficult', 'fast', 'slow', 'confusing', 'boring', 'hate', 'worst'];

        positives.forEach(w => { if (text.includes(w)) polarity += 0.35; });
        negatives.forEach(w => { if (text.includes(w)) polarity -= 0.35; });

        polarity = Math.max(-1.0, Math.min(1.0, polarity));
        if (Math.abs(polarity) > 0.1) subjectivity = 0.65;

        document.getElementById('live-polarity').textContent = polarity.toFixed(2);
        document.getElementById('live-subjectivity').textContent = subjectivity.toFixed(2);

        const moodTag = document.getElementById('live-mood');
        if (polarity > 0.15) {
            moodTag.className = 'mood-tag positive';
            moodTag.textContent = 'POSITIVE 😊';
        } else if (polarity < -0.15) {
            moodTag.className = 'mood-tag negative';
            moodTag.textContent = 'NEGATIVE 😟';
        } else {
            moodTag.className = 'mood-tag neutral';
            moodTag.textContent = 'NEUTRAL 😐';
        }
    });

    formFeedback?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const studentName = document.getElementById('fb-student-name').value.trim() || 'Anonymous Student';
        const comment = fbCommentInput.value.trim();

        if (!comment) {
            showToast('Please enter a feedback message before submitting.', true);
            return;
        }

        try {
            const res = await fetch('/api/feedback/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ student_name: studentName, comment })
            });

            const data = await res.json();
            if (data.success) {
                showToast(`Feedback logged: ${data.sentiment_label}`);
                fbCommentInput.value = '';
                loadFeedbackFeed();
                loadDashboardStats();
                refreshWordCloud();
            }
        } catch (err) {
            console.error('Feedback submission error:', err);
        }
    });

    async function loadFeedbackFeed() {
        const feedList = document.getElementById('feedback-feed-list');
        if (!feedList) return;

        try {
            const res = await fetch('/api/feedback/recent');
            const data = await res.json();

            if (!data.feedbacks || data.feedbacks.length === 0) {
                feedList.innerHTML = '<div class="empty-state">No feedback submitted yet.</div>';
                return;
            }

            feedList.innerHTML = data.feedbacks.map(fb => {
                let badgeClass = 'positive';
                if (fb.sentiment_label === 'Negative') badgeClass = 'negative';
                if (fb.sentiment_label === 'Neutral') badgeClass = 'neutral';

                return `
                    <div class="feedback-card">
                        <div class="feedback-top">
                            <span class="feedback-author">${fb.student_name || 'Student'}</span>
                            <span class="mood-tag ${badgeClass}">${fb.sentiment_label} (${fb.polarity > 0 ? '+' : ''}${fb.polarity})</span>
                        </div>
                        <p class="feedback-text">"${fb.comment}"</p>
                        <div class="feedback-meta">
                            <span>Subjectivity: ${fb.subjectivity}</span>
                            <span>Time: ${fb.timestamp || 'Just now'}</span>
                        </div>
                    </div>
                `;
            }).join('');
        } catch (err) {
            console.error('Feedback feed load error:', err);
        }
    }

    // =========================================================================
    // 6. SQLITE STUDENT DIRECTORY
    // =========================================================================
    const searchStudent = document.getElementById('search-student');
    const filterRisk = document.getElementById('filter-risk');
    const filterResult = document.getElementById('filter-result');
    const modalAddStudent = document.getElementById('modal-add-student');
    const btnOpenAddStudent = document.getElementById('btn-open-add-student');
    const btnCloseModal = document.getElementById('btn-close-modal');
    const formNewStudent = document.getElementById('form-new-student');

    async function loadStudentsTable() {
        const tbody = document.getElementById('students-table-body');
        if (!tbody) return;

        try {
            const res = await fetch('/api/students');
            const data = await res.json();
            studentsCache = data.students || [];
            renderFilteredStudents();
        } catch (err) {
            console.error('Error fetching students:', err);
        }
    }

    function renderFilteredStudents() {
        const tbody = document.getElementById('students-table-body');
        if (!tbody) return;

        const query = searchStudent.value.toLowerCase().trim();
        const risk = filterRisk.value;
        const result = filterResult.value;

        const filtered = studentsCache.filter(s => {
            const matchesSearch = s.student_id.toLowerCase().includes(query) || s.student_name.toLowerCase().includes(query);
            const matchesRisk = (risk === 'All') || (s.academic_risk === risk);
            const matchesResult = (result === 'All') || (s.result === result);
            return matchesSearch && matchesRisk && matchesResult;
        });

        if (filtered.length === 0) {
            tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; padding: 24px; color: #64748b;">No students found matching current filters.</td></tr>`;
            return;
        }

        tbody.innerHTML = filtered.map(s => {
            const riskClass = s.academic_risk.toLowerCase();
            const resultClass = s.result.toLowerCase();

            return `
                <tr>
                    <td style="font-family: var(--font-mono); font-weight: 700; color: #a5b4fc;">${s.student_id}</td>
                    <td style="font-weight: 600; color: #fff;">${s.student_name}</td>
                    <td>${s.study_hours} hrs/wk</td>
                    <td>${s.attendance}%</td>
                    <td>${s.assignments_completed}/20</td>
                    <td style="font-family: var(--font-mono); font-weight: 700;">${s.exam_score}</td>
                    <td><span class="status-badge ${resultClass}">${s.result}</span></td>
                    <td><span class="pill-risk ${riskClass}">${s.academic_risk}</span></td>
                    <td>
                        <button class="btn btn-outline btn-sm" onclick="window.testStudentInML(${s.study_hours}, ${s.attendance}, ${s.assignments_completed})">
                            Predict ML
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    [searchStudent, filterRisk, filterResult].forEach(el => {
        el?.addEventListener('input', renderFilteredStudents);
        el?.addEventListener('change', renderFilteredStudents);
    });

    window.testStudentInML = (h, a, as) => {
        switchTab('tab-ml');
        inputHours.value = h;
        inputAttendance.value = a;
        inputAssignments.value = as;
        updateSliderLabels();
        runInference();
        showToast('Loaded student attributes into ML Outcome Predictor.');
    };

    btnOpenAddStudent?.addEventListener('click', () => modalAddStudent.classList.add('active'));
    btnCloseModal?.addEventListener('click', () => modalAddStudent.classList.remove('active'));
    modalAddStudent?.addEventListener('click', (e) => {
        if (e.target === modalAddStudent) modalAddStudent.classList.remove('active');
    });

    formNewStudent?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const newStudent = {
            student_id: document.getElementById('new-id').value.trim(),
            student_name: document.getElementById('new-name').value.trim(),
            study_hours: parseFloat(document.getElementById('new-hours').value),
            attendance: parseFloat(document.getElementById('new-attendance').value),
            assignments_completed: parseInt(document.getElementById('new-assignments').value, 10)
        };

        try {
            const res = await fetch('/api/students', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newStudent)
            });
            const data = await res.json();
            if (data.success) {
                showToast(`Student ${data.student.student_name} added to SQLite!`);
                modalAddStudent.classList.remove('active');
                formNewStudent.reset();
                loadStudentsTable();
                loadDashboardStats();
            }
        } catch (err) {
            console.error('Error adding student:', err);
        }
    });

    function showToast(message, isError = false) {
        const toast = document.getElementById('toast-notification');
        if (!toast) return;
        toast.textContent = message;
        toast.style.borderColor = isError ? 'var(--red)' : 'var(--cyan)';
        toast.style.display = 'flex';
        setTimeout(() => {
            toast.style.display = 'none';
        }, 3200);
    }

    // =========================================================================
    // INITIALIZATION
    // =========================================================================
    loadDashboardStats();
    loadDashboardCharts();
    loadAttendanceHistory();
    loadKaggleSampleGallery();
    runInference();
});
