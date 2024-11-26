import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import folium_static
import random

# Page settings
st.set_page_config(
    page_title="Location Tracking",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styles
st.markdown("""
<style>
    .main {
        padding: 0 !important;
    }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    .hour-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        padding: 10px;
        justify-content: flex-start;
    }
    .hour-button {
        padding: 8px 16px;
        border: none;
        border-radius: 5px;
        color: white;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s;
        width: calc(33.33% - 4px);
        text-align: center;
        margin-bottom: 5px;
    }
    .hour-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    [data-testid="stSidebar"] {
        width: 25% !important;
    }
    [data-testid="stSidebarContent"] {
        padding: 1rem;
    }
    .stButton button {
        width: 100%;
    }
    .data-section {
        margin-top: 20px;
        border-top: 1px solid #eee;
        padding-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Function to load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('location_logs.csv')  # Updated path to look for CSV in the same directory
        df['timestamp'] = pd.to_datetime('2024-' + df['timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return empty DataFrame if file not found

# Session state initialization
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = None
if 'selected_hours' not in st.session_state:
    st.session_state.selected_hours = set()

# Load data
try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Sidebar (25% section)
with st.sidebar:
    st.title("📅 Calendar")
    
    # Date selection
    available_dates = df['timestamp'].dt.date.unique()
    selected_date = st.date_input(
        "Select Date",
        value=st.session_state.selected_date if st.session_state.selected_date else available_dates.min(),
        min_value=available_dates.min(),
        max_value=available_dates.max()
    )
    
    # Clear selected hours if date changes
    if selected_date != st.session_state.selected_date:
        st.session_state.selected_hours = set()
        st.session_state.selected_date = selected_date
    
    # Get data for selected date
    filtered_df = df[df['timestamp'].dt.date == selected_date]
    
    if not filtered_df.empty:
        # Hour buttons
        st.markdown("### ⏰ Hours")
        
        # Fixed colors for each hour
        hour_colors = {
            0: '#8B0000', 1: '#006400', 2: '#00008B', 3: '#008B8B',
            4: '#8B008B', 5: '#FF8C00', 6: '#9932CC', 7: '#2F4F4F',
            8: '#556B2F', 9: '#8B4513', 10: '#1E90FF', 11: '#9400D3',
            12: '#228B22', 13: '#B22222', 14: '#483D8B', 15: '#00CED1',
            16: '#4682B4', 17: '#5F9EA0', 18: '#2E8B57', 19: '#6B8E23',
            20: '#8A2BE2', 21: '#7B68EE', 22: '#191970', 23: '#800000'
        }
        
        # Available hours for the selected date
        available_hours = sorted(filtered_df['timestamp'].dt.hour.unique())
        
        # Custom CSS for button colors
        button_css = ""
        for hour in available_hours:
            button_css += f"""
                [data-testid="baseButton-secondary"][aria-label="hour_{hour}"] {{
                    background-color: {hour_colors[hour]} !important;
                    color: white !important;
                    border: none !important;
                }}
                [data-testid="baseButton-secondary"][aria-label="hour_{hour}"]:hover {{
                    background-color: {hour_colors[hour]} !important;
                    filter: brightness(120%);
                }}
            """
        
        st.markdown(f"""
        <style>
            {button_css}
            [data-testid="baseButton-secondary"] {{
                font-weight: bold !important;
            }}
        </style>
        """, unsafe_allow_html=True)
        
        # "All" button
        if st.button("🕐 All Hours", 
                    type="primary" if not st.session_state.selected_hours else "secondary",
                    use_container_width=True,
                    key="all_hours"):
            st.session_state.selected_hours = set()
            st.rerun()
        
        # Hour buttons
        cols = st.columns(3)
        for i, hour in enumerate(available_hours):
            col_idx = i % 3
            with cols[col_idx]:
                if st.button(
                    f"{hour:02d}:00",
                    key=f"hour_{hour}",
                    type="primary" if hour in st.session_state.selected_hours else "secondary",
                    use_container_width=True,
                    help=f"View data for {hour:02d}:00"
                ):
                    if hour in st.session_state.selected_hours:
                        st.session_state.selected_hours.remove(hour)
                    else:
                        st.session_state.selected_hours.add(hour)
                    st.rerun()
        
        # Data list section
        st.markdown('<div class="data-section">', unsafe_allow_html=True)
        st.markdown("### 📝 Data List")
        
        # Display filtered data based on selected hours
        if st.session_state.selected_hours:
            display_df = filtered_df[filtered_df['timestamp'].dt.hour.isin(st.session_state.selected_hours)]
            hours_str = ", ".join(f"{hour:02d}:00" for hour in sorted(st.session_state.selected_hours))
            st.markdown(f"#### 🕐 Selected Times: {hours_str}")
        else:
            display_df = filtered_df
            st.markdown("#### 📊 All Data")
        
        # Format the timestamp for display
        display_df = display_df.copy()
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        st.dataframe(
            display_df[['timestamp', 'latitude', 'longitude', 'zip_file']].sort_values('timestamp'),
            use_container_width=True,
            height=300
        )
        
        # CSV export button
        csv = display_df[['timestamp', 'latitude', 'longitude', 'zip_file']].to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"location_data_{selected_date}.csv",
            mime="text/csv",
            key="download_csv"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("No data available for this date")

# Map (75% section)
if not filtered_df.empty:
    m = folium.Map(
        location=[filtered_df['latitude'].mean(), filtered_df['longitude'].mean()],
        zoom_start=13
    )
    
    # Fixed colors for each hour
    hour_colors = {
        0: '#8B0000', 1: '#006400', 2: '#00008B', 3: '#008B8B',
        4: '#8B008B', 5: '#FF8C00', 6: '#9932CC', 7: '#2F4F4F',
        8: '#556B2F', 9: '#8B4513', 10: '#1E90FF', 11: '#9400D3',
        12: '#228B22', 13: '#B22222', 14: '#483D8B', 15: '#00CED1',
        16: '#4682B4', 17: '#5F9EA0', 18: '#2E8B57', 19: '#6B8E23',
        20: '#8A2BE2', 21: '#7B68EE', 22: '#191970', 23: '#800000'
    }
    
    # Filter and draw routes by hour
    if st.session_state.selected_hours:
        # Draw routes for selected hours
        for hour in sorted(st.session_state.selected_hours):
            hour_data = filtered_df[filtered_df['timestamp'].dt.hour == hour]
            if not hour_data.empty:
                # Draw route
                coordinates = hour_data[['latitude', 'longitude']].values.tolist()
                folium.PolyLine(
                    coordinates,
                    weight=3,
                    color=hour_colors[hour],
                    opacity=0.8
                ).add_to(m)
                
                # Add markers
                for _, row in hour_data.iterrows():
                    folium.CircleMarker(
                        [row['latitude'], row['longitude']],
                        radius=8,
                        color=hour_colors[hour],
                        fill=True,
                        popup=f"Time: {row['timestamp']}<br>ZIP: {row['zip_file']}",
                        tooltip=f"{row['timestamp'].strftime('%H:%M:%S')}"
                    ).add_to(m)
    else:
        # Draw routes for all hours
        for hour in available_hours:
            hour_data = filtered_df[filtered_df['timestamp'].dt.hour == hour]
            if not hour_data.empty:
                coordinates = hour_data[['latitude', 'longitude']].values.tolist()
                folium.PolyLine(
                    coordinates,
                    weight=3,
                    color=hour_colors[hour],
                    opacity=0.8
                ).add_to(m)
                
                # Add markers
                for _, row in hour_data.iterrows():
                    folium.CircleMarker(
                        [row['latitude'], row['longitude']],
                        radius=8,
                        color=hour_colors[hour],
                        fill=True,
                        popup=f"Time: {row['timestamp']}<br>ZIP: {row['zip_file']}",
                        tooltip=f"{row['timestamp'].strftime('%H:%M:%S')}"
                    ).add_to(m)
    
    # Display map
    folium_static(m, width=None, height=800)
else:
    st.warning("No data available for selected date")
