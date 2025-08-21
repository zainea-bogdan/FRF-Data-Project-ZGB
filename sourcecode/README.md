# MVP — Jupyter Notebook Presentation

**Check the [notebook](mvp_step_by_step.ipynb) for a full step-by-step walkthrough.**  
The analysis follows the _Soccermatics_ guide ([read more](https://soccermatics.readthedocs.io/en/latest/gallery/lesson4/plot_ExpectedThreat.html)) for computing an xT heatmap, but adapted to work with **WyScout data in Excel format**.

**Datasource:** WyScout, Excel export for the 2024–2025 season, including all U Cluj matches **only**.

**Key twist:** instead of analyzing U Cluj’s own actions, the focus is on **opponents’ passes and shots** to reveal where they create attacking threat. The results are then interpreted from U Cluj’s perspective, highlighting **defensive danger zones**—both per-opponent and overall—based on last season’s data.

---

# Flow of the MVP GUI — Flask Application

## 1) Application Startup

**What happens:** you run `app.run(debug=True)` and the server starts.

**How:**

- On import, a `try/except` attempts to load `Universitatea_Cluj_2024_2025_events.csv`.  
  If the file is missing, a message is printed (_"file doesn’t exist"_). No dummy DataFrame is created.  
  The loaded data (`df_raw`) is kept in memory and accessible globally.
- The Flask app `app` is initialized. Globals like `TEAMS`, `PLOT_DESCRIPTIONS`, and `calculation_cache` are prepared.

**Why it matters:** the dataset loads **once**; subsequent requests reuse it → faster responses.

---

## 2) Initial Page Load (`/`)

**What happens:** visiting the root URL triggers `index()`.

**How:**

- `@app.route('/')` maps the route.
- `index()` returns `render_template_string(HTML_FORM, teams=teams)`, which includes:
  - Title: _UCLUJ Team Analytics Dashboard_
  - Team dropdown
  - **Run Analysis** button

**Why it matters:** lightweight setup—no heavy processing yet.

---

## 3) User Clicks “Run Analysis” (`/analyze`)

**What happens:** the form submits a `POST` to `/analyze`.

**How:**

- `@app.route('/analyze', methods=['POST', 'GET'])` triggers `analyze()`.
- Parameters via `request.values.get()`:
  - `selected_team_id_str` (team),
  - `selected_plot_title` (None initially),
  - `selected_sector` (None initially).
- **Filtering:**
  - If `UCLUJ` → keep all opponents’ events.
  - Else → filter events for the selected team.
- **Validation:** if `processed_df` is empty → return a clear error message.
- **Cache:**
  - Keyed by team.
  - If missing → run `run_all_calculations(processed_df)` (all heatmaps, probabilities, xT matrix) and store the results.
  - If present → reuse instantly.
- **Default plot:** if `selected_plot_title` is `None`, fall back to the first option (e.g., _Moving-Ball Actions Heatmap_).
- **Plot generation:** `generate_specific_plot()` pulls the right stats from cache → `generate_heatmap_plot()` renders with `matplotlib` → image is Base64-encoded.
- **Render:** `render_template_string(HTML_RESULTS, …)` returns the image, plot list, and the selected description.

**Why it matters:** heavy computations run **once per team**, then everything is cached.

---

## 4) User Changes Plot or Sector

**What happens:** the plot/sector dropdowns trigger a `GET` to `/analyze` via `onchange`.

**How:**

- `analyze()` runs again with `selected_plot_title` and/or `selected_sector`.
- **Cache is used:** no re-calculation.
- **Branching:**
  - If **Transition Matrix** → fetch `transition_matrices_array` and call `generate_transition_matrix_plot(selected_sector)` (handles indexing & highlighting).
  - Else → `generate_specific_plot()` → `generate_heatmap_plot()`.
- **Render:** the updated plot is displayed immediately.

**Why it matters:** responsive interaction with minimal overhead.

---

## 5) Future Improvements for the GUI

- **Refined color schemes**: improve the choice of colors in plots to make them more attractive and easier to interpret.
- **Enhanced explanations**: adapt and refine the descriptions based on feedback from the coaching staff.
- **Expanded plotting options**: support additional types of visualizations depending on team requirements.
