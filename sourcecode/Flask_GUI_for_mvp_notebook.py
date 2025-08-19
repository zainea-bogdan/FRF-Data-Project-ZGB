import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from flask import Flask, render_template_string, request, url_for, redirect
from scipy.stats import binned_statistic_2d
from itertools import product
import io
import base64
import ast
import warnings
import os

# Set a non-GUI backend for Matplotlib to prevent thread errors in Flask
plt.switch_backend('Agg')

# Suppress pandas and other library warnings for cleaner output
pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

# --- DATA LOADING AND PREPROCESSING ---
# This part of the code is executed once when the app starts.
try:
    df_raw = pd.read_csv("datasets/Universitatea_Cluj_2024_2025_events.csv")
    # Convert 'type.secondary' and 'pass.endLocation' from strings to lists/objects
    df_raw['type.secondary'] = df_raw['type.secondary'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    # Assume 'pass.endLocation' is also a string representation of an object
    df_raw['pass.endLocation.x'] = df_raw['pass.endLocation.x'].astype(float)
    df_raw['pass.endLocation.y'] = df_raw['pass.endLocation.y'].astype(float)

except FileNotFoundError:
    print("Error: Dataset file not found. Please check the file path.")
    # Create a dummy DataFrame if the file is not found to allow the app to run
    data = {
        'player.id': np.random.randint(1, 10, 1000),
        'player.name': ['Player ' + str(i) for i in np.random.randint(1, 10, 1000)],
        'player.position': np.random.choice(['Defender', 'Midfielder', 'Forward'], 1000),
        'team.name': np.random.choice(['UCLUJ', 'Team B', 'Team C'], 1000),
        'type.secondary': np.random.choice(['short_or_medium_pass', 'long_pass', 'other_event'], 1000),
        'pass.accurate': np.random.choice([True, False], 1000),
        'matchId': np.random.choice([1, 2, 3, 4, 5], 1000),
        'minute': np.random.randint(0, 95, 1000),
        'second': np.random.randint(0, 60, 1000),
        'location.x': np.random.randint(1, 100, 1000),
        'location.y': np.random.randint(1, 100, 1000),
        'pass.endLocation.x': np.random.randint(1, 100, 1000),
        'pass.endLocation.y': np.random.randint(1, 100, 1000),
        'matchPeriod': np.random.choice(['1H', '2H'], 1000),
        'shot.isGoal': np.random.choice([True, False], 1000),
        'type.primary': np.random.choice(['pass', 'shot'], 1000),
        'team.id': np.random.choice([60374, 11566], 1000)
    }
    df_raw = pd.DataFrame(data)

# --- Define the list of teams and their IDs ---
TEAMS = [
    (11566, 'Rapid Bucureşti'),
    (11564, 'Dinamo Bucureşti'),
    (11565, 'FCS Bucureşti'),
    (11611, 'CFR Cluj'),
    (26233, 'Universitatea Craiova'),
    (61242, 'Farul Constanţa'),
    (11634, 'Botoşani'),
    (11571, 'Oţelul'),
    (11663, 'Unirea Slobozia'),
    (11886, 'Poli Iaşi'),
    (60392, 'AS FC Buzău'),
    (32854, 'Sepsi'),
    (60390, 'Petrolul 52'),
    (30817, 'UTA Arad'),
    (55427, 'Hermannstadt')
]

# --- PLOT DESCRIPTIONS ---
# Dictionary to store a description for each plot
PLOT_DESCRIPTIONS = {
    'Pass Heatmap': "This heatmap visualizes the starting locations of all accurate passes. The darker shades of blue indicate areas where a high number of passes were initiated. This gives a clear picture of the team's build-up play and general passing patterns.",
    'Shot Heatmap': "This heatmap shows the locations from where all shots were taken. The green color intensity represents the concentration of shot attempts, highlighting the most common shooting areas on the pitch for the selected team.",
    'Goal Heatmap': "This heatmap displays the locations of all goals scored. The red color intensity indicates the areas from which the team successfully scored, giving insights into the most effective scoring zones.",
    'Move Probability': "This is a probability map showing the likelihood of a successful pass (move) occurring in each zone of the pitch. Hotter colors indicate higher probability. This is a fundamental component of the Expected Threat (xT) model.",
    'Shot Probability': "This map visualizes the probability of a shot being taken from each zone on the pitch. The greener the area, the more likely a shot is to occur from that location, which is a key factor in calculating xT.",
    'Goal Probability': "This plot shows the probability of a shot resulting in a goal from each zone. Redder areas indicate a higher likelihood of a goal being scored from that position, serving as a simple Expected Goals (xG) model.",
    'xT Matrix after 1 Moves': "The Expected Threat (xT) matrix after one iteration of the Markov chain. This is the initial state of the xT model, showing the raw threat values of each zone based on direct pass and shot probabilities.",
    'xT Matrix after 2 Moves': "The xT matrix after two moves. The values have been updated to reflect the added threat of passes that move the ball into more dangerous areas, even if they aren't followed by an immediate shot.",
    'xT Matrix after 3 Moves': "The xT matrix after three moves. The model's understanding of long-term threat has deepened. Values in deeper areas of the pitch are starting to increase as their potential for leading to a goal becomes more evident.",
    'xT Matrix after 4 Moves': "The xT matrix after four moves. The model is now capable of valuing sequences of passes that lead to a high-threat zone. The values are becoming more stable and representative of the pitch's true offensive value.",
    'xT Matrix after 5 Moves': "The xT matrix after five moves. The threat values across the pitch are becoming more refined. The high-value zones near the goal are clearly defined, and passes into these areas are highly valued by the model.",
    'xT Matrix after 6 Moves': "The xT matrix after six moves. The values are nearing convergence. This iteration of the model provides a comprehensive view of the pitch's offensive value, accounting for complex passing sequences.",
    'xT Matrix after 7 Moves': "The xT matrix after seven moves. At this stage, the changes in xT values are minimal, indicating that the model has largely converged. The heatmap accurately reflects the strategic value of each zone.",
    'xT Matrix after 8 Moves': "The xT matrix after eight moves. The values are now very stable. This is a robust representation of the offensive value of each zone, factoring in multiple passes and shots.",
    'xT Matrix after 9 Moves': "The xT matrix after nine moves. The model has reached a high level of accuracy. The values across the pitch provide a reliable measure of the threat associated with ball possession in any given zone.",
    'xT Matrix after 10 Moves': "The final Expected Threat (xT) matrix after 10 iterations. This converged model provides the most accurate and complete representation of the offensive value of each zone on the pitch."
}

# --- CACHING ---
# Cache to store calculation results to avoid re-computation on subsequent requests
calculation_cache = {}

# --- FLASK WEB APPLICATION SETUP ---
app = Flask(__name__)

# The HTML for the main page with a dropdown menu.
HTML_FORM = """
<!doctype html>
<html>
<head>
    <title>Football Analytics GUI</title>
    <style>
        body { font-family: sans-serif; margin: 2em; background-color: #f0f2f5; }
        .container { max-width: 800px; margin: auto; }
        .form-container { background: #fff; padding: 2em; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        .form-container form { display: flex; flex-direction: column; gap: 1em; }
        .form-container select, .form-container button { 
            width: 100%; padding: 12px; font-size: 16px; 
            border-radius: 6px; border: 1px solid #ccc; box-sizing: border-box; 
        }
        .form-container button { background-color: #007bff; color: white; cursor: pointer; border: none; font-weight: bold; }
        .form-container button:hover { background-color: #0056b3; }
        h1 { text-align: center; color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>UCLUJ Team Analytics Dashboard</h1>
        <div class="form-container">
            <form action="/analyze" method="post">
                <label for="team_id_selection">Select a Team:</label>
                <select name="team_id_selection" id="team_id_selection">
                    <option value="UCLUJ">UCLUJ - All Games (Detailed Analysis)</option>
                    {% for team_id, team_name in teams %}
                    <option value="{{ team_id }}">Game {{ team_name }}</option>
                    {% endfor %}
                </select>
                <button type="submit">Run Analysis</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

# HTML for the results page with the new dropdown
HTML_RESULTS = """
<!doctype html>
<html>
<head>
    <title>Analysis Results</title>
    <style>
        body { font-family: sans-serif; margin: 2em; background-color: #f0f2f5; }
        .container { max-width: 1200px; margin: auto; }
        .plot-controls { background: #fff; padding: 1em; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 2em; text-align: center; }
        .plot-controls select { width: 50%; padding: 12px; font-size: 16px; border-radius: 6px; border: 1px solid #ccc; }
        .plot-box { 
            background: #fff; padding: 1em; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
            text-align: center; margin-bottom: 2em;
        }
        .plot-box img { max-width: 100%; height: auto; display: block; margin: auto; }
        .plot-caption { 
            font-size: 1.1em; color: #555; line-height: 1.6; 
            margin-top: 1em; padding-top: 1em; border-top: 1px solid #eee;
        }
        .plot-caption h2 { margin-top: 0; font-size: 1.2em; color: #333; }
        .message-box { background: #fff; padding: 2em; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        .back-button { display: inline-block; margin-bottom: 2em; padding: 10px 15px; background-color: #6c757d; color: white; text-decoration: none; border-radius: 6px; }
        .back-button:hover { background-color: #5a6268; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-button">← Go Back</a>
        <h1>Analysis for {{ title }}</h1>
        {% if plots %}
            <div class="plot-controls">
                <form action="/analyze" method="get">
                    <input type="hidden" name="team_id_selection" value="{{ team_id_selection }}">
                    <label for="plot_select">Select a Plot:</label>
                    <select name="plot_title" id="plot_select" onchange="this.form.submit()">
                        {% for plot_title in plot_titles %}
                        <option value="{{ plot_title }}" {% if plot_title == selected_plot_title %}selected{% endif %}>{{ plot_title }}</option>
                        {% endfor %}
                    </select>
                </form>
            </div>
            
            {% for plot_title, plot_url in plots.items() %}
                <div class="plot-box">
                    <img src="data:image/png;base64,{{ plot_url }}" alt="{{ plot_title }}">
                    <div class="plot-caption">
                        <h2>{{ plot_title }}</h2>
                        <p>
                            {{ descriptions[plot_title] }}
                        </p>
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div class="message-box">
                <p>{{ message }}</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

def generate_heatmap_plot(binned_statistic, title, cmap='Blues', show_labels=False, figsize=(15, 8)):
    """
    Generates a heatmap plot from a pre-binned statistic and returns it as a base64 encoded image string.
    Added a `show_labels` parameter to conditionally display labels and `figsize` for plot size.
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=figsize)
    pitch = Pitch(line_color='black', pitch_type='custom', pitch_length=105, pitch_width=68, line_zorder=2)
    
    pitch.draw(ax=ax)
    
    if binned_statistic is None:
        ax.set_title(title, fontsize=20)
    else:
        # Plot the heatmap
        pcm = pitch.heatmap(binned_statistic, cmap=cmap, edgecolor='grey', ax=ax)
        
        # Add a colorbar
        ax_cbar = fig.add_axes([0.95, 0.1, 0.03, 0.8])
        plt.colorbar(pcm, cax=ax_cbar)
        
        # Conditionally add labels to the plot
        if show_labels:
            pitch.label_heatmap(binned_statistic, color='blue', fontsize=9,
                                 ax=ax, ha='center', va='center', str_format="{0:,.2f}", zorder=3)
        
        fig.suptitle(title, fontsize=20)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def run_all_calculations(dataframe):
    """
    Runs all the core calculations once and stores the binned statistics.
    """
    calculations = {}
    pitch = Pitch(line_color='black', pitch_type='custom', pitch_length=105, pitch_width=68, line_zorder=2)
    bins = (16, 12)
    
    # 1. HEATMAPS FOR MOVES, SHOTS, AND GOALS
    pass_types = ['short_or_medium_pass', 'long_pass', 'head_pass', 'smart_pass', 'cross', 'forward_pass', 'progressive_pass', 'lateral_pass']
    move_df = dataframe.loc[
        (dataframe['type.secondary'].apply(lambda x: isinstance(x, list) and any(item in x for item in pass_types))) &
        (dataframe['pass.accurate'] == True)
    ].copy()

    shot_df = dataframe.loc[dataframe['type.primary'] == "shot"].copy()
    goal_df = shot_df.loc[shot_df['shot.isGoal'] == True].copy()
    
    calculations['move_binned'] = pitch.bin_statistic(move_df['location.x'], move_df['location.y'], statistic='count', bins=bins, normalize=False) if not move_df.empty else None
    calculations['shot_binned'] = pitch.bin_statistic(shot_df["location.x"], shot_df["location.y"], statistic='count', bins=bins, normalize=False) if not shot_df.empty else None
    calculations['goal_binned'] = pitch.bin_statistic(goal_df["location.x"], goal_df["location.y"], statistic='count', bins=bins, normalize=False) if not goal_df.empty else None

    # 2. PROBABILITY MAPS
    if calculations['move_binned'] is not None and calculations['shot_binned'] is not None and calculations['goal_binned'] is not None:
        move_count = calculations['move_binned']["statistic"]
        shot_count = calculations['shot_binned']["statistic"]
        goal_count = calculations['goal_binned']["statistic"]
        
        total_actions = move_count + shot_count
        move_probability = np.divide(move_count, total_actions, out=np.zeros_like(move_count), where=total_actions != 0)
        shot_probability = np.divide(shot_count, total_actions, out=np.zeros_like(shot_count), where=total_actions != 0)
        goal_probability = np.divide(goal_count, shot_count, out=np.zeros_like(goal_count), where=shot_count != 0)

        move_prob_binned = calculations['move_binned'].copy()
        move_prob_binned["statistic"] = move_probability
        shot_prob_binned = calculations['shot_binned'].copy()
        shot_prob_binned["statistic"] = shot_probability
        goal_prob_binned = calculations['goal_binned'].copy()
        goal_prob_binned["statistic"] = goal_probability
        
        calculations['move_prob_binned'] = move_prob_binned
        calculations['shot_prob_binned'] = shot_prob_binned
        calculations['goal_prob_binned'] = goal_prob_binned
        calculations['goal_probability'] = goal_probability
        calculations['shot_probability'] = shot_probability
        calculations['move_probability'] = move_probability
    
    # 3. xT MATRIX (Markov chain calculation)
    if 'move_prob_binned' in calculations:
        pitch_length = 105
        pitch_width = 68
        
        start_sectors = binned_statistic_2d(move_df['location.x'], move_df['location.y'], values=None, statistic='count', bins=bins, range=[[0, 105], [0, 68]], expand_binnumbers=True)[3]
        move_df['start_sector_x_bin'], move_df['start_sector_y_bin'] = start_sectors[0], start_sectors[1]
        end_sectors = binned_statistic_2d(move_df['pass.endLocation.x'], move_df['pass.endLocation.y'], values=None, statistic='count', bins=bins, range=[[0, 105], [0, 68]], expand_binnumbers=True)[3]
        move_df['end_sector_x_bin'], move_df['end_sector_y_bin'] = end_sectors[0], end_sectors[1]

        transition_matrices_array = np.zeros((192, 12, 16))
        for start_sector_x in range(1, 17):
            for start_sector_y in range(1, 13):
                this_sector_moves = move_df[(move_df['start_sector_x_bin'] == start_sector_x) & (move_df['start_sector_y_bin'] == start_sector_y)]
                
                count_starts = len(this_sector_moves)
                if count_starts == 0: continue
                end_counts = this_sector_moves.groupby(['end_sector_x_bin', 'end_sector_y_bin']).size().reset_index(name='count_ends')
                start_sector_flat_idx = (start_sector_y - 1) * 16 + (start_sector_x - 1)
                for _, row2 in end_counts.iterrows():
                    end_sector_x, end_sector_y, value = row2['end_sector_x_bin'], row2['end_sector_y_bin'], row2['count_ends']
                    if 0 < end_sector_x <= 16 and 0 < end_sector_y <= 12:
                        transition_matrices_array[start_sector_flat_idx][end_sector_y - 1][end_sector_x - 1] = value / count_starts

        xT_final = np.zeros((12, 16))
        num_iterations = 10
        xT_matrices = {}
        for i in range(num_iterations):
            shoot_expected_payoff = calculations['goal_probability'] * calculations['shot_probability']
            move_prob_reshaped = calculations['move_probability'].reshape(192)
            move_expected_payoff = move_prob_reshaped * np.sum(transition_matrices_array * xT_final, axis=(1, 2))
            move_expected_payoff_intermediate = move_expected_payoff.reshape(12, 16)
            xT_final = shoot_expected_payoff + move_expected_payoff_intermediate
            
            xT_binned_iter = pitch.bin_statistic(dataframe['location.x'], dataframe['location.y'], statistic='count', bins=bins, normalize=False)
            xT_binned_iter["statistic"] = xT_final
            xT_matrices[f'xT Matrix after {i+1} Moves'] = xT_binned_iter
        
        calculations['xT_matrices'] = xT_matrices
    
    return calculations

def generate_specific_plot(calculations, plot_title, df):
    """
    Generates a single plot based on a title and pre-calculated statistics.
    """
    plots = {}
    pitch = Pitch(line_color='black', pitch_type='custom', pitch_length=105, pitch_width=68, line_zorder=2)
    
    if plot_title == 'Pass Heatmap':
        binned_stat = calculations.get('move_binned')
        title = 'Pass Heatmap' # Correct title for the dictionary lookup
        cmap = 'Blues'
        show_labels = False
    elif plot_title == 'Shot Heatmap':
        binned_stat = calculations.get('shot_binned')
        title = 'Shot Heatmap' # Correct title for the dictionary lookup
        cmap = 'Greens'
        show_labels = False
    elif plot_title == 'Goal Heatmap':
        binned_stat = calculations.get('goal_binned')
        title = 'Goal Heatmap' # Correct title for the dictionary lookup
        cmap = 'Reds'
        show_labels = False
    elif plot_title == 'Move Probability':
        binned_stat = calculations.get('move_prob_binned')
        title = 'Move Probability' # Correct title for the dictionary lookup
        cmap = 'Blues'
        show_labels = False
    elif plot_title == 'Shot Probability':
        binned_stat = calculations.get('shot_prob_binned')
        title = 'Shot Probability' # Correct title for the dictionary lookup
        cmap = 'Greens'
        show_labels = False
    elif plot_title == 'Goal Probability':
        binned_stat = calculations.get('goal_prob_binned')
        title = 'Goal Probability' # Correct title for the dictionary lookup
        cmap = 'Reds'
        show_labels = False
    elif 'xT Matrix after' in plot_title:
        xT_matrices = calculations.get('xT_matrices', {})
        binned_stat = xT_matrices.get(plot_title)
        title = plot_title
        cmap = 'Oranges'
        show_labels = True
    else:
        binned_stat = None
        title = "Plot Not Found"
        cmap = 'Greys'
        show_labels = False

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(15, 8))
    pitch.draw(ax=ax)
    
    if binned_stat is None:
        ax.set_title(title, fontsize=20)
    else:
        pcm = pitch.heatmap(binned_stat, cmap=cmap, edgecolor='grey', ax=ax)
        ax_cbar = fig.add_axes([0.95, 0.1, 0.03, 0.8])
        plt.colorbar(pcm, cax=ax_cbar)
        
        if show_labels:
            pitch.label_heatmap(binned_stat, color='blue', fontsize=9,
                                 ax=ax, ha='center', va='center', str_format="{0:,.2f}", zorder=3)
        fig.suptitle(title, fontsize=20)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return image_base64, title

@app.route('/')
def index():
    """Renders the main page with the form."""
    teams = [
        (11566, 'Rapid Bucureşti'),
        (11564, 'Dinamo Bucureşti'),
        (11565, 'FCS Bucureşti'),
        (11611, 'CFR Cluj'),
        (26233, 'Universitatea Craiova'),
        (61242, 'Farul Constanţa'),
        (11634, 'Botoşani'),
        (11571, 'Oţelul'),
        (11663, 'Unirea Slobozia'),
        (11886, 'Poli Iaşi'),
        (60392, 'AS FC Buzău'),
        (32854, 'Sepsi'),
        (60390, 'Petrolul 52'),
        (30817, 'UTA Arad'),
        (55427, 'Hermannstadt')
    ]
    return render_template_string(HTML_FORM, teams=teams)

@app.route('/analyze', methods=['POST', 'GET'])
def analyze():
    """
    Handles form submission and plot selection, runs the analysis, and renders the results page.
    """
    selected_team_id_str = request.values.get('team_id_selection')
    selected_plot_title = request.values.get('plot_title')

    if selected_team_id_str == 'UCLUJ':
        processed_df = df_raw.copy()
        processed_df = processed_df[processed_df["team.id"] != 60374] # Filter for opponents
        title = "All Games (Detailed Analysis)"
        team_id_context = 'UCLUJ'
    else:
        selected_team_id = int(selected_team_id_str)
        processed_df = df_raw.copy()
        processed_df = processed_df[processed_df["team.id"] == selected_team_id] 
        team_name = next((name for tid, name in TEAMS if tid == selected_team_id), f"Team {selected_team_id}")
        title = f"Game {team_name}"
        team_id_context = selected_team_id_str

    if processed_df.empty:
        message = f"No data available for the selected game. Please go back and try again."
        return render_template_string(HTML_RESULTS, plots={}, title=title, message=message, team_id_selection=team_id_context)

    processed_df['type.secondary'] = processed_df['type.secondary'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    
    cache_key = (team_id_context)
    if cache_key not in calculation_cache:
        calculation_cache[cache_key] = run_all_calculations(processed_df)

    plot_titles = ['Pass Heatmap', 'Shot Heatmap', 'Goal Heatmap', 'Move Probability', 'Shot Probability', 'Goal Probability']
    plot_titles.extend([f'xT Matrix after {i+1} Moves' for i in range(10)])
    
    if not selected_plot_title:
        selected_plot_title = plot_titles[0]
    
    plot_url, plot_title_result = generate_specific_plot(calculation_cache[cache_key], selected_plot_title, processed_df)
    plots_to_display = {plot_title_result: plot_url}
    
    return render_template_string(HTML_RESULTS, plots=plots_to_display, title=title, plot_titles=plot_titles, selected_plot_title=selected_plot_title, team_id_selection=team_id_context, descriptions=PLOT_DESCRIPTIONS)

if __name__ == '__main__':
    app.run(debug=True)
