"""
JouleLens — CSS Styles Module.
All custom CSS for the dark-themed energy profiler UI.
"""

CSS = """
<style>
/* ===== Google Fonts ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');

/* ===== Root Variables ===== */
:root {
    --bg-primary: #0D1117;
    --bg-secondary: #161B22;
    --bg-card: #1C2128;
    --border-color: #30363D;
    --accent-green: #00FF88;
    --accent-blue: #58A6FF;
    --accent-warning: #F0A500;
    --accent-danger: #FF4B4B;
    --accent-success: #3FB950;
    --text-primary: #E6EDF3;
    --text-secondary: #8B949E;
}

/* ===== Global Overrides ===== */
.stApp {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

[data-testid="stHeader"] {
    background-color: var(--bg-primary) !important;
}

/* ===== Sidebar ===== */
[data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-color) !important;
}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown span,
[data-testid="stSidebar"] .stMarkdown li {
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] label,
[data-testid="stSidebar"] .stNumberInput label {
    color: var(--text-secondary) !important;
}

/* ===== Metric Cards ===== */
[data-testid="stMetric"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-left: 4px solid var(--accent-green) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
}

[data-testid="stMetric"] label {
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
}

[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 1.4rem !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    word-break: break-all !important;
}

[data-testid="stMetric"] [data-testid="stMetricValue"] > div {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
}

/* ===== Buttons ===== */
.stButton > button {
    background: linear-gradient(135deg, #00FF88, #00CC6A) !important;
    color: #0D1117 !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 0.6rem 1.5rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 15px rgba(0, 255, 136, 0.15) !important;
}

.stButton > button:hover {
    box-shadow: 0 0 25px rgba(0, 255, 136, 0.4) !important;
    transform: translateY(-1px) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ===== Download Buttons ===== */
.stDownloadButton > button {
    background: linear-gradient(135deg, #58A6FF, #388BFD) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    border: none !important;
}

.stDownloadButton > button:hover {
    box-shadow: 0 0 20px rgba(88, 166, 255, 0.4) !important;
}

/* ===== Text Area (Code Editor) ===== */
.stTextArea textarea {
    font-family: 'JetBrains Mono', monospace !important;
    background-color: #0D1117 !important;
    color: #E6EDF3 !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
}

.stTextArea label {
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
}

/* ===== DataFrames ===== */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
}

/* ===== Expanders ===== */
[data-testid="stExpander"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
}

[data-testid="stExpander"] summary {
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}

/* ===== Select Boxes ===== */
[data-testid="stSelectbox"] label {
    color: var(--text-secondary) !important;
}

/* ===== Radio Buttons ===== */
.stRadio label {
    color: var(--text-secondary) !important;
}

.stRadio [role="radiogroup"] label {
    color: var(--text-primary) !important;
}

/* ===== Tabs ===== */
.stTabs [data-baseweb="tab-list"] {
    background-color: var(--bg-secondary) !important;
    border-radius: 8px !important;
}

.stTabs [data-baseweb="tab"] {
    color: var(--text-secondary) !important;
}

.stTabs [aria-selected="true"] {
    color: var(--accent-green) !important;
}

/* ===== Score Badges ===== */
.score-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 12px 24px;
    border-radius: 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: 1px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.score-a {
    background: linear-gradient(135deg, #00FF88, #00CC6A);
    color: #0D1117;
    box-shadow: 0 4px 20px rgba(0, 255, 136, 0.3);
}

.score-b {
    background: linear-gradient(135deg, #3FB950, #2EA043);
    color: #0D1117;
    box-shadow: 0 4px 20px rgba(63, 185, 80, 0.3);
}

.score-c {
    background: linear-gradient(135deg, #F0A500, #D4940A);
    color: #0D1117;
    box-shadow: 0 4px 20px rgba(240, 165, 0, 0.3);
}

.score-d {
    background: linear-gradient(135deg, #FF8C00, #E07800);
    color: #0D1117;
    box-shadow: 0 4px 20px rgba(255, 140, 0, 0.3);
}

.score-f {
    background: linear-gradient(135deg, #FF4B4B, #DA3633);
    color: #FFFFFF;
    box-shadow: 0 4px 20px rgba(255, 75, 75, 0.3);
}

/* ===== Gradient Header ===== */
.gradient-header {
    background: linear-gradient(135deg, #00FF88 0%, #58A6FF 50%, #00FF88 100%);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-shift 4s ease infinite;
    font-family: 'Inter', sans-serif;
    font-weight: 900;
    font-size: 2.4rem;
    margin-bottom: 0.2rem;
    line-height: 1.2;
}

@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.gradient-subtitle {
    color: var(--text-secondary);
    font-family: 'Inter', sans-serif;
    font-size: 1.1rem;
    font-weight: 400;
    margin-bottom: 2rem;
    animation: fadeInUp 1s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(15px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* ===== Live Pulsing Dot ===== */
.live-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: #00FF88;
    margin-right: 8px;
    animation: pulse 1.5s ease-in-out infinite;
    vertical-align: middle;
}

.live-dot-red {
    background-color: #FF4B4B;
}

.live-dot-yellow {
    background-color: #F0A500;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.5); }
    70% { box-shadow: 0 0 0 10px rgba(0, 255, 136, 0); }
    100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }
}

/* ===== Metric Card Custom ===== */
.metric-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-left: 4px solid var(--accent-green);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}

.metric-card:hover {
    border-color: var(--accent-green);
    box-shadow: 0 4px 20px rgba(0, 255, 136, 0.1);
    transform: translateY(-2px);
    cursor: pointer;
}

.metric-card .metric-label {
    color: var(--text-secondary);
    font-size: 0.85rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

.metric-card .metric-value {
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
}

.metric-card .metric-delta {
    color: var(--accent-green);
    font-size: 0.8rem;
    margin-top: 4px;
}

/* ===== Callout Boxes ===== */
.energy-callout {
    background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(63, 185, 80, 0.08));
    border: 1px solid rgba(0, 255, 136, 0.3);
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    margin: 1rem 0;
}

.energy-callout .callout-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 800;
    color: #00FF88;
}

.energy-callout .callout-label {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-top: 4px;
}

.danger-callout {
    background: linear-gradient(135deg, rgba(255, 75, 75, 0.1), rgba(218, 54, 51, 0.08));
    border: 1px solid rgba(255, 75, 75, 0.3);
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    margin: 1rem 0;
}

/* ===== Footer ===== */
.joulelens-footer {
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.8rem;
    padding: 2rem 0 1rem 0;
    border-top: 1px solid var(--border-color);
    margin-top: 3rem;
    font-family: 'Inter', sans-serif;
}

/* ===== Optimization Cards ===== */
.opt-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 10px;
}

.opt-card .opt-title {
    color: var(--text-primary);
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 6px;
}

.opt-card .opt-desc {
    color: var(--text-secondary);
    font-size: 0.9rem;
    line-height: 1.5;
}

.technique-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-right: 6px;
    background-color: rgba(88, 166, 255, 0.15);
    color: #58A6FF;
    border: 1px solid rgba(88, 166, 255, 0.3);
}

.impact-high {
    background-color: rgba(255, 75, 75, 0.15);
    color: #FF4B4B;
    border: 1px solid rgba(255, 75, 75, 0.3);
}

.impact-medium {
    background-color: rgba(240, 165, 0, 0.15);
    color: #F0A500;
    border: 1px solid rgba(240, 165, 0, 0.3);
}

.impact-low {
    background-color: rgba(63, 185, 80, 0.15);
    color: #3FB950;
    border: 1px solid rgba(63, 185, 80, 0.3);
}

/* ===== Sidebar Logo ===== */
.sidebar-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00FF88, #58A6FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}

.sidebar-version {
    color: var(--text-secondary);
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    opacity: 0.7;
}

/* ===== Divider ===== */
.styled-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-color), transparent);
    border: none;
    margin: 1.5rem 0;
}

/* ===== Scrollbar ===== */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: var(--bg-primary);
}
::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #484F58;
}

/* ===== Number Input ===== */
.stNumberInput label {
    color: var(--text-secondary) !important;
}

/* ===== Code Blocks ===== */
.stCode, code {
    font-family: 'JetBrains Mono', monospace !important;
}

/* ===== Status Messages ===== */
[data-testid="stStatusWidget"] {
    background-color: var(--bg-card) !important;
}

/* ===== Toast/Alerts ===== */
.stAlert {
    border-radius: 8px !important;
}

/* ===== Carbon Widget ===== */
.carbon-widget {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 14px 16px;
    margin: 8px 0;
}

.carbon-widget .cw-label {
    font-size: 0.75rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.carbon-widget .cw-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
}
</style>
"""
