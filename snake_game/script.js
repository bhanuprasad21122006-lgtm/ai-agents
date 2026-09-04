/**
 * NEON ARCADE SNAKE ENGINE
 * Built with HTML5 Canvas, Vanilla JS & Web Audio API
 */

// --- CONFIGURATION & CONSTANTS ---
const GRID_SIZE = 20; // 20x20 grid
const STORAGE_KEY_HIGH_SCORE = 'snake_high_score';
const STORAGE_KEY_MUTED = 'snake_muted';

// Direction Vectors
const DIR = {
    UP: { x: 0, y: -1, name: 'UP' },
    DOWN: { x: 0, y: 1, name: 'DOWN' },
    LEFT: { x: -1, y: 0, name: 'LEFT' },
    RIGHT: { x: 1, y: 0, name: 'RIGHT' }
};

// --- AUDIO SYNTHESIZER (WEB AUDIO API) ---
class SoundController {
    constructor() {
        this.ctx = null;
        this.isMuted = localStorage.getItem(STORAGE_KEY_MUTED) === 'true';
    }

    init() {
        if (!this.ctx) {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (AudioCtx) {
                this.ctx = new AudioCtx();
            }
        }
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    toggleMute() {
        this.isMuted = !this.isMuted;
        localStorage.setItem(STORAGE_KEY_MUTED, this.isMuted);
        return this.isMuted;
    }

    playEatStandard() {
        if (this.isMuted) return;
        this.init();
        if (!this.ctx) return;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        const now = this.ctx.currentTime;

        osc.type = 'sine';
        osc.frequency.setValueAtTime(320, now);
        osc.frequency.exponentialRampToValueAtTime(780, now + 0.08);

        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.08);
    }

    playEatGolden() {
        if (this.isMuted) return;
        this.init();
        if (!this.ctx) return;

        const notes = [523.25, 659.25, 783.99]; // C5, E5, G5 arpeggio
        notes.forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            const now = this.ctx.currentTime + idx * 0.05;

            osc.type = 'triangle';
            osc.frequency.setValueAtTime(freq, now);

            gain.gain.setValueAtTime(0.2, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.12);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now);
            osc.stop(now + 0.12);
        });
    }

    playLevelUp() {
        if (this.isMuted) return;
        this.init();
        if (!this.ctx) return;

        const chord = [440, 554.37, 659.25, 880]; // A4, C#5, E5, A5
        chord.forEach((freq, i) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            const now = this.ctx.currentTime + i * 0.06;

            osc.type = 'square';
            osc.frequency.setValueAtTime(freq, now);

            gain.gain.setValueAtTime(0.1, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now);
            osc.stop(now + 0.2);
        });
    }

    playGameOver() {
        if (this.isMuted) return;
        this.init();
        if (!this.ctx) return;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        const now = this.ctx.currentTime;

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(220, now);
        osc.frequency.exponentialRampToValueAtTime(40, now + 0.4);

        gain.gain.setValueAtTime(0.3, now);
        gain.gain.linearRampToValueAtTime(0.01, now + 0.4);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.4);
    }
}

// --- PARTICLE POOL SYSTEM ---
class ParticleSystem {
    constructor(maxParticles = 50) {
        this.pool = [];
        for (let i = 0; i < maxParticles; i++) {
            this.pool.push({
                x: 0,
                y: 0,
                vx: 0,
                vy: 0,
                color: '#fff',
                alpha: 0,
                size: 2,
                active: false
            });
        }
    }

    burst(x, y, color, count = 15) {
        let spawned = 0;
        for (let p of this.pool) {
            if (!p.active) {
                p.x = x;
                p.y = y;
                const angle = Math.random() * Math.PI * 2;
                const speed = 1 + Math.random() * 3;
                p.vx = Math.cos(angle) * speed;
                p.vy = Math.sin(angle) * speed;
                p.color = color;
                p.alpha = 1;
                p.size = 2 + Math.random() * 3;
                p.active = true;
                spawned++;
                if (spawned >= count) break;
            }
        }
    }

    update() {
        for (let p of this.pool) {
            if (p.active) {
                p.x += p.vx;
                p.y += p.vy;
                p.alpha -= 0.03;
                if (p.alpha <= 0) {
                    p.active = false;
                }
            }
        }
    }

    draw(ctx) {
        ctx.save();
        for (let p of this.pool) {
            if (p.active) {
                ctx.globalAlpha = Math.max(0, p.alpha);
                ctx.fillStyle = p.color;
                ctx.shadowColor = p.color;
                ctx.shadowBlur = 6;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }
        ctx.restore();
    }
}

// --- MAIN GAME ENGINE ---
class SnakeGame {
    constructor() {
        // DOM Elements
        this.canvas = document.getElementById('game-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.canvasWrapper = document.getElementById('canvas-wrapper');

        // HUD Elements
        this.scoreEl = document.getElementById('score-val');
        this.highScoreEl = document.getElementById('highscore-val');
        this.levelEl = document.getElementById('level-val');
        this.speedEl = document.getElementById('speed-val');

        // Overlays & Buttons
        this.startOverlay = document.getElementById('start-overlay');
        this.pauseOverlay = document.getElementById('pause-overlay');
        this.gameoverOverlay = document.getElementById('gameover-overlay');

        this.startBtn = document.getElementById('start-btn');
        this.pauseBtn = document.getElementById('pause-btn');
        this.restartBtn = document.getElementById('restart-btn');
        this.muteBtn = document.getElementById('mute-btn');
        this.muteIcon = document.getElementById('mute-icon');

        this.overlayStartBtn = document.getElementById('overlay-start-btn');
        this.overlayResumeBtn = document.getElementById('overlay-resume-btn');
        this.overlayRestartBtn = document.getElementById('overlay-restart-btn');

        // Audio & Particles
        this.sound = new SoundController();
        this.particles = new ParticleSystem(50);

        // State Machine
        this.state = 'IDLE'; // IDLE, RUNNING, PAUSED, GAME_OVER

        // Game Metrics
        this.score = 0;
        this.highScore = parseInt(localStorage.getItem(STORAGE_KEY_HIGH_SCORE) || '0', 10);
        this.level = 1;
        this.foodsEaten = 0;

        // Grid & Cell Dimension Calculation
        this.cellSize = 20;

        // Snake Representation
        this.snake = [];
        this.currentDir = DIR.RIGHT;
        this.inputQueue = [];

        // Food Schema
        this.standardFood = null;
        this.goldenFood = null; // { x, y, ticksRemaining }

        // Logic Loop Timer
        this.lastStepTime = 0;
        this.stepInterval = 150; // ms

        this.initCanvasDPI();
        this.bindEvents();
        this.updateHUD();
        this.updateMuteIcon();

        // Start render loop
        requestAnimationFrame((ts) => this.loop(ts));
    }

    initCanvasDPI() {
        const dpr = window.devicePixelRatio || 1;
        const rect = this.canvas.getBoundingClientRect();
        const displayWidth = rect.width || 400;
        const displayHeight = rect.height || 400;

        this.canvas.width = displayWidth * dpr;
        this.canvas.height = displayHeight * dpr;
        this.ctx.scale(dpr, dpr);

        this.cellSize = displayWidth / GRID_SIZE;
    }

    updateMuteIcon() {
        this.muteIcon.textContent = this.sound.isMuted ? '🔇' : '🔊';
    }

    resetGame() {
        this.score = 0;
        this.level = 1;
        this.foodsEaten = 0;
        this.stepInterval = 150;
        this.currentDir = DIR.RIGHT;
        this.inputQueue = [];

        // Initial Snake Head at center (10, 10) with 3 segments extending left
        this.snake = [
            { x: 10, y: 10 },
            { x: 9, y: 10 },
            { x: 8, y: 10 }
        ];

        this.goldenFood = null;
        this.spawnStandardFood();
        this.updateHUD();
    }

    spawnStandardFood() {
        let x, y, collision;
        do {
            collision = false;
            x = Math.floor(Math.random() * GRID_SIZE);
            y = Math.floor(Math.random() * GRID_SIZE);

            for (let segment of this.snake) {
                if (segment.x === x && segment.y === y) {
                    collision = true;
                    break;
                }
            }
            if (this.goldenFood && this.goldenFood.x === x && this.goldenFood.y === y) {
                collision = true;
            }
        } while (collision);

        this.standardFood = { x, y };
    }

    spawnGoldenFood() {
        let x, y, collision;
        do {
            collision = false;
            x = Math.floor(Math.random() * GRID_SIZE);
            y = Math.floor(Math.random() * GRID_SIZE);

            for (let segment of this.snake) {
                if (segment.x === x && segment.y === y) {
                    collision = true;
                    break;
                }
            }
            if (this.standardFood && this.standardFood.x === x && this.standardFood.y === y) {
                collision = true;
            }
        } while (collision);

        this.goldenFood = {
            x,
            y,
            ticksRemaining: 35 // Active for 35 ticks
        };
    }

    startGame() {
        this.sound.init();
        this.resetGame();
        this.state = 'RUNNING';

        this.startOverlay.classList.add('hidden');
        this.pauseOverlay.classList.add('hidden');
        this.gameoverOverlay.classList.add('hidden');

        this.startBtn.disabled = true;
        this.pauseBtn.disabled = false;
        this.pauseBtn.textContent = 'Pause';
    }

    togglePause() {
        if (this.state === 'RUNNING') {
            this.state = 'PAUSED';
            this.pauseOverlay.classList.remove('hidden');
            this.pauseBtn.textContent = 'Resume';
        } else if (this.state === 'PAUSED') {
            this.sound.init();
            this.state = 'RUNNING';
            this.pauseOverlay.classList.add('hidden');
            this.pauseBtn.textContent = 'Pause';
        }
    }

    restartGame() {
        this.sound.init();
        this.startGame();
    }

    gameOver() {
        this.state = 'GAME_OVER';
        this.sound.playGameOver();

        // Screen shake trigger
        this.canvasWrapper.classList.remove('shake');
        void this.canvasWrapper.offsetWidth; // trigger reflow
        this.canvasWrapper.classList.add('shake');

        const isNewHigh = this.score > this.highScore;
        if (isNewHigh) {
            this.highScore = this.score;
            localStorage.setItem(STORAGE_KEY_HIGH_SCORE, this.highScore.toString());
        }

        document.getElementById('final-score').textContent = this.score;
        document.getElementById('final-level').textContent = this.level;
        document.getElementById('final-highscore').textContent = this.highScore;

        const badge = document.getElementById('new-high-badge');
        if (isNewHigh && this.score > 0) {
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }

        this.pauseBtn.disabled = true;
        this.startBtn.disabled = false;
        this.gameoverOverlay.classList.remove('hidden');
        this.updateHUD();
    }

    // Input Buffer Queue Handling (Prevents double tap self-collisions)
    queueDirection(newDir) {
        if (this.state === 'IDLE') {
            this.startGame();
            return;
        }

        if (this.state !== 'RUNNING') return;

        const lastDir = this.inputQueue.length > 0 
            ? this.inputQueue[this.inputQueue.length - 1] 
            : this.currentDir;

        // Reject 180-degree immediate reversal
        if (newDir.x === -lastDir.x && newDir.y === -lastDir.y) {
            return;
        }

        if (this.inputQueue.length < 2) {
            this.inputQueue.push(newDir);
        }
    }

    bindEvents() {
        // Keyboard Listener
        window.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'ArrowUp':
                case 'w':
                case 'W':
                    e.preventDefault();
                    this.queueDirection(DIR.UP);
                    break;
                case 'ArrowDown':
                case 's':
                case 'S':
                    e.preventDefault();
                    this.queueDirection(DIR.DOWN);
                    break;
                case 'ArrowLeft':
                case 'a':
                case 'A':
                    e.preventDefault();
                    this.queueDirection(DIR.LEFT);
                    break;
                case 'ArrowRight':
                case 'd':
                case 'D':
                    e.preventDefault();
                    this.queueDirection(DIR.RIGHT);
                    break;
                case ' ':
                    e.preventDefault();
                    this.togglePause();
                    break;
                case 'r':
                case 'R':
                    e.preventDefault();
                    this.restartGame();
                    break;
            }
        });

        // Touch D-Pad Controls
        document.getElementById('btn-up').addEventListener('click', () => this.queueDirection(DIR.UP));
        document.getElementById('btn-down').addEventListener('click', () => this.queueDirection(DIR.DOWN));
        document.getElementById('btn-left').addEventListener('click', () => this.queueDirection(DIR.LEFT));
        document.getElementById('btn-right').addEventListener('click', () => this.queueDirection(DIR.RIGHT));

        // Action Buttons
        this.startBtn.addEventListener('click', () => this.startGame());
        this.pauseBtn.addEventListener('click', () => this.togglePause());
        this.restartBtn.addEventListener('click', () => this.restartGame());

        this.overlayStartBtn.addEventListener('click', () => this.startGame());
        this.overlayResumeBtn.addEventListener('click', () => this.togglePause());
        this.overlayRestartBtn.addEventListener('click', () => this.restartGame());

        this.muteBtn.addEventListener('click', () => {
            const isMuted = this.sound.toggleMute();
            this.updateMuteIcon();
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.initCanvasDPI();
        });
    }

    // Main Logic Step Tick
    step() {
        if (this.inputQueue.length > 0) {
            this.currentDir = this.inputQueue.shift();
        }

        const head = this.snake[0];
        const newHead = {
            x: head.x + this.currentDir.x,
            y: head.y + this.currentDir.y
        };

        // Wall Collision Check
        if (newHead.x < 0 || newHead.x >= GRID_SIZE || newHead.y < 0 || newHead.y >= GRID_SIZE) {
            this.gameOver();
            return;
        }

        // Self Collision Check
        for (let i = 0; i < this.snake.length; i++) {
            if (this.snake[i].x === newHead.x && this.snake[i].y === newHead.y) {
                this.gameOver();
                return;
            }
        }

        // Move Snake
        this.snake.unshift(newHead);

        let ateFood = false;
        const pixelX = (newHead.x + 0.5) * this.cellSize;
        const pixelY = (newHead.y + 0.5) * this.cellSize;

        // Check Standard Food Eating
        if (this.standardFood && newHead.x === this.standardFood.x && newHead.y === this.standardFood.y) {
            ateFood = true;
            this.foodsEaten++;
            this.score += 10 * this.level;
            this.sound.playEatStandard();
            this.particles.burst(pixelX, pixelY, '#ff0055', 15);

            this.spawnStandardFood();

            // Spawn Golden Food every 5 foods
            if (this.foodsEaten % 5 === 0 && !this.goldenFood) {
                this.spawnGoldenFood();
            }

            // Check Level Progression & Speed Scaling
            const nextLevel = 1 + Math.floor(this.foodsEaten / 5);
            if (nextLevel > this.level) {
                this.level = nextLevel;
                this.sound.playLevelUp();
                // Speed increases by 15ms per level down to 50ms min
                this.stepInterval = Math.max(50, 150 - (this.level - 1) * 15);
            }

            this.updateHUD();
        }

        // Check Golden Food Eating
        if (this.goldenFood && newHead.x === this.goldenFood.x && newHead.y === this.goldenFood.y) {
            ateFood = true;
            this.score += 30 * this.level;
            this.sound.playEatGolden();
            this.particles.burst(pixelX, pixelY, '#ffd700', 25);
            this.goldenFood = null;
            this.updateHUD();
        }

        // If no food ate, remove tail segment
        if (!ateFood) {
            this.snake.pop();
        }

        // Update Golden Food Timer
        if (this.goldenFood) {
            this.goldenFood.ticksRemaining--;
            if (this.goldenFood.ticksRemaining <= 0) {
                this.goldenFood = null;
            }
        }
    }

    updateHUD() {
        this.scoreEl.textContent = this.score;
        this.highScoreEl.textContent = Math.max(this.score, this.highScore);
        this.levelEl.textContent = this.level;

        // Calculate speed multiplier percentage (base 150ms = 100%)
        const speedPercent = Math.round((150 / this.stepInterval) * 100);
        this.speedEl.textContent = `${speedPercent}%`;
    }

    // Rendering Pipeline
    render() {
        const ctx = this.ctx;
        const cs = this.cellSize;

        // Clear canvas
        ctx.clearRect(0, 0, GRID_SIZE * cs, GRID_SIZE * cs);

        // Render Subtle Background Grid
        ctx.strokeStyle = 'rgba(0, 243, 255, 0.04)';
        ctx.lineWidth = 1;
        for (let i = 0; i <= GRID_SIZE; i++) {
            ctx.beginPath();
            ctx.moveTo(i * cs, 0);
            ctx.lineTo(i * cs, GRID_SIZE * cs);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(0, i * cs);
            ctx.lineTo(GRID_SIZE * cs, i * cs);
            ctx.stroke();
        }

        // Render Standard Food (Neon Magenta Pulsing Apple)
        if (this.standardFood) {
            const fx = (this.standardFood.x + 0.5) * cs;
            const fy = (this.standardFood.y + 0.5) * cs;
            const radius = (cs / 2) * 0.75;
            const pulse = Math.sin(Date.now() / 150) * 1.5;

            ctx.save();
            ctx.shadowColor = '#ff0055';
            ctx.shadowBlur = 12 + pulse;
            ctx.fillStyle = '#ff0055';
            ctx.beginPath();
            ctx.arc(fx, fy, radius + pulse * 0.5, 0, Math.PI * 2);
            ctx.fill();

            // Inner Highlight
            ctx.fillStyle = '#ffb3d1';
            ctx.beginPath();
            ctx.arc(fx - radius * 0.3, fy - radius * 0.3, radius * 0.3, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }

        // Render Golden Food (Glowing Gold Star + Countdown Ring)
        if (this.goldenFood) {
            const gx = (this.goldenFood.x + 0.5) * cs;
            const gy = (this.goldenFood.y + 0.5) * cs;
            const radius = (cs / 2) * 0.8;
            const progress = this.goldenFood.ticksRemaining / 35;

            ctx.save();
            // Golden Glow
            ctx.shadowColor = '#ffd700';
            ctx.shadowBlur = 15;
            ctx.fillStyle = '#ffd700';

            // Diamond Star Shape
            ctx.beginPath();
            ctx.moveTo(gx, gy - radius);
            ctx.lineTo(gx + radius * 0.8, gy);
            ctx.lineTo(gx, gy + radius);
            ctx.lineTo(gx - radius * 0.8, gy);
            ctx.closePath();
            ctx.fill();

            // Timer Countdown Ring
            ctx.strokeStyle = '#ffd700';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(gx, gy, radius * 1.2, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * progress);
            ctx.stroke();
            ctx.restore();
        }

        // Render Snake Body & Head
        for (let i = this.snake.length - 1; i >= 0; i--) {
            const seg = this.snake[i];
            const px = seg.x * cs;
            const py = seg.y * cs;
            const isHead = (i === 0);

            ctx.save();
            if (isHead) {
                // Head Styling
                ctx.fillStyle = '#00f3ff';
                ctx.shadowColor = '#00f3ff';
                ctx.shadowBlur = 12;

                ctx.beginPath();
                ctx.roundRect(px + 1, py + 1, cs - 2, cs - 2, 6);
                ctx.fill();

                // Snake Eyes
                ctx.fillStyle = '#05050a';
                const eyeSize = cs * 0.15;
                let eye1X = px + cs * 0.3, eye1Y = py + cs * 0.3;
                let eye2X = px + cs * 0.7, eye2Y = py + cs * 0.3;

                if (this.currentDir === DIR.DOWN) {
                    eye1Y = py + cs * 0.7; eye2Y = py + cs * 0.7;
                } else if (this.currentDir === DIR.LEFT) {
                    eye1X = px + cs * 0.3; eye1Y = py + cs * 0.3;
                    eye2X = px + cs * 0.3; eye2Y = py + cs * 0.7;
                } else if (this.currentDir === DIR.RIGHT) {
                    eye1X = px + cs * 0.7; eye1Y = py + cs * 0.3;
                    eye2X = px + cs * 0.7; eye2Y = py + cs * 0.7;
                }

                ctx.beginPath();
                ctx.arc(eye1X, eye1Y, eyeSize, 0, Math.PI * 2);
                ctx.arc(eye2X, eye2Y, eyeSize, 0, Math.PI * 2);
                ctx.fill();
            } else {
                // Gradient Cyan-to-Purple Tail
                const ratio = i / this.snake.length;
                ctx.fillStyle = `hsl(${180 + ratio * 80}, 100%, 50%)`;
                ctx.shadowColor = '#00f3ff';
                ctx.shadowBlur = Math.max(0, 8 - i * 0.5);

                ctx.beginPath();
                ctx.roundRect(px + 2, py + 2, cs - 4, cs - 4, 4);
                ctx.fill();
            }
            ctx.restore();
        }

        // Render Particle System Effects
        this.particles.update();
        this.particles.draw(ctx);
    }

    // Frame Game Loop
    loop(timestamp) {
        if (!this.lastStepTime) this.lastStepTime = timestamp;

        if (this.state === 'RUNNING') {
            const delta = timestamp - this.lastStepTime;
            if (delta >= this.stepInterval) {
                this.step();
                this.lastStepTime = timestamp;
            }
        }

        this.render();
        requestAnimationFrame((ts) => this.loop(ts));
    }
}

// Initialize Game Engine on DOM Loaded
window.addEventListener('DOMContentLoaded', () => {
    window.gameEngine = new SnakeGame();
});
