/* MAGI-Link document.js
 * Based on itorr/magi — core vote logic replaced with /api/analyze call
 */

let device = String(navigator.userAgent.match(/steam|macos/i)).toLowerCase();
if (
    /iPhone|iPad|iPod/i.test(navigator.userAgent) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
) device = 'ios';
document.documentElement.setAttribute('data-device', device);

const $  = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];

const finalVoteStatusEl = $('.final-vote-status');
const items   = $$('.magi-item');
const bodyEl  = document.body;
const questionEl = $('.question-input');

/* ── code ticker ── */
const randAll = _ => {
    $('.code').innerHTML = 100 + Math.floor(Math.random() * 600);
};

/* ── sound toggle ── */
let sound = true;
const soundEl = $('.sound');
soundEl.onclick = e => {
    e.stopPropagation();
    sound = !sound;
    soundEl.setAttribute('data-text', sound ? 'ON' : 'OFF');
};
soundEl.setAttribute('data-text', 'ON');

/* ── web audio ── */
let play = _ => { startWebAudio(); play(); };
let stopAll = _ => {};
let playOscillator = _ => {};

let audioCtx, osc, lfo, VCO, carrierVolume;
const AudioContextCtor = window.AudioContext || window.webkitAudioContext;

const loadAudio = _ => {
    audioCtx = new AudioContextCtor();
    carrierVolume = audioCtx.createGain();
    carrierVolume.gain.linearRampToValueAtTime(.5, 0);
    carrierVolume.connect(audioCtx.destination);
};

let startWebAudio = _ => {
    play = _ => {
        if (!audioCtx) loadAudio();
        osc = audioCtx.createOscillator();
        osc.type = 'sine';
        osc.frequency.value = 2080;
        lfo = audioCtx.createOscillator();
        lfo.type = 'square';
        lfo.frequency.value = exMode ? 30 : 10;
        lfo.connect(carrierVolume.gain);
        osc.connect(carrierVolume);
        lfo.start(0);
        osc.start(0);
    };
    playOscillator = (hz = 3400) => {
        if (!audioCtx) loadAudio();
        VCO = audioCtx.createOscillator();
        VCO.frequency.value = hz;
        VCO.connect(carrierVolume);
        VCO.start(0);
        VCO.stop(audioCtx.currentTime + .8);
    };
    stopAll = _ => {
        try { osc.stop(0); lfo.stop(0); } catch (e) {}
        try { VCO.stop(audioCtx.currentTime); } catch (e) {}
    };
};

document.addEventListener('visibilitychange', _ => {
    if (document.hidden) {
        stopAll();
        try { audioCtx.close(); audioCtx = null; } catch (e) {}
    }
});

if (!AudioContextCtor) soundEl.setAttribute('data-text', 'ERR');

/* ── volume ── */
let volume = 66;
const volumeEl = $('.volume');
const volumes  = [1, 10, 33, 50, 66, 90, 65535];
volumeEl.onclick = e => {
    e.stopPropagation();
    const idx = volumes.indexOf(volume);
    volume = volumes[(idx + 1) % volumes.length];
    volumeEl.setAttribute('data-text', volume);
};

/* ── priority ── */
const priorityEl = $('.priority');
let priority = 'AAA';
const prioritys = ['E', '+++', 'A', 'AA', 'AAA'];
priorityEl.onclick = e => {
    e.stopPropagation();
    const idx = prioritys.indexOf(priority);
    priority = prioritys[(idx + 1) % prioritys.length];
    priorityEl.setAttribute('data-text', priority);
};

/* ── ex mode ── */
let exMode = false;
const exModeEl = $('.ex-mode');
exModeEl.onclick = e => {
    e.stopPropagation();
    exMode = !exMode;
    bodyEl.setAttribute('data-ex-mode', exMode);
    exModeEl.setAttribute('data-text', exMode ? 'ON' : 'OFF');
};
exModeEl.setAttribute('data-text', 'OFF');

/* ── file name ── */
const fileEl = $('.file');
fileEl.onclick = e => {
    e.stopPropagation();
    fileEl.innerText = prompt('INPUT FILE', fileEl.innerText) || 'MAGI_SYS';
};

/* ── reset ── */
const doReset = _ => {
    bodyEl.removeAttribute('data-status');
    bodyEl.removeAttribute('data-vote-status');
    items.forEach(el => {
        el.removeAttribute('data-status');
        el.querySelector('h2').removeAttribute('data-summary');
    });
    finalVoteStatusEl.removeAttribute('data-status');
};
$('.reset').onclick = e => { e.stopPropagation(); doReset(); };
$('footer').onclick = e => e.stopPropagation();

/* ── extract first meaningful sentence from agent output ── */
const extractSummary = text => {
    const lines = text.split('\n')
        .map(l => l.trim())
        .filter(l => l && !l.match(/^【/) && !l.match(/^={3}/) && !l.match(/^▸/));
    const first = lines[0] || '';
    // strip leading list markers, keep ~18 chars
    return first.replace(/^[-•·＊*]\s*/, '').slice(0, 18);
};

/* ── parse verdict → per-panel statuses ── */
const parseVerdict = verdict => {
    // Default: all resolve
    const s = { melchior: 'resolve', malthasar: 'resolve', casper: 'resolve' };
    let finalStatus = 'resolve';
    let rejected = false;

    if (verdict.includes('全体一致通过')) {
        // All three agree: resolve
    } else if (verdict.includes('二比一通过')) {
        // CASPER-3 is the arbiter holding the dissenting opinion
        s.casper = 'reject';
    } else if (verdict.includes('否决') || verdict.includes('搁置')) {
        s.melchior = s.malthasar = s.casper = 'reject';
        finalStatus = 'reject';
        rejected = true;
    }

    return { statuses: s, finalStatus, rejected };
};

/* ── main activation ── */
const one = async _ => {
    const currentStatus = bodyEl.getAttribute('data-status');

    // If voted → reset on click (same as original)
    if (currentStatus === 'voted') { doReset(); return; }

    // Ignore while API call in progress
    if (currentStatus === 'voting') return;

    // Require question
    const question = questionEl ? questionEl.value.trim() : '';
    if (!question) {
        if (questionEl) {
            questionEl.classList.add('error');
            questionEl.focus();
            setTimeout(() => questionEl.classList.remove('error'), 500);
        }
        return;
    }

    // Enter voting state (starts flash animation)
    bodyEl.setAttribute('data-status', 'voting');
    if (sound) { stopAll(); play(); }
    randAll();

    try {
        const res = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();
        const { statuses, finalStatus, rejected } = parseVerdict(data.verdict || '');

        // Apply per-panel resolve/reject
        $('.melchior').setAttribute('data-status',  statuses.melchior);
        $('.malthasar').setAttribute('data-status', statuses.malthasar);
        $('.casper').setAttribute('data-status',    statuses.casper);

        // Set summary text shown inside each panel's h2 (via data-summary → CSS content:attr)
        $('.melchior  h2').setAttribute('data-summary', extractSummary(data.melchior));
        $('.malthasar h2').setAttribute('data-summary', extractSummary(data.balthasar));
        $('.casper    h2').setAttribute('data-summary', extractSummary(data.casper));

        finalVoteStatusEl.setAttribute('data-status', finalStatus);
        bodyEl.setAttribute('data-vote-status', finalStatus);
        bodyEl.setAttribute('data-status', 'voted');

        if (sound) { stopAll(); playOscillator(rejected ? 3400 : 2000); }

    } catch (err) {
        console.error('MAGI API error:', err);
        doReset();
        if (sound) stopAll();
    }
};

/* ── bind events ── */
randAll();
$('.magi-box').onclick = one;

window.onkeydown = e => {
    if (e.keyCode === 32 && e.target === document.body) {
        e.preventDefault();
        one();
    }
};

if (questionEl) {
    // Prevent click on input from triggering magi-box click
    questionEl.addEventListener('click',   e => e.stopPropagation());
    questionEl.addEventListener('keydown', e => {
        e.stopPropagation();
        if (e.key === 'Enter') one();
    });
}

const submitBtn = $('.question-btn');
if (submitBtn) {
    submitBtn.onclick = e => { e.stopPropagation(); one(); };
}

/* ── loading intro ── */
setTimeout(_ => { bodyEl.removeAttribute('data-loading'); }, 1000);
