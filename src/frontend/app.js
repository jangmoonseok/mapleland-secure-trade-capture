document.addEventListener('DOMContentLoaded', () => {
    const startStreamBtn = document.getElementById('startStreamBtn');
    const videoContainer = document.getElementById('videoContainer');
    const screenVideo = document.getElementById('screenVideo');
    const captureCanvas = document.getElementById('captureCanvas');
    const manualCaptureBtn = document.getElementById('manualCaptureBtn');
    
    const itemNameInput = document.getElementById('itemName');
    const statSTRInput = document.getElementById('statSTR');
    const statDEXInput = document.getElementById('statDEX');
    const statLUKInput = document.getElementById('statLUK');
    const statusMessage = document.getElementById('statusMessage');
    const submitBtn = document.querySelector('.submit-btn');

    let isStreaming = false;

    // Start Screen Stream
    startStreamBtn.addEventListener('click', async () => {
        try {
            const stream = await navigator.mediaDevices.getDisplayMedia({
                video: { cursor: "always" },
                audio: false
            });
            screenVideo.srcObject = stream;
            videoContainer.style.display = 'block';
            startStreamBtn.textContent = '스트리밍 중...';
            startStreamBtn.disabled = true;
            isStreaming = true;
            
            // Stop stream listener
            stream.getVideoTracks()[0].onended = () => {
                isStreaming = false;
                startStreamBtn.textContent = '화면 공유 시작';
                startStreamBtn.disabled = false;
                videoContainer.style.display = 'none';
            };
        } catch (err) {
            console.error("Error starting screen capture:", err);
            setStatus("화면 캡처 권한을 얻지 못했습니다.", "error");
        }
    });

    // Listen for PrintScreen key
    window.addEventListener('keyup', (e) => {
        if (e.key === "PrintScreen" && isStreaming) {
            captureAndProcessFrame();
        }
    });

    // Manual Capture Fallback
    manualCaptureBtn.addEventListener('click', () => {
        if (isStreaming) {
            captureAndProcessFrame();
        }
    });

    function setStatus(msg, type) {
        statusMessage.textContent = msg;
        statusMessage.className = 'status-message'; // reset
        if (type) {
            statusMessage.classList.add(`status-${type}`);
        }
    }

    async function captureAndProcessFrame() {
        if (!isStreaming) return;
        
        setStatus("프레임을 캡처하여 분석 중입니다...", "processing");
        
        const context = captureCanvas.getContext('2d');
        captureCanvas.width = screenVideo.videoWidth;
        captureCanvas.height = screenVideo.videoHeight;
        
        // Draw video frame to canvas
        context.drawImage(screenVideo, 0, 0, captureCanvas.width, captureCanvas.height);
        
        // Convert canvas to blob
        captureCanvas.toBlob(async (blob) => {
            if (!blob) {
                setStatus("이미지를 캡처하지 못했습니다.", "error");
                return;
            }

            try {
                // Send to backend OCR
                const formData = new FormData();
                formData.append("image", blob, "capture.png");

                const response = await fetch("http://localhost:8000/api/extract", {
                    method: "POST",
                    body: formData
                });

                if (!response.ok) {
                    throw new Error("서버 응답 오류가 발생했습니다.");
                }

                const data = await response.json();

                if (data.error) {
                    setStatus(`검증 에러: ${data.error}`, "error");
                    return;
                }

                // Auto-fill form
                itemNameInput.value = data.item_name || "알 수 없음";
                statSTRInput.value = data.stats?.STR || 0;
                statDEXInput.value = data.stats?.DEX || 0;
                statLUKInput.value = data.stats?.LUK || 0;
                
                setStatus("아이템을 성공적으로 분석하고 검증했습니다!", "success");
                submitBtn.disabled = false;
                
            } catch (err) {
                console.error("OCR API Error:", err);
                // For demonstration, mock fill if backend fails or isn't running
                setStatus("백엔드에 연결할 수 없습니다. 시연용 가상 데이터를 입력합니다.", "processing");
                setTimeout(() => {
                    itemNameInput.value = "노가다 목장갑 (가상)";
                    statSTRInput.value = 5;
                    statDEXInput.value = 0;
                    statLUKInput.value = 2;
                    setStatus("아이템 분석 완료 (가상 데이터)!", "success");
                    submitBtn.disabled = false;
                }, 1000);
            }
        }, 'image/png');
    }
});
