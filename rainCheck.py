import pandas as pd
import streamlit as st
import plotly.graph_objects as go

data = pd.read_csv('data/Rainfall_Data_LL.csv')

st.set_page_config(page_title='rainCheck - Rainfall Dashboard')
st.title('rainCheck: Rainfall Data Visualization Dashboard')
st.write("Welcome to rainCheck! Explore the rainfall data for various regions and timeframes.")

sidebar = st.sidebar
sidebar.title('Filters')

region_filter = sidebar.selectbox('Select Region', data['SUBDIVISION'].unique())
year_filter = sidebar.selectbox('Select Year', data['YEAR'].unique()[1:])
months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
month_range = sidebar.slider('Select Months', 1, 12, (1, 12))
sidebar.write("Selected Months:", f"{months[month_range[0]-1]} to {months[month_range[1]-1]}")

sidebar.title('Display Options')
df_show = sidebar.radio("Graph type", ["Show Dataframe", "Show Barplot"])

# Filter the data based on region and year
data_filtered = data[(data['SUBDIVISION'] == region_filter) & (data['YEAR'] == year_filter)]
coords = pd.DataFrame({
    'lat': data_filtered["Latitude"],
    'lon': data_filtered['Longitude']
})

# Select the data for the chosen month range
data_for_monthrange = data_filtered[months[month_range[0]-1:month_range[1]]]
selected_months = months[month_range[0]-1:month_range[1]]

st.write(f"Rainfall in {region_filter} for the duration {months[month_range[0]-1]} to {months[month_range[1]-1]} {year_filter}")

if df_show == "Show Dataframe":
    st.dataframe(data_for_monthrange)

elif df_show == "Show Barplot":
    total_rainfall = data_for_monthrange.sum().rename('Total Rainfall')

    fig = go.Figure(data=[go.Bar(x=total_rainfall.index, y=total_rainfall.values, name='Total Rainfall')])
    fig.update_layout(template='plotly_dark', title='Total Rainfall Bar Plot - YoY Comparison')

    # Year-over-Year comparison annotations
    yoy_annotations = []
    for i, month in enumerate(selected_months):
        # Get the rainfall data for the same month of the previous year if available
        prev_year_data = data[(data['SUBDIVISION'] == region_filter) & (data['YEAR'] == year_filter - 1)]
        if not prev_year_data.empty:
            prev_month_rainfall = prev_year_data[month].iloc[0]
            curr_month_rainfall = data_filtered[month].iloc[0]
            diff = curr_month_rainfall - prev_month_rainfall

            # Set the annotation text, color, and position
            diff_color = 'green' if diff > 0 else 'red' if diff < 0 else 'grey'
            annotation_text = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"
            yoy_annotations.append(
                dict(x=i, y=total_rainfall[i], text=annotation_text, showarrow=True, arrowhead=1, ax=0, ay=-40,
                        bgcolor=diff_color))

    fig.update_layout(annotations=yoy_annotations)

    st.plotly_chart(fig)

# Display the map with coordinates
st.map(coords, zoom=6)

