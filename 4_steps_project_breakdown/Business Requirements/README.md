# Overview: U Cluj Defensive Performance

In this project, I’m building an **Expected Threat (xT) model** to evaluate **U Cluj’s defensive performance**, inspired by the methodology introduced in [_Soccermatics_](https://soccermatics.readthedocs.io/en/latest/lesson4/EvaluatingActions.html). Using **Wyscout event data** from all matches, I wanted to go beyond basic defensive metrics (like goals conceded) and see **how opponent actions actually generate danger on the pitch**.

For the MVP, I focused on delivering a first set of insights through **zone-based visualizations and metrics**:

- **Movement Maps** → 2D histograms showing where opponent passes and carries happen most often.
- **Shot & Goal Maps** → highlighting the pitch zones where opponents create shots and convert goals.
- **Transition Zone Probabilities** → visualizations that show how opponents move the ball from midfield zones into threatening areas.
- **xT Evolution per Action** → a step-by-step matrix illustrating how Expected Threat increases with each type of pass or cross.
- **Opponent Player Rankings (per 90 minutes)** → identifying the top opponent players who generated the highest cumulative xT against U Cluj.

By putting these outputs together, I can start to see **where U Cluj is most vulnerable**, **how threats develop during possessions**, and **which players cause the biggest problems** — all of which form a data-driven base for tactical improvements.

---

## Key Questions Guiding the Analysis

While building this, I kept in mind some of the main questions that stakeholders might have, in accordance with what we learned during the live sessions organized by DataCamp's team of national and international mentors.

My MVP doesn’t answer everything perfectly, but it provides solid first steps toward:

- **Which areas of the pitch are most frequently exploited by opponents?**  
  → Movement, shot, and goal maps reveal recurring zones of defensive exposure.

- **Do opponents create more danger through central zones or from wide areas?**  
  → Transition zone analysis highlights the pathways most commonly used to enter the final third.

- **Which types of actions add the greatest threat against us?**  
  → xT evolution shows whether quick passes, long balls, or wide deliveries create the most danger.

- **Are there consistent “red zones” in our defensive structure?**  
  → Zone-based xT maps expose the pitch areas where vulnerabilities are repeatedly observed.

- **Which opposition players generate the most threat against U Cluj?**  
  → Opponent rankings (per 90 minutes) highlight the attackers who have caused the greatest problems this season.

---

## Data Required

To make the notebook run properly, I set it up to expect a folder named **`datasets/`** with the extracted **Wyscout event data**.

- **Season**: 2024–2025
- **Matches**: All 40 games played by U Cluj
- **Format**: CSV file (one file with all matches, as exported from Wyscout)

All you need to do is place this file inside the `datasets/` directory at the root of the repository before running the notebook.

---

## Methodology for the MVP

I documented the whole process in a **single Jupyter Notebook**. This way, everything is in one place:

- **Integrated workflow** → all steps, from data preparation to visualization, live together for easier management.
- **Faster prototyping** → I can quickly adjust ideas and immediately see results.
- **Transparency & reproducibility** → each step (data cleaning, feature creation, visualization, xT calculation) is documented so the results can be followed or extended later.

This notebook-first setup keeps things simple for the MVP while leaving room to break it into scripts and functions if the project grows.

---

## Future Directions

If I push this project further, there are several directions I’d like to explore to make the analysis more complete and useful:

- **Modularized Workflow**

  - Separate the current all-in-one notebook into clear components:
    - **Data Engineering** → extraction, cleaning, and transformation of event data.
    - **Analysis** → xT model calculations, action breakdowns, and player metrics.
    - **Visualization** → maps, plots, and interactive dashboards.
  - This makes the project easier to maintain, extend, and collaborate on, while aligning with good data engineering practices.

- **Shot Quality & Danger Calibration**

  - Bring in _expected goals (xG)_ to measure not just where shots happen, but how good they are.
  - Connect xT buildup directly to xG outcomes, following the _Soccermatics_ idea of linking possession value to shot quality.

- **Defensive Action Mapping**

  - Add heatmaps of duels, interceptions, and clearances.
  - Compare defensive actions with high-xT zones to see if problems are due to positioning, reaction speed, or pressure.

- **Expanded xT Model Variables**

  - Include more context (e.g., pass length, direction, game state, player position).
  - Build more detailed “xT added” metrics per action type.

- **Opponent Profiling**

  - Extend the player rankings into role-based profiles (wingers, strikers, midfielders).
  - Track how different kinds of players exploit different zones.

- **Interactive Dashboard**

  - Turn everything into a user-friendly tool (Power BI, Streamlit) where coaches can filter by match, player, or action type.

- **Predictive Systems** (long-term)
  - Move beyond describing what happened to predicting what’s likely next.
  - For example: flagging possessions as “likely dangerous” before they even reach the final third, as outlined in _Soccermatics_.
