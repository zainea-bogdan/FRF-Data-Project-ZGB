# Overview Business Context and Problem I am trying to solve

This project aims to improve U Cluj's defense by using advanced data analysis. Instead of just looking at how many goals I concede, I want to understand the specific reasons why opponents create dangerous chances against U Cluj. This will help us identify our defensive weaknesses and make smarter tactical adjustments.

## Core Questions I will try to answer:

- Where are we most vulnerable on the pitch? I'll pinpoint the exact areas where opponents create their most dangerous attacks against us.

- What specific opponent actions break down U Cluj defense? I'll identify which types of passes or runs consistently put us in trouble.

- Who are our most exposed players defensively? I'll analyze individual player performance in defensive situations.

- Can we predict and prevent defensive breakdowns? We'll develop a way to flag an opponent's possession as "dangerous" early on, before a shot is even taken.

## Data Required

To achieve our goals, I will primarily use the following columns from your game event data for developing the MVP OF THIS PROJECT:

- `location.x` (starting X coordinate of an event)
- `location.y` (starting Y coordinate of an event)
- `pass.endLocation.x` (ending X coordinate for a pass)
- `pass.endLocation.y` (ending Y coordinate for a pass)
- `carry.endLocation.x` (ending X coordinate for a carry)
- `carry.endLocation.y` (ending Y coordinate for a carry)
- `type.primary` (e.g., 'Pass', 'Carry')
- `type.secondary` (for more specific event types if needed)
- `team.id` (to identify our team vs. opponent)
- `opponentTeam.id` (to identify the opposing team)
- `matchId` (to group events by match)
- `seasonId` (to filter for the last season)

## Methodology Step by Step

I am tackling this project in four clear phases, moving from raw data to actionable insights:

### Smart Data Preparation

This involves transforming raw event data into powerful new metrics that quantify defensive performance and opponent threat.

### Visualizing the Problem

Turning my new data and features into easy-to-understand visuals that highlight U Cluj defensive weaknesses.

### Building a Predictive System

Developing a smart model that can predict a defensive problem before it happens.

### Actionable Insights

Translating all findings into a clear, concise, and actionable plan for the coaching staff.

## Desired MVP Until the End of DATACAMP:

For my first usable version (MVP), I will focus on completing the Smart Data Preparation (Feature Engineering) and generating Key Visualizations. This is a highly achievable and immediately valuable goal.I will apply this analysis for U Cluj using all their matches' data from the last season. This focused approach makes my project doable and provides immediate, valuable insights.

## What I Will Do for the MVP:

### Gather Opponent Actions

I'll select all the pass events and carry (dribbling) events made by the opponent team in every match from the last season for our selected teams. This data will be organized in a clear table.

### Map the Field into a Grid

I'll divide the soccer field into a grid of smaller squares (like a chessboard, for example 12 squares wide by 16 squares long). Every square on the field will have a unique ID.

### Build the "Danger Map" (xT Map)

Using all the opponent passes and carries from across the entire league (or a large dataset), i'll calculate how often the ball moves from one grid square to another. This helps us understand typical ball movement patterns.

Then, using a Markov chain mathematical method, I'll assign a single number to every single square on our grid. This number is the Expected Threat (xT) value for that square.

> **What xT means:** The xT value of a square tells us: "If the ball is in this square, what is the average chance it will eventually lead to a goal?" Squares closer to the opponent's goal will naturally have higher xT values.

**Result:** This gives me one universal "Danger Map" for the entire league, showing how dangerous each spot on the field usually is.

### Calculate "Opponent xT Added" (Our Key Metric)

Now, for each individual opponent pass and carry event against our selected teams, we'll use our "Danger Map."

We'll look up the xT value of the square where the action started and the xT value of the square where it ended.

We then calculate:  
(xT of the End Square) - (xT of the Start Square)

**Why this helps:** This difference, called `opponent_xT_added`, is a single number that tells us if that specific pass or carry made the opponent's attack significantly more dangerous. A large positive number means it was a very threatening action that broke down our defense. This helps us pinpoint the exact moments and actions that put us in trouble.

### Overall Team View for Last Season

Finally, we'll gather all the `opponent_xT_added` values from the matches played against U Cluj in the last season.

I'll sum or average these values to get a clear, overall picture of the total threat U Cluj conceded from opponent passes and carries throughout the entire year.

### Vulnerability Heatmaps (Visualization)

I will create a heatmap of the pitch where the color of each grid cell is based on the average or total `opponent_xT_added` from actions that occurred in that cell against U Cluj. This map will immediately show us U Cluj's biggest "red zones" of defensive weakness.

## Extra Futures I Would Like to Add

If I successfully complete this MVP and find the insights useful, our next steps could include:

- **Visualizing Opponent Pass Networks:** Creating network graphs to show how opponents connect passes, especially those that generate high xT, to reveal their key playmakers and attacking patterns.

- **Finding ML Patterns in Passes Leading to Goals:** Developing a machine learning model that can predict the likelihood of an opponent's possession leading to a goal, acting as an "early warning system" by identifying specific patterns of passes and carries that are highly dangerous.

- **Full Predictive System:** Expanding the predictive model to include more factors and provide real-time insights.

- **Actionable Insights & Interactive Dashboard:** Creating detailed reports for the coaching staff with specific recommendations and building an interactive dashboard to monitor defensive performance over time.
