// Jukebox From Hell - Frontend

const form = document.getElementById('search-form');
const queryInput = document.getElementById('query');
const searchBtn = document.getElementById('search-btn');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const errorMsg = document.getElementById('error-msg');
const player = document.getElementById('player');
const audio = document.getElementById('audio');
const mascot = document.getElementById('mascot');

const playerTitle = document.getElementById('player-title');
const playerArtist = document.getElementById('player-artist');
const playerThumb = document.getElementById('player-thumb');
const playerDuration = document.getElementById('player-duration');
const visualizerCanvas = document.getElementById('visualizer');

let audioContext = null;
let analyser = null;
let animationId = null;
let sourceConnected = false;

// Search
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;

    showState('loading');

    try {
        const res = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query }),
        });

        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || 'The jukebox jammed. Try again.');
        }

        const track = await res.json();
        playTrack(track);
    } catch (err) {
        showError(err.message);
    }
});

function playTrack(track) {
    playerTitle.textContent = track.title;
    playerArtist.textContent = track.artist;
    playerDuration.textContent = track.duration ? formatDuration(track.duration) : '';

    if (track.thumbnail) {
        playerThumb.src = track.thumbnail;
        playerThumb.classList.remove('hidden');
    } else {
        playerThumb.classList.add('hidden');
    }

    audio.src = `/api/stream/${track.id}`;
    audio.load();
    audio.play().catch(() => {}); // autoplay may be blocked

    showState('player');
    mascot.classList.add('mascot-playing');

    // Media Session API for mobile lock screen controls
    if ('mediaSession' in navigator) {
        navigator.mediaSession.metadata = new MediaMetadata({
            title: track.title,
            artist: track.artist,
            artwork: track.thumbnail
                ? [{ src: track.thumbnail, sizes: '512x512', type: 'image/jpeg' }]
                : [],
        });
    }

    initVisualizer();
}

// Audio visualizer using Web Audio API
function initVisualizer() {
    if (!visualizerCanvas) return;

    try {
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }

        analyser = audioContext.createAnalyser();
        analyser.fftSize = 128;

        if (!sourceConnected) {
            const source = audioContext.createMediaElementSource(audio);
            source.connect(analyser);
            analyser.connect(audioContext.destination);
            sourceConnected = true;
        }

        if (audioContext.state === 'suspended') {
            audioContext.resume();
        }

        drawVisualizer();
    } catch (e) {
        // Web Audio API not supported or CORS issue - hide visualizer
        visualizerCanvas.classList.add('hidden');
    }
}

function drawVisualizer() {
    if (!analyser || !visualizerCanvas) return;

    const ctx = visualizerCanvas.getContext('2d');
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    const width = visualizerCanvas.width = visualizerCanvas.offsetWidth * window.devicePixelRatio;
    const height = visualizerCanvas.height = visualizerCanvas.offsetHeight * window.devicePixelRatio;

    function draw() {
        animationId = requestAnimationFrame(draw);
        analyser.getByteFrequencyData(dataArray);

        ctx.clearRect(0, 0, width, height);

        const barCount = bufferLength;
        const barWidth = width / barCount;
        const gap = 2;

        for (let i = 0; i < barCount; i++) {
            const value = dataArray[i] / 255;
            const barHeight = value * height;

            // Gradient from cyan to red based on intensity
            const hue = 190 - (value * 170); // cyan(190) -> red(20)
            ctx.fillStyle = `hsla(${hue}, 100%, 55%, ${0.6 + value * 0.4})`;

            const x = i * barWidth + gap / 2;
            ctx.fillRect(x, height - barHeight, barWidth - gap, barHeight);
        }
    }

    draw();
}

// State management
function showState(state) {
    loading.classList.add('hidden');
    error.classList.add('hidden');
    player.classList.add('hidden');
    searchBtn.disabled = false;

    switch (state) {
        case 'loading':
            loading.classList.remove('hidden');
            loading.classList.add('fade-in');
            searchBtn.disabled = true;
            break;
        case 'player':
            player.classList.remove('hidden');
            player.classList.add('fade-in');
            break;
        case 'error':
            error.classList.remove('hidden');
            error.classList.add('fade-in');
            break;
    }
}

function showError(msg) {
    errorMsg.textContent = msg;
    showState('error');
}

function resetPlayer() {
    showState('idle');
    mascot.classList.remove('mascot-playing');
    audio.pause();
    audio.src = '';
    queryInput.value = '';
    queryInput.focus();

    if (animationId) {
        cancelAnimationFrame(animationId);
        animationId = null;
    }
}

// Make resetPlayer available globally (used by onclick in template)
window.resetPlayer = resetPlayer;

// Pause visualizer when audio pauses
audio.addEventListener('pause', () => {
    mascot.classList.remove('mascot-playing');
});

audio.addEventListener('play', () => {
    mascot.classList.add('mascot-playing');
    if (audioContext && audioContext.state === 'suspended') {
        audioContext.resume();
    }
});

// Utility
function formatDuration(seconds) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
}
