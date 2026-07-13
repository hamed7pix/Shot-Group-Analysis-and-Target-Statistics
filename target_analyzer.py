import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
from datetime import datetime
import csv

class TargetAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shot Group Analysis & Target Statistics")
        self.root.geometry("800x800")
        self.root.resizable(False, False)
        self.root.configure(bg="#FAF6EE")

        # Color Palette
        self.COLORS = {
            "bg": "#FAF6EE",            # Light Warm Cream
            "target_beige": "#F5E2C2",  # Target Paper Color
            "target_black": "#232323",  # Inner target rings black
            "shot_blue": "#2196F3",     # Vibrant shot blue
            "shot_border": "#0D47A1",   # Dark blue border
            "red_indicator": "#E53935", # Centroid and group radius red
            "panel_grey": "#F1F1EF"     # Sidebar background
        }

        # App Variables
        self.shots = []  # List of tuples: (x_pixel, y_pixel)
        self.target_center = (240, 240) # Canvas center coordinates
        self.outer_ring_radius_px = 220 # Radius of 1-ring in pixels
        
        # Target presets (ISSF specs or Custom)
        self.target_presets = {
            "10m Air Pistol (155.5 mm)": {"target_diameter": 155.5, "shot_diameter": 4.5},
            "10m Air Rifle (45.5 mm)": {"target_diameter": 45.5, "shot_diameter": 4.5},
            "50m Pistol (500.0 mm)": {"target_diameter": 500.0, "shot_diameter": 5.6},
            "Custom Target (300.0 mm)": {"target_diameter": 300.0, "shot_diameter": 4.5}
        }
        self.selected_preset = tk.StringVar(value="10m Air Pistol (155.5 mm)")
        self.target_diameter_mm = tk.DoubleVar(value=155.5)
        self.shot_diameter_mm = tk.DoubleVar(value=4.5)

        self.setup_ui()
        self.draw_target()
        self.calculate_metrics()

    def setup_ui(self):
        # Main Layout: Two Columns (Left = Target UI, Right = Control Panel)
        main_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ================= LEFT COLUMN =================
        left_column = tk.Frame(main_frame, bg=self.COLORS["bg"])
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 1. Header Frame (Date and Live Score)
        header_frame = tk.Frame(left_column, bg=self.COLORS["bg"])
        header_frame.pack(fill=tk.X, pady=(0, 5))

        self.date_label = tk.Label(
            header_frame, 
            text=datetime.today().strftime('%d/%m/%Y'), 
            font=("Helvetica", 18, "bold"), 
            fg="#4A4A4A", 
            bg=self.COLORS["bg"]
        )
        self.date_label.pack(side=tk.LEFT)

        self.score_label = tk.Label(
            header_frame, 
            text="0-0x", 
            font=("Helvetica", 20, "bold"), 
            fg="#1A1A1A", 
            bg=self.COLORS["bg"]
        )
        self.score_label.pack(side=tk.RIGHT)

        # 2. Target Canvas
        self.canvas = tk.Canvas(
            left_column, 
            width=480, 
            height=480, 
            bg=self.COLORS["target_beige"], 
            highlightthickness=1, 
            highlightbackground="#D1C1A5"
        )
        self.canvas.pack(pady=5)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # 3. Stats Panel
        stats_frame = tk.Frame(left_column, bg=self.COLORS["bg"])
        stats_frame.pack(fill=tk.X, pady=10)

        # Columns for windage, elevation, radius, and spread
        lbl_style = {"font": ("Helvetica", 14), "bg": self.COLORS["bg"], "fg": "#424242", "anchor": "w"}
        val_style = {"font": ("Helvetica", 15, "bold"), "bg": self.COLORS["bg"], "fg": "#1A1A1A", "anchor": "w"}

        # Column 1
        col1 = tk.Frame(stats_frame, bg=self.COLORS["bg"])
        col1.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(col1, text="Windage:", **lbl_style).grid(row=0, column=0, sticky="w", pady=2)
        self.windage_val = tk.Label(col1, text="0.0 mm", **val_style)
        self.windage_val.grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(col1, text="Elevation:", **lbl_style).grid(row=1, column=0, sticky="w", pady=2)
        self.elevation_val = tk.Label(col1, text="0.0 mm", **val_style)
        self.elevation_val.grid(row=1, column=1, sticky="w", padx=5)

        # Column 2
        col2 = tk.Frame(stats_frame, bg=self.COLORS["bg"])
        col2.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        tk.Label(col2, text="Mean radius:", **lbl_style).grid(row=0, column=0, sticky="w", pady=2)
        self.mean_radius_val = tk.Label(col2, text="0.0 mm", **val_style)
        self.mean_radius_val.grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(col2, text="Max spread:", **lbl_style).grid(row=1, column=0, sticky="w", pady=2)
        self.max_spread_val = tk.Label(col2, text="0.0 mm", **val_style)
        self.max_spread_val.grid(row=1, column=1, sticky="w", padx=5)

        # 4. Score Sheet Histogram Canvas
        self.histo_canvas = tk.Canvas(
            left_column, 
            width=480, 
            height=120, 
            bg=self.COLORS["bg"], 
            highlightthickness=0
        )
        self.histo_canvas.pack(fill=tk.X, pady=(5, 0))

        # ================= RIGHT COLUMN (CONTROLS) =================
        right_column = tk.Frame(main_frame, width=280, bg=self.COLORS["panel_grey"], bd=1, relief=tk.SOLID)
        right_column.pack_propagate(False)
        right_column.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))

        # Header Control Panel
        tk.Label(
            right_column, 
            text="CONTROL CENTER", 
            font=("Helvetica", 12, "bold"), 
            bg="#37474F", 
            fg="white", 
            pady=8
        ).pack(fill=tk.X)

        # Section 1: Target calibration settings
        settings_frame = tk.LabelFrame(
            right_column, 
            text=" Target Setup & Calibration ", 
            font=("Helvetica", 10, "bold"), 
            bg=self.COLORS["panel_grey"], 
            pady=10, 
            padx=10
        )
        settings_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(settings_frame, text="Target Standard:", bg=self.COLORS["panel_grey"]).pack(anchor="w")
        self.preset_combo = ttk.Combobox(
            settings_frame, 
            textvariable=self.selected_preset, 
            values=list(self.target_presets.keys()), 
            state="readonly"
        )
        self.preset_combo.pack(fill=tk.X, pady=(2, 10))
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_change)

        tk.Label(settings_frame, text="Outer Ring Diameter (mm):", bg=self.COLORS["panel_grey"]).pack(anchor="w")
        self.dia_entry = ttk.Entry(settings_frame, textvariable=self.target_diameter_mm)
        self.dia_entry.pack(fill=tk.X, pady=(2, 5))
        self.dia_entry.bind("<KeyRelease>", lambda e: self.refresh_after_calibration_change())

        tk.Label(settings_frame, text="Shot / Pellet Diameter (mm):", bg=self.COLORS["panel_grey"]).pack(anchor="w", pady=(7, 0))
        self.shot_dia_entry = ttk.Entry(settings_frame, textvariable=self.shot_diameter_mm)
        self.shot_dia_entry.pack(fill=tk.X, pady=(2, 5))
        self.shot_dia_entry.bind("<KeyRelease>", lambda e: self.refresh_after_calibration_change())

        # Section 2: Command Actions
        btn_frame = tk.Frame(right_column, bg=self.COLORS["panel_grey"])
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 10))

        self.btn_calc = ttk.Button(btn_frame, text="Calculate Statistics", command=self.calculate_metrics)
        self.btn_calc.pack(fill=tk.X, pady=3)

        self.btn_undo = ttk.Button(btn_frame, text="Undo Last Shot", command=self.undo_last_shot)
        self.btn_undo.pack(fill=tk.X, pady=3)

        self.btn_clear = ttk.Button(btn_frame, text="Clear Target", command=self.clear_all)
        self.btn_clear.pack(fill=tk.X, pady=3)

        self.btn_export = ttk.Button(btn_frame, text="Export CSV Data", command=self.export_csv)
        self.btn_export.pack(fill=tk.X, pady=3)

        # Section 3: Shot Coordinate Table (Coordinates visualizer)
        table_frame = tk.LabelFrame(
            right_column, 
            text=" Shot Log ", 
            font=("Helvetica", 10, "bold"), 
            bg=self.COLORS["panel_grey"]
        )
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.shot_listbox = tk.Listbox(
            table_frame, 
            font=("Courier", 9), 
            selectmode=tk.SINGLE, 
            highlightthickness=0
        )
        self.shot_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.shot_listbox.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.shot_listbox.config(yscrollcommand=scrollbar.set)
        
        # Double click log item to delete it
        self.shot_listbox.bind("<Double-Button-1>", self.delete_selected_shot)

        # User helper instructions on bottom
        tk.Label(
            right_column, 
            text="Tip: Left-click on target to shoot.\nDouble-click a shot log row to delete it.", 
            font=("Helvetica", 8, "italic"), 
            bg=self.COLORS["panel_grey"], 
            fg="#555555"
        ).pack(side=tk.BOTTOM, pady=10)

    # ================= TARGET GRAPHICS =================
    def draw_target(self):
        self.canvas.delete("all")
        xc, yc = self.target_center
        outer_r = self.outer_ring_radius_px

        # Spacing of 10 rings inside
        step = outer_r / 10

        # Draw ring zones
        for i in range(1, 11):
            r = outer_r - (i - 1) * step
            
            # Rings 7, 8, 9, 10, X are black
            if i >= 7:
                fill_col = self.COLORS["target_black"]
                line_col = "#555555" if i == 7 else "white"
            else:
                fill_col = self.COLORS["target_beige"]
                line_col = "#232323"

            self.canvas.create_oval(
                xc - r, yc - r, xc + r, yc + r, 
                fill=fill_col, outline=line_col, width=1
            )

        # Draw X-Ring (half size of ring 10)
        rx = step * 0.25
        self.canvas.create_oval(
            xc - rx, yc - rx, xc + rx, yc + rx, 
            fill="", outline="white", width=0.8, dash=(3, 3)
        )

        # Horizontal and vertical target guidelines
        self.canvas.create_line(xc - outer_r, yc, xc + outer_r, yc, fill="#4A4A4A", width=0.5, dash=(4, 4))
        self.canvas.create_line(xc, yc - outer_r, xc, yc + outer_r, fill="#4A4A4A", width=0.5, dash=(4, 4))

        # Write Ring Labels (1 to 8)
        label_font = ("Helvetica", 9, "bold")
        for i in range(1, 9):
            # Positional offset for label midpoints
            r_mid = outer_r - (i - 0.5) * step
            color = "white" if i >= 7 else "#232323"
            
            # Left & Right Labels
            self.canvas.create_text(xc - r_mid, yc, text=str(i), fill=color, font=label_font)
            self.canvas.create_text(xc + r_mid, yc, text=str(i), fill=color, font=label_font)
            # Top & Bottom Labels
            self.canvas.create_text(xc, yc - r_mid, text=str(i), fill=color, font=label_font)
            self.canvas.create_text(xc, yc + r_mid, text=str(i), fill=color, font=label_font)

    def draw_shots_and_centroid(self):
        # Clear dynamically drawn overlays (shots and helper guides)
        self.canvas.delete("overlay")

        if not self.shots:
            return

        # 1. Plot shots (blue dots)
        shot_radius_px = self.get_shot_radius_px()
        for idx, (x, y) in enumerate(self.shots):
            r = shot_radius_px
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=self.COLORS["shot_blue"], 
                outline=self.COLORS["shot_border"], 
                width=1.5, tags="overlay"
            )

        # 2. Render dispersion stats visually (if there is at least one shot)
        n = len(self.shots)
        avg_x = sum([p[0] for p in self.shots]) / n
        avg_y = sum([p[1] for p in self.shots]) / n

        # Draw Centroid Crosshair "+"
        cross_size = 5
        self.canvas.create_line(avg_x - cross_size, avg_y, avg_x + cross_size, avg_y, fill=self.COLORS["red_indicator"], width=2, tags="overlay")
        self.canvas.create_line(avg_x, avg_y - cross_size, avg_x, avg_y + cross_size, fill=self.COLORS["red_indicator"], width=2, tags="overlay")

        # Draw Mean Radius circle centered at centroid
        if n >= 2:
            distances = [math.sqrt((p[0] - avg_x)**2 + (p[1] - avg_y)**2) for p in self.shots]
            mean_r_px = sum(distances) / n
            self.canvas.create_oval(
                avg_x - mean_r_px, avg_y - mean_r_px, 
                avg_x + mean_r_px, avg_y + mean_r_px,
                outline=self.COLORS["red_indicator"], 
                width=1.5, dash=(4, 2), tags="overlay"
            )

    # ================= CALCULATIONS =================
    def on_canvas_click(self, event):
        # Click on target canvas limits
        xc, yc = self.target_center
        dist = math.sqrt((event.x - xc)**2 + (event.y - yc)**2)
        if dist <= self.outer_ring_radius_px + 10:  # Allow small margin outside Ring 1
            self.shots.append((event.x, event.y))
            self.draw_shots_and_centroid()
            self.calculate_metrics()

    def get_mm_per_pixel(self):
        # Outer ring 1 radius is 220 pixels.
        outer_radius_mm = self.target_diameter_mm.get() / 2.0
        return outer_radius_mm / self.outer_ring_radius_px

    def get_shot_radius_px(self):
        """Return the physical shot radius in canvas pixels."""
        try:
            mm_per_px = self.get_mm_per_pixel()
            shot_radius_mm = self.shot_diameter_mm.get() / 2.0
            return max(2.0, shot_radius_mm / mm_per_px)
        except (tk.TclError, ZeroDivisionError):
            return 6.0

    def refresh_after_calibration_change(self):
        """Refresh shot size and all values after a calibration edit."""
        try:
            if self.target_diameter_mm.get() <= 0 or self.shot_diameter_mm.get() <= 0:
                return
        except tk.TclError:
            return
        self.draw_shots_and_centroid()
        self.calculate_metrics()

    def calculate_metrics(self):
        n = len(self.shots)
        try:
            mm_per_px = self.get_mm_per_pixel()
            shot_radius_mm = self.shot_diameter_mm.get() / 2.0
            if mm_per_px <= 0 or shot_radius_mm <= 0:
                return
        except (tk.TclError, ZeroDivisionError):
            return
        xc, yc = self.target_center

        # Clear and update shot table listbox
        self.shot_listbox.delete(0, tk.END)

        if n == 0:
            self.score_label.config(text="0-0x")
            self.windage_val.config(text="0.0 mm")
            self.elevation_val.config(text="0.0 mm")
            self.mean_radius_val.config(text="0.0 mm")
            self.max_spread_val.config(text="0.0 mm")
            self.draw_histogram({k: 0 for k in ["X", 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]})
            return

        # Compute shot coordinates relative to center in millimeters
        # Standard target: +x is right, +y is up
        shots_mm = []
        scores_distribution = {k: 0 for k in ["X", 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]}
        total_numerical_score = 0
        x_count = 0

        # Ring definitions based on ISSF proportions:
        # Ring 10 radius is 1/10th of outer radius. X-ring radius is 1/20th of outer radius.
        ring_step_mm = (self.target_diameter_mm.get() / 2.0) / 10

        for idx, (px, py) in enumerate(self.shots):
            dx_mm = (px - xc) * mm_per_px
            dy_mm = (yc - py) * mm_per_px  # inverted vertical screen axis
            dist_to_center_mm = math.sqrt(dx_mm**2 + dy_mm**2)
            shots_mm.append((dx_mm, dy_mm, dist_to_center_mm))

            # Score classification by the gauge rule.
            # A shot receives the higher value when any part of its hole
            # touches or crosses that scoring ring. Therefore, the nearest
            # edge of the shot hole, rather than only its centre, is tested.
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
                    scores_distribution[ring_val] += 1
                
            total_numerical_score += ring_val
            
            # Format and insert to Shot list log
            score_text = "X" if is_x else str(ring_val)
            self.shot_listbox.insert(
                tk.END, 
                f"S{idx+1:02d}: R={score_text:<2} (X:{dx_mm:+.1f}, Y:{dy_mm:+.1f} mm)"
            )

        # Update Live Score Header
        self.score_label.config(text=f"{total_numerical_score}-{x_count}x")

        # Centroid / Group offset calculations
        sum_x = sum([s[0] for s in shots_mm])
        sum_y = sum([s[1] for s in shots_mm])
        avg_x = sum_x / n
        avg_y = sum_y / n

        # Windage label output
        wind_dir = "→" if avg_x >= 0 else "←"
        self.windage_val.config(text=f"{wind_dir} {abs(avg_x):.1f} mm")

        # Elevation label output
        elev_dir = "↑" if avg_y >= 0 else "↓"
        self.elevation_val.config(text=f"{elev_dir} {abs(avg_y):.1f} mm")

        # Mean Radius (MR)
        distances_to_centroid = [math.sqrt((s[0] - avg_x)**2 + (s[1] - avg_y)**2) for s in shots_mm]
        mean_radius_mm = sum(distances_to_centroid) / n
        self.mean_radius_val.config(text=f"{mean_radius_mm:.1f} mm")

        # Extreme Spread (Max Spread)
        if n >= 2:
            max_spread_mm = 0.0
            for i in range(n):
                for j in range(i + 1, n):
                    d = math.sqrt((shots_mm[i][0] - shots_mm[j][0])**2 + (shots_mm[i][1] - shots_mm[j][1])**2)
                    if d > max_spread_mm:
                        max_spread_mm = d
            self.max_spread_val.config(text=f"{max_spread_mm:.1f} mm")
        else:
            self.max_spread_val.config(text="0.0 mm")

        # Render score histogram graphics
        self.draw_histogram(scores_distribution)

    # ================= HISTOGRAM DRAWING =================
    def draw_histogram(self, dist_dict):
        self.histo_canvas.delete("all")
        
        categories = ["X", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1"]
        # Convert dictionary keys safely to strings to pull values
        counts = [dist_dict.get(int(c) if c.isdigit() else c, 0) for c in categories]
        
        max_count = max(counts) if max(counts) > 0 else 1
        
        canvas_w = 480
        canvas_h = 120
        col_count = len(categories)
        col_width = canvas_w / col_count

        for i, cat in enumerate(categories):
            count = counts[i]
            x0 = i * col_width + 4
            x1 = (i + 1) * col_width - 4
            
            # Dynamic bar scale mapping to canvas height
            bar_height = (count / max_count) * 45 if count > 0 else 2
            y0 = 60 - bar_height
            y1 = 60
            
            # Draw count bar
            bar_color = "#212121" if count > 0 else "#E0E0E0"
            self.histo_canvas.create_rectangle(x0, y0, x1, y1, fill=bar_color, outline="")

            # Count Label (number directly below bar)
            count_text = str(count) if count > 0 else "—"
            count_font = ("Helvetica", 11, "bold") if count > 0 else ("Helvetica", 10)
            count_color = "#111111" if count > 0 else "#888888"
            self.histo_canvas.create_text((x0 + x1)/2, 75, text=count_text, fill=count_color, font=count_font)

            # Ring ID Label (X, 10, 9, etc.)
            self.histo_canvas.create_text((x0 + x1)/2, 95, text=cat, fill="#666666", font=("Helvetica", 10))

    # ================= EVENT UTILITIES =================
    def on_preset_change(self, event):
        preset_name = self.selected_preset.get()
        if preset_name in self.target_presets:
            preset = self.target_presets[preset_name]
            self.target_diameter_mm.set(preset["target_diameter"])
            self.shot_diameter_mm.set(preset["shot_diameter"])
            self.draw_shots_and_centroid()
            self.calculate_metrics()

    def undo_last_shot(self):
        if self.shots:
            self.shots.pop()
            self.draw_shots_and_centroid()
            self.calculate_metrics()

    def delete_selected_shot(self, event):
        selection = self.shot_listbox.curselection()
        if selection:
            index = selection[0]
            self.shots.pop(index)
            self.draw_shots_and_centroid()
            self.calculate_metrics()

    def clear_all(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all shots?"):
            self.shots.clear()
            self.draw_shots_and_centroid()
            self.calculate_metrics()

    def export_csv(self):
        if not self.shots:
            messagebox.showwarning("No Data", "There are no shots plotted to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Shot Log Data"
        )
        if file_path:
            try:
                mm_per_px = self.get_mm_per_pixel()
                xc, yc = self.target_center
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Shot Number", "X_pixel", "Y_pixel", "X_mm", "Y_mm"])
                    for idx, (px, py) in enumerate(self.shots):
                        dx_mm = (px - xc) * mm_per_px
                        dy_mm = (yc - py) * mm_per_px
                        writer.writerow([idx + 1, px, py, f"{dx_mm:.2f}", f"{dy_mm:.2f}"])
                messagebox.showinfo("Export Successful", f"Saved successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not save file:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TargetAnalyzerApp(root)
    root.mainloop()
