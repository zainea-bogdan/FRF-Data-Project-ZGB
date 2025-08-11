# Overview: U Cluj Defensive Performance Analysis

This project aims to improve U Cluj's defense by moving beyond basic stats like goals conceded. The goal is to understand the specific reasons why opponents create dangerous chances, helping the team identify their defensive weaknesses and make smarter tactical adjustments.

---

## Core Questions the Analysis Will Answer

- **Where is U Cluj most vulnerable on the pitch?**  
  The analysis will pinpoint the exact areas where opponents create their most dangerous attacks.

- **What specific opponent actions break down U Cluj's defense?**  
  The analysis will reverse-engineer opponent attacks to identify which passes or runs consistently put the team in trouble.

- **Can the team predict and prevent defensive breakdowns?**  
  A method will be developed to flag an opponent's possession as "dangerous" early on.

---

## Data Required

To achieve these goals, the following columns from the game event data will be used:

- `id`
- `matchId`
- `matchPeriod`
- `minute`
- `second`
- `type.primary`
- `type.secondary`
- `location.x`
- `location.y`
- `team.id`
- `team.name`
- `opponentTeam.id`
- `opponentTeam.name`
- `player.id`
- `player.name`
- `pass.endLocation.x`
- `pass.endLocation.y`
- `shot.xg`
- `shot.isGoal`
- `shot.onTarget`
- `carry.endLocation.x`
- `carry.endLocation.y`
- `possession.id`
- `possession.duration`
- `possession.startLocation.x`
- `possession.startLocation.y`
- `possession.endLocation.x`
- `possession.endLocation.y`
- `competitionId`
- `seasonId`
- `Home_Away`

---

## Methodology Step by Step

The project is being tackled in four clear phases, moving from raw data to actionable insights:

1. **Smart Data Preparation**  
   Transform raw event data into powerful new metrics that quantify defensive performance and opponent threat.

2. **Visualizing the Problem**  
   Turn the new data and features into easy-to-understand visuals that highlight U Cluj's defensive weaknesses.

3. **Building a Predictive System**  
   Develop a smart model that can predict a defensive problem before it happens.

4. **Actionable Insights**  
   Translate all findings into a clear, concise, and actionable plan for the coaching staff.

---

## Desired MVP Until the End of DATACAMP

For the first usable version (MVP), the focus will be on completing **Smart Data Preparation (Phase 1)** and generating **Key Visualizations (Phase 2)**.  
This is a highly achievable and immediately valuable goal. All of U Cluj's matches from the last season will be used for this analysis.

---

### What the MVP Will Include

#### A. U Cluj's Defensive Vulnerability Map

1. **Gather Opponent Actions**  
   Collect all opponent pass and carry events from all of U Cluj's games in the last season.

2. **Build a "Danger Map" (xT Map)**  
   Using a Markov chain mathematical method, create a grid-based _Danger Map_.  
   This map will assign an Expected Threat (**xT**) value to every square on the field, based on all passes and carries from the collected data.

3. **Calculate "Opponent xT Added"**  
   For each opponent pass and carry against U Cluj:  
   `(xT of End Square) - (xT of Start Square)` = `opponent_xT_added`  
   This number shows how much danger that specific action created.

4. **Create a Heatmap**  
   Visualize `opponent_xT_added` values on a pitch heatmap, with color intensity showing the average threat created in each grid cell (U Cluj's biggest "red zones").

---

#### B. Opponent Pass Network and Patterns

1. **Filter for Dangerous Possessions**  
   Select possessions with a high `opponent_xT_added` value or that resulted in a shot.

2. **Build a Network Graph**

   - Nodes = pitch grid zones
   - Links = ball movement from one zone to another
   - Link thickness = number of passes/carries
   - Display this graph as an overlay on a pitch diagram.

3. **Find Common Patterns**  
   Identify the **top 5–10 most common pathways** opponents used to enter dangerous zones.  
   Trace the strongest links to reverse-engineer their most successful attacking sequences.

---

## Extra Features the Team Would Like to Add

If the MVP is successful, future steps could include:

- **Shot Quality Analysis**: Analyze average `shot.xg` of shots conceded to understand chance quality.
- **Defensive Action Analysis**: Create heatmaps of successful duels and interceptions to compare strengths vs. vulnerabilities.
- **A Full Predictive System**: Expand the model to include more variables and real-time predictions.
- **An Interactive Dashboard**: Build a user-friendly interface for the coaching staff to monitor defensive KPIs.
