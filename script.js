const videoElement = document.querySelector('.input_video');
const canvasElement = document.querySelector('.output_canvas');
const canvasCtx = canvasElement.getContext('2d');

const totalEl = document.getElementById('totalCounter');
const perHandEl = document.getElementById('perHand');

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');

let camera = null;

const TIP = [4, 8, 12, 16, 20];
const PIP = [null, 6, 10, 14, 18];

function countFingers(landmarks, handednessLabel, width, height) {
	const pts = landmarks.map(lm => [lm.x * width, lm.y * height]);

	let up = 0;

	const tipX = pts[4][0];
	const mcpX = pts[2][0];
	if (handednessLabel === 'Right') {
		if (tipX > mcpX) up++;
	} else {
		if (tipX < mcpX) up++;
	}

	for (let i = 1; i < 5; i++) {
		const tipY = pts[TIP[i]][1];
		const pipY = pts[PIP[i]][1];
		if (tipY < pipY) up++;
	}
	return up;
}

function onResults(results) {
	const vw = videoElement.videoWidth || 1280;
	const vh = videoElement.videoHeight || 720;

	canvasElement.width = vw;
	canvasElement.height = vh;

	canvasCtx.save();
	canvasCtx.clearRect(0, 0, vw, vh);
	canvasCtx.drawImage(results.image, 0, 0, vw, vh);

	let total = 0;
	let perHandLines = [];

	if (results.multiHandLandmarks && results.multiHandedness) {
		for (let i = 0; i < results.multiHandLandmarks.length; i++) {
			const handLms = results.multiHandLandmarks[i];
			const handed = results.multiHandedness[i].label;

			window.drawConnectors(canvasCtx, handLms, window.HAND_CONNECTIONS, { color: '#22c55e', lineWidth: 4 });
			window.drawLandmarks(canvasCtx, handLms, { color: '#0ea5e9', lineWidth: 2, radius: 2 });

			const cnt = countFingers(handLms, handed, vw, vh);
			total += cnt;
			perHandLines.push(`${handed} hand: ${cnt}`);
		}
	}

	totalEl.textContent = `Total: ${total}`;
	perHandEl.textContent = perHandLines.join('\n');

	canvasCtx.restore();
}

const hands = new window.Hands({
	locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
});
hands.setOptions({
	selfieMode: true,
	maxNumHands: 2,
	modelComplexity: 1,
	minDetectionConfidence: 0.6,
	minTrackingConfidence: 0.6,
});
hands.onResults(onResults);

async function start() {
	startBtn.disabled = true;
	stopBtn.disabled = false;

	camera = new window.Camera(videoElement, {
		onFrame: async () => { await hands.send({ image: videoElement }); },
		width: 1280,
		height: 720,
	});
	await camera.start();
}

async function stop() {
	stopBtn.disabled = true;
	startBtn.disabled = false;

	if (camera) {
		await camera.stop();
		camera = null;
	}
	const vw = videoElement.videoWidth || 1280;
	const vh = videoElement.videoHeight || 720;
	canvasCtx.clearRect(0, 0, vw, vh);
	totalEl.textContent = 'Total: 0';
	perHandEl.textContent = '';
}

startBtn.addEventListener('click', start);
stopBtn.addEventListener('click', stop);


