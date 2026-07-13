from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

# Target presets
TARGET_PRESETS = {
    "10m Air Pistol (155.5 mm)": {"target_diameter": 155.5, "shot_diameter": 4.5},
    "10m Air Rifle (45.5 mm)": {"target_diameter": 45.5, "shot_diameter": 4.5},
    "50m Pistol (500.0 mm)": {"target_diameter": 500.0, "shot_diameter": 5.6},
    "Custom Target (300.0 mm)": {"target_diameter": 300.0, "shot_diameter": 4.5}
}

@app.route("/")
def index():
    return render_template("index.html", presets=TARGET_PRESETS)

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.json
    shots = data.get("shots", [])
    target_diameter_mm = float(data.get("target_diameter_mm", 155.5))
    shot_diameter_mm = float(data.get("shot_diameter_mm", 4.5))
    outer_ring_radius_px = float(data.get("outer_ring_radius_px", 220))
    target_center_x = float(data.get("target_center_x", 240))
    target_center_y = float(data.get("target_center_y", 240))

    if not shots:
        return jsonify({
            "score": "0-0x",
            "windage": "0.0 mm",
            "elevation": "0.0 mm",
            "mean_radius": "0.0 mm",
            "max_spread": "0.0 mm",
            "distribution": {str(k): 0 for k in ["X", 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]},
            "shot_log": [],
            "centroid": None,
            "mean_radius_px": None
        })

    mm_per_px = (target_diameter_mm / 2.0) / outer_ring_radius_px
    shot_radius_mm = shot_diameter_mm / 2.0

    shots_mm = []
    scores_distribution = {str(k): 0 for k in ["X", 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]}
    total_numerical_score = 0
    x_count = 0
    shot_log = []

    ring_step_mm = (target_diameter_mm / 2.0) / 10

    for idx, shot in enumerate(shots):
        px, py = shot["x"], shot["y"]
        dx_mm = (px - target_center_x) * mm_per_px
        dy_mm = (target_center_y - py) * mm_per_px  # inverted y axis
        dist_to_center_mm = math.sqrt(dx_mm**2 + dy_mm**2)
        shots_mm.append((dx_mm, dy_mm, dist_to_center_mm))

        ring_val = 0
        is_x = False
        nearest_shot_edge_mm = max(0.0, dist_to_center_mm - shot_radius_mm)
        x_ring_radius_mm = ring_step_mm * 0.25

        if nearest_shot_edge_mm <= x_ring_radius_mm:
            ring_val = 10
            is_x = True
            scores_distribution["X"] += 1
            x_count += 1
        else:
            for ring in range(10, 0, -1):
                outer_bound_mm = ring_step_mm * (11 - ring)
                if nearest_shot_edge_mm <= outer_bound_mm:
                    ring_val = ring
                    break

            if ring_val > 0:
                scores_distribution[str(ring_val)] += 1

        total_numerical_score += ring_val
        score_text = "X" if is_x else str(ring_val)
        shot_log.append(f"S{idx+1:02d}: R={score_text:<2} (X:{dx_mm:+.1f}, Y:{dy_mm:+.1f} mm)")

    n = len(shots)
    sum_x = sum([s[0] for s in shots_mm])
    sum_y = sum([s[1] for s in shots_mm])
    avg_x = sum_x / n
    avg_y = sum_y / n

    wind_dir = "→" if avg_x >= 0 else "←"
    windage = f"{wind_dir} {abs(avg_x):.1f} mm"

    elev_dir = "↑" if avg_y >= 0 else "↓"
    elevation = f"{elev_dir} {abs(avg_y):.1f} mm"

    distances_to_centroid = [math.sqrt((s[0] - avg_x)**2 + (s[1] - avg_y)**2) for s in shots_mm]
    mean_radius_mm = sum(distances_to_centroid) / n
    mean_radius = f"{mean_radius_mm:.1f} mm"

    # centroid px
    avg_px_x = sum([s["x"] for s in shots]) / n
    avg_px_y = sum([s["y"] for s in shots]) / n
    mean_r_px = mean_radius_mm / mm_per_px

    max_spread_mm = 0.0
    if n >= 2:
        for i in range(n):
            for j in range(i + 1, n):
                d = math.sqrt((shots_mm[i][0] - shots_mm[j][0])**2 + (shots_mm[i][1] - shots_mm[j][1])**2)
                if d > max_spread_mm:
                    max_spread_mm = d
    max_spread = f"{max_spread_mm:.1f} mm"

    return jsonify({
        "score": f"{total_numerical_score}-{x_count}x",
        "windage": windage,
        "elevation": elevation,
        "mean_radius": mean_radius,
        "max_spread": max_spread,
        "distribution": scores_distribution,
        "shot_log": shot_log,
        "centroid": {"x": avg_px_x, "y": avg_px_y},
        "mean_radius_px": mean_r_px
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
