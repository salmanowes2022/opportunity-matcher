import streamlit as st

def apply_custom_css():
    """Apply custom CSS styling to improve the UI"""
    
    st.markdown("""
    <style>
    /* Main app styling */
    .main {
        padding-top: 2rem;
    }
    
    /* Custom title styling */
    .custom-title {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(90deg, #1f4e79 0%, #2c5aa0 50%, #3498db 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    /* Subtitle styling */
    .custom-subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Card-like containers */
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
    
    /* Success/warning/error styling */
    .success-card {
        background: linear-gradient(90deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .warning-card {
        background: linear-gradient(90deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .info-card {
        background: linear-gradient(90deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #2980b9 0%, #1f4e79 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Form styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 5px;
        border: 2px solid #e1e8ed;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 1px #3498db;
    }
    
    /* Metric styling */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        text-align: center;
        border: 1px solid #e1e8ed;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        border: 1px solid #e1e8ed;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3498db;
        color: white;
    }
    
    /* Progress indicators */
    .progress-bar {
        background: #e1e8ed;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #3498db 0%, #2ecc71 100%);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Footer styling */
    .custom-footer {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 2rem;
        border-top: 1px solid #e1e8ed;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, delta=None, help_text=None):
    """Create a styled metric card"""
    
    delta_html = ""
    if delta:
        delta_color = "green" if delta > 0 else "red" if delta < 0 else "gray"
        delta_symbol = "↗" if delta > 0 else "↘" if delta < 0 else "→"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.8rem;">{delta_symbol} {abs(delta):.1%}</div>'
    
    help_html = ""
    if help_text:
        help_html = f'<div style="color: #666; font-size: 0.8rem; margin-top: 0.5rem;">{help_text}</div>'
    
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">{title}</div>
        <div style="font-size: 2rem; font-weight: 700; color: #2c3e50;">{value}</div>
        {delta_html}
        {help_html}
    </div>
    """, unsafe_allow_html=True)

def create_status_indicator(score):
    """Create a visual status indicator based on score"""
    
    if score >= 0.7:
        color = "#28a745"
        status = "Excellent Match"
        icon = "🎯"
    elif score >= 0.5:
        color = "#ffc107"
        status = "Good Match"
        icon = "👍"
    else:
        color = "#dc3545"
        status = "Needs Work"
        icon = "⚠️"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, {color}15 0%, {color}25 100%);
        border-left: 4px solid {color};
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        text-align: center;
    ">
        <div style="font-size: 2rem;">{icon}</div>
        <div style="font-size: 1.2rem; font-weight: 600; color: {color};">{status}</div>
        <div style="font-size: 1.5rem; font-weight: 700; margin-top: 0.5rem;">{score:.1%}</div>
    </div>
    """, unsafe_allow_html=True)