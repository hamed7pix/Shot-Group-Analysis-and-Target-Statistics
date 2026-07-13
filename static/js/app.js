const canvas = document.getElementById('targetCanvas');
const ctx = canvas.getContext('2d');
const histoCanvas = document.getElementById('histoCanvas');
const histoCtx = histoCanvas.getContext('2d');

let shots = [];
let targetMetrics = null;

const TARGET_CENTER_X = 240;
const TARGET_CENTER_Y = 240;
const OUTER_RING_RADIUS_PX = 220;

function drawTarget() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const xc = TARGET_CENTER_X;
    const yc = TARGET_CENTER_Y;
    const outerR = OUTER_RING_RADIUS_PX;
    const step = outerR / 10;

    // Draw rings
    for (let i = 1; i <= 10; i++) {
        const r = outerR - (i - 1) * step;
        ctx.beginPath();
        ctx.arc(xc, yc, r, 0, 2 * Math.PI);

        if (i >= 7) {
            ctx.fillStyle = '#232323';
            ctx.fill();
            ctx.strokeStyle = i === 7 ? '#555555' : 'white';
        } else {
            ctx.fillStyle = '#F5E2C2';
            ctx.fill();
            ctx.strokeStyle = '#232323';
        }
        ctx.lineWidth = 1;
        ctx.stroke();
    }

    // X-Ring
    const rx = step * 0.25;
    ctx.beginPath();
    ctx.arc(xc, yc, rx, 0, 2 * Math.PI);
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 0.8;
    ctx.setLineDash([3, 3]);
    ctx.stroke();
    ctx.setLineDash([]);

    // Guidelines
    ctx.beginPath();
    ctx.moveTo(xc - outerR, yc);
    ctx.lineTo(xc + outerR, yc);
    ctx.moveTo(xc, yc - outerR);
    ctx.lineTo(xc, yc + outerR);
    ctx.strokeStyle = '#4A4A4A';
    ctx.lineWidth = 0.5;
    ctx.setLineDash([4, 4]);
    ctx.stroke();
    ctx.setLineDash([]);

    // Labels
    ctx.font = 'bold 9px Helvetica';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    for (let i = 1; i <= 8; i++) {
        const rMid = outerR - (i - 0.5) * step;
        const color = i >= 7 ? 'white' : '#232323';
        ctx.fillStyle = color;

        ctx.fillText(i.toString(), xc - rMid, yc);
        ctx.fillText(i.toString(), xc + rMid, yc);
        ctx.fillText(i.toString(), xc, yc - rMid);
        ctx.fillText(i.toString(), xc, yc + rMid);
    }
}

function getShotRadiusPx() {
    const tDia = parseFloat(document.getElementById('dia-entry').value) || 155.5;
    const sDia = parseFloat(document.getElementById('shot-dia-entry').value) || 4.5;
    const mmPerPx = (tDia / 2.0) / OUTER_RING_RADIUS_PX;
    return Math.max(2.0, (sDia / 2.0) / mmPerPx);
}

function drawShotsAndCentroid() {
    drawTarget();

    if (shots.length === 0) return;

    const r = getShotRadiusPx();

    // Draw shots
    shots.forEach(shot => {
        ctx.beginPath();
        ctx.arc(shot.x, shot.y, r, 0, 2 * Math.PI);
        ctx.fillStyle = '#2196F3';
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = '#0D47A1';
        ctx.stroke();
    });

    if (targetMetrics && targetMetrics.centroid && shots.length > 0) {
        const cx = targetMetrics.centroid.x;
        const cy = targetMetrics.centroid.y;

        // Draw crosshair
        ctx.beginPath();
        ctx.moveTo(cx - 5, cy);
        ctx.lineTo(cx + 5, cy);
        ctx.moveTo(cx, cy - 5);
        ctx.lineTo(cx, cy + 5);
        ctx.strokeStyle = '#E53935';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Draw Mean Radius
        if (shots.length >= 2 && targetMetrics.mean_radius_px) {
            ctx.beginPath();
            ctx.arc(cx, cy, targetMetrics.mean_radius_px, 0, 2 * Math.PI);
            ctx.strokeStyle = '#E53935';
            ctx.lineWidth = 1.5;
            ctx.setLineDash([4, 2]);
            ctx.stroke();
            ctx.setLineDash([]);
        }
    }
}

function drawHistogram(distribution) {
    histoCtx.clearRect(0, 0, histoCanvas.width, histoCanvas.height);

    const categories = ["X", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1"];
    const counts = categories.map(c => distribution[c] || 0);
    const maxCount = Math.max(...counts, 1);

    const canvasW = 480;
    const colCount = categories.length;
    const colWidth = canvasW / colCount;

    categories.forEach((cat, i) => {
        const count = counts[i];
        const x0 = i * colWidth + 4;
        const width = colWidth - 8;

        const barHeight = count > 0 ? (count / maxCount) * 45 : 2;
        const y0 = 60 - barHeight;

        histoCtx.fillStyle = count > 0 ? '#212121' : '#E0E0E0';
        histoCtx.fillRect(x0, y0, width, barHeight);

        // Count Text
        histoCtx.fillStyle = count > 0 ? '#111111' : '#888888';
        histoCtx.font = count > 0 ? 'bold 11px Helvetica' : '10px Helvetica';
        histoCtx.textAlign = 'center';
        histoCtx.fillText(count > 0 ? count.toString() : '—', x0 + width/2, 75);

        // Category Label
        histoCtx.fillStyle = '#666666';
        histoCtx.font = '10px Helvetica';
        histoCtx.fillText(cat, x0 + width/2, 95);
    });
}

async function calculateMetrics() {
    const tDia = parseFloat(document.getElementById('dia-entry').value) || 155.5;
    const sDia = parseFloat(document.getElementById('shot-dia-entry').value) || 4.5;

    const payload = {
        shots: shots,
        target_diameter_mm: tDia,
        shot_diameter_mm: sDia,
        outer_ring_radius_px: OUTER_RING_RADIUS_PX,
        target_center_x: TARGET_CENTER_X,
        target_center_y: TARGET_CENTER_Y
    };

    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        targetMetrics = await response.json();

        // Update DOM
        document.getElementById('score-label').textContent = targetMetrics.score;
        document.getElementById('windage-val').textContent = targetMetrics.windage;
        document.getElementById('elevation-val').textContent = targetMetrics.elevation;
        document.getElementById('mean-radius-val').textContent = targetMetrics.mean_radius;
        document.getElementById('max-spread-val').textContent = targetMetrics.max_spread;

        const listbox = document.getElementById('shot-listbox');
        listbox.innerHTML = '';
        targetMetrics.shot_log.forEach((logStr, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = logStr;
            listbox.appendChild(option);
        });

        drawHistogram(targetMetrics.distribution);
        drawShotsAndCentroid();
    } catch (err) {
        console.error("Error calculating metrics:", err);
    }
}

// Event Listeners
canvas.addEventListener('mousedown', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const dist = Math.sqrt(Math.pow(x - TARGET_CENTER_X, 2) + Math.pow(y - TARGET_CENTER_Y, 2));
    if (dist <= OUTER_RING_RADIUS_PX + 10) {
        shots.push({x, y});
        calculateMetrics();
    }
});

document.getElementById('btn-export').addEventListener('click', () => {
    if (shots.length === 0) {
        alert("There are no shots plotted to export.");
        return;
    }

    const tDia = parseFloat(document.getElementById('dia-entry').value) || 155.5;
    const mmPerPx = (tDia / 2.0) / OUTER_RING_RADIUS_PX;

    let csvContent = "data:text/csv;charset=utf-8,Shot Number,X_pixel,Y_pixel,X_mm,Y_mm\n";

    shots.forEach((shot, index) => {
        const dx_mm = (shot.x - TARGET_CENTER_X) * mmPerPx;
        const dy_mm = (TARGET_CENTER_Y - shot.y) * mmPerPx;
        csvContent += `${index + 1},${shot.x},${shot.y},${dx_mm.toFixed(2)},${dy_mm.toFixed(2)}\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "shot_log_data.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

document.getElementById('preset-combo').addEventListener('change', (e) => {
    const selectedOption = e.target.options[e.target.selectedIndex];
    document.getElementById('dia-entry').value = selectedOption.dataset.tdia;
    document.getElementById('shot-dia-entry').value = selectedOption.dataset.sdia;
    calculateMetrics();
});

document.getElementById('dia-entry').addEventListener('input', calculateMetrics);
document.getElementById('shot-dia-entry').addEventListener('input', calculateMetrics);

document.getElementById('btn-undo').addEventListener('click', () => {
    if (shots.length > 0) {
        shots.pop();
        calculateMetrics();
    }
});

document.getElementById('btn-clear').addEventListener('click', () => {
    if (confirm("Are you sure you want to clear all shots?")) {
        shots = [];
        calculateMetrics();
    }
});

document.getElementById('shot-listbox').addEventListener('dblclick', (e) => {
    if (e.target.tagName === 'OPTION') {
        const idx = parseInt(e.target.value);
        if (!isNaN(idx)) {
            shots.splice(idx, 1);
            calculateMetrics();
        }
    }
});

// Initial draw
drawTarget();
drawHistogram({"X":0, "10":0, "9":0, "8":0, "7":0, "6":0, "5":0, "4":0, "3":0, "2":0, "1":0});
