# Shot Group Analysis & Target Statistics

A desktop application for analyzing shooting performance on ISSF-style targets. The application allows users to place shots on a virtual target, calculate statistical measures of shot groups, visualize shot distribution, and export shooting data for further analysis.

## Features

- Interactive target with mouse-based shot placement.
- Support for multiple ISSF target standards.
- Custom target diameter configuration.
- Automatic shot scoring.
- ISSF touch scoring rule implementation.
- X-ring detection.
- Live score display.
- Windage and elevation calculation.
- Mean radius calculation.
- Extreme spread calculation.
- Group centroid visualization.
- Mean radius circle visualization.
- Score distribution histogram.
- Shot coordinate log.
- Undo last shot.
- Delete individual shots.
- Clear target.
- Export shot data to CSV.

---

## Supported Target Standards

- 10 m Air Pistol
- 10 m Air Rifle
- 50 m Pistol
- Custom target

The target diameter may also be entered manually for custom applications.

---

## ISSF Touch Scoring

Unlike many simple target simulators, this application uses the **touch scoring rule**.

A shot receives the higher score whenever the edge of the projectile touches the higher scoring ring.

Instead of using only the center of the shot, the scoring algorithm considers the physical projectile diameter.

Default projectile diameters:

| Discipline | Projectile Diameter |
|------------|--------------------:|
| Air Rifle / Air Pistol | 4.5 mm |
| 50 m Pistol | 5.6 mm |

This produces scoring that more closely matches official ISSF competition rules.

---

## Statistics

The application calculates:

- Total score
- Number of X-ring hits
- Windage
- Elevation
- Mean Radius (MR)
- Extreme Spread (ES)
- Group centroid
- Score distribution

---

## Visualizations

The application displays:

- Virtual shooting target
- Shot locations
- Group centroid
- Mean radius circle
- Score histogram
- Shot log with coordinates

---

## Export

Shot data can be exported as CSV.

The exported file includes:

- Shot number
- X coordinate (pixels)
- Y coordinate (pixels)
- X coordinate (mm)
- Y coordinate (mm)

---

## Requirements

- Python 3.10+

### Standard Libraries

The project only uses Python standard libraries.

```
tkinter
math
datetime
csv
```

No external packages are required.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/ShotGroupAnalyzer.git
```

Move into the project directory:

```bash
cd ShotGroupAnalyzer
```

Run the application:

```bash
python target_analyzer.py
```

---

## Usage

1. Select the desired target standard.
2. Adjust the target diameter if required.
3. Click anywhere on the target to record a shot.
4. Review the calculated statistics.
5. Export the shot data if needed.

Double-click a shot in the log to remove it.

---

## Future Improvements

Planned features include:

- Decimal ISSF scoring
- Multiple shooting sessions
- PDF report generation
- Image import and automatic shot detection
- Shot timer integration
- Group comparison
- Multiple target overlays
- Heat map visualization
- Confidence ellipse
- CEP and R95 calculations
- MOA and MIL conversion
- Firearm and ammunition profiles
- Session history database

---

## Project Structure

```
ShotGroupAnalyzer/
│
├── target_analyzer.py
├── README.md
└── LICENSE
```

---

## License

This project is released under the MIT License.

---

## Acknowledgements

This application is inspired by competitive target shooting analysis methods and ISSF target specifications. It is intended as an educational and performance analysis tool for athletes, coaches, and shooting enthusiasts.
