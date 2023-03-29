import os
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from io import BytesIO
import plotly.graph_objs as go
import altair as alt
import gspread
import numpy as np
import folium
import pyarrow as pa
import plotly.express as px
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from oauth2client.service_account import ServiceAccountCredentials
import json



# Load the JSON credentials from the Streamlit secret
service_account_info = json.loads(st.secrets['GOOGLE_SERVICE_ACCOUNT_CREDENTIALS'])

# Set up the credentials and authorize the application
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = service_account.Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)



# Open the spreadsheet by name and select the "Citizen" tab
spreadsheet_name = 'Pourashava_Dashboard_V3'

# Open the Google Sheet and select the "Overview" tab
sheet = client.open('Pourashava_Dashboard_V3')
worksheet = sheet.worksheet('Overview')


data = worksheet.get_all_records(empty2zero=True)
df = pd.DataFrame(data).dropna()

# Streamlit app
import streamlit as st

st.set_page_config(page_title="IUGIP Dashboard", page_icon=":smiley:", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        max-width: 1200px;
        margin: auto;
        }
    </style>
    """,
    unsafe_allow_html=True,
)




st.markdown("<h1 style='font-size:25px; color:white;'>Urban Governance Improvement Action Plan (UGIAP) for IUGIP</h1>", unsafe_allow_html=True)


####### ---------------------------------


# Create the sidebar with options
option = st.sidebar.selectbox('Select an option', ['About', 'Overview', 'Area wise Performance', 'Pourashava Pefromance', 'Indicators'])

# Description option
if option == 'About':
    #st.header('XXXX')
    st.write("The Government of the People's Republic of Bangladesh will receive a loan towards the cost of the Improving Urban Governance and Infrastructure Program (IUGIP) from Asian Development Bank (ADB) and Agence Francaise De Development (AFD). It is expected that the fund or loan will be received from ADB and AFD for the 50 target Pourashavas (PSs), for enhancing the scope of the Pourashavas. The project is going to launch implementation activities in 2023 and planned to be implemented over a period of 6 (six) years with ending in 2029.")
    st.write('The Dashbaord - Text to be added')

# Scatter Plot option
elif option == 'Overview':
    st.write('Location of the Participating Pourashava')
    
    ###### Create a map centered on Bangladesh
    m = folium.Map(location=[23.6850, 90.3563], zoom_start=7)

    # Define marker colors for each grade value
    grade_colors = {'A+': 'darkgreen', 'A': 'lightgreen', 'B': 'lightblue', 'C': 'gray', 'D': 'lightgray'}

    # Add markers for each pourashava in the dataframe
    for index, row in df.iterrows():
        name = row['Pourashava']
        lat = float(row['Lat'])
        lon = float(row['Lon'])
        score = row['Total Score']
        grade = row['Grade']
        color = grade_colors.get(grade, 'black')  # Get the marker color based on the grade value
        popup_msg = f"{name}<br>Score: {score}<br>Grade: {grade}"
        folium.Marker(location=[lat, lon], tooltip=name, popup=popup_msg, icon=folium.Icon(color=color)).add_to(m)

    # Display the map using the folium_static function
    folium_static(m)
    ### ------------------

    ##### Sort the DataFrame by Total Score and create a pie chart
    df_sorted = df.sort_values('Total Score', ascending=False)
            
    # Count the number of Pourashavas in each Grade category
    counts = df.groupby('Grade')['Pourashava'].nunique()
    
    # Create the pie chart
    fig_pie = go.Figure(data=[go.Pie(labels=counts.index, values=counts.values)])

    # Move the legend of the pie chart to the bottom
    fig_pie.update_layout(legend=dict(orientation='h', yanchor='top', y=0, xanchor='left', x=0.25))
            
    # Create a horizontal bar chart of the Grade counts
    Grade_counts = df['Grade'].value_counts().reindex(['A+', 'A', 'B', 'C', 'D'])
    fig_bar = go.Figure(data=[go.Bar(x=Grade_counts.values, y=Grade_counts.index, orientation='h')])
            
  
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<h3 style='text-align: center;font-size: 15px;'>A+ (Outstanding), A (Very Good), B (Good), C (Average), D (Unsatisfactory)</h3>", unsafe_allow_html=True)
     
    # Top 10 pourashvas

    st.markdown("<h2 style='font-size: 20px;'>Top 10 Pourashavas</h2>", unsafe_allow_html=True)
    df_sorted = df_sorted.reset_index(drop=False).head(10)
    df_sorted.index += 1
    st.table(df_sorted[['Pourashava', 'Total Score', 'Grade']])


###### Area wise Performance
elif option == 'Area wise Performance':

    ###### 1. Citizen Awareness and Participation
    st.markdown("<h2 style='font-size: 20px;'>Citizen Awareness and Participation (Max Score 17)</h2>", unsafe_allow_html=True)

    # Create the pivot table
    pivot_table = pd.pivot_table(df, values='Citizen', index='Pourashava', sort=False)

    # Create the chart
    chart = alt.Chart(pivot_table.reset_index()).mark_bar().encode(
        x=alt.X('Pourashava', axis=alt.Axis(title=None)),
        y=alt.Y('Citizen:Q', axis=alt.Axis(title='Score')),
        tooltip=['Pourashava', 'Citizen:Q']
    ).properties(
        width=800,
        height=300
    )

    # Set the axis labels
    chart = chart.configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        labelAngle=-90
    )

    # Display the chart
    st.altair_chart(chart, use_container_width=True)

    ###### 2. Urban Planning
    st.markdown("<h2 style='font-size: 20px;'>Urban Planning (Max Score 7)</h2>", unsafe_allow_html=True)

    # Create a pivot table with the Planning scores for each Pourashava
    pivot_table = pd.pivot_table(df, values='Planning', index='Pourashava', sort=False)

    # Create the chart
    chart = alt.Chart(pivot_table.reset_index()).mark_bar().encode(
        x=alt.X('Pourashava', axis=alt.Axis(title=None)),
        y=alt.Y('Planning:Q', axis=alt.Axis(title='Score')),
        tooltip=['Pourashava', 'Planning:Q']
    ).properties(
        width=800,
        height=300
    )

    # Set the axis labels
    chart = chart.configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        labelAngle=-90
    )

    # Display the chart
    st.altair_chart(chart, use_container_width=True)


    ###### 3. Equity and Inclusiveness of Women and Urban Poor
    st.markdown("<h2 style='font-size: 20px;'>Equity and Inclusiveness of Women and Urban Poor (Max Score 8)</h2>", unsafe_allow_html=True)

    pivot_table = pd.pivot_table(df, values='Equity', index='Pourashava')

    # Create the chart
    chart = alt.Chart(pivot_table.reset_index()).mark_bar().encode(
        x=alt.X('Pourashava', axis=alt.Axis(title=None)),
        y=alt.Y('Equity:Q', axis=alt.Axis(title='Score')),
        tooltip=['Pourashava', 'Equity:Q']
    ).properties(
        width=800,
        height=300
    )

    # Set the axis labels
    chart = chart.configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        labelAngle=-90
    )

    # Display the chart
    st.altair_chart(chart, use_container_width=True)


    ###### 4. Enhancement of Local Resource Mobilization
    st.markdown("<h2 style='font-size: 20px;'>Enhancement of Local Resource Mobilization (Max Score 18)</h2>", unsafe_allow_html=True)
    pivot_table = pd.pivot_table(df, values='Resources', index='Pourashava')
            
            # Create the chart
    chart = alt.Chart(pivot_table.reset_index()).mark_bar().encode(
                x=alt.X('Pourashava', axis=alt.Axis(title=None)),
                y=alt.Y('Resources:Q', axis=alt.Axis(title='Score')),
                tooltip=['Pourashava', 'Resources:Q']
            ).properties(
                width=800,
                height=300
            )

    # Set the axis labels
    chart = chart.configure_axis(
                labelFontSize=12,
                titleFontSize=14,
                labelAngle=-90
            )
            # Display the chart
    st.altair_chart(chart, use_container_width=True)


    ###### 5. Financial Management, Accountibility and Sustainability
    st.markdown("<h2 style='font-size: 20px;'>Financial Management, Accountibility and Sustainability (Max Score 18)</h2>", unsafe_allow_html=True)
    pivot_table = pd.pivot_table(df, values='FIN MGT', index='Pourashava')

    # Create the chart
    chart = alt.Chart(pivot_table.reset_index()).mark_bar().encode(
        x=alt.X('Pourashava', axis=alt.Axis(title=None)),
        y=alt.Y('FIN MGT:Q', axis=alt.Axis(title='Score')),
        tooltip=['Pourashava', 'FIN MGT:Q']
    ).properties(
        width=800,
        height=300
    )

    # Set the axis labels
    chart = chart.configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        labelAngle=-90
    )

    # Display the chart
    st.altair_chart(chart, use_container_width=True)

    ###### 6. Operation and Maintenance and Managemen
    st.markdown("<h2 style='font-size: 20px;'>Operation and Maintenance (O&M) and Management (Max Score 8)</h2>", unsafe_allow_html=True)
    pivot_table = pd.pivot_table(df, values='O&M', index='Pourashava')

    # Create the chart
    chart = alt.Chart(pivot_table.reset_index()).mark_bar().encode(
        x=alt.X('Pourashava', axis=alt.Axis(title=None)),
        y=alt.Y('O&M:Q', axis=alt.Axis(title='Score')),
        tooltip=['Pourashava', 'O&M:Q']
    ).properties(
        width=800,
        height=300
    )

    # Set the axis labels
    chart = chart.configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        labelAngle=-90
    )

    # Display the chart
    st.altair_chart(chart, use_container_width=True)

    ###### 7. Condition Survey & Prepared Road and Drain Network and Other Assest Inventory
    st.markdown("<h2 style='font-size: 20px;'>Condition Survey & Prepared Road and Drain Network and Other Assest Inventory (Max Score 4)</h2>", unsafe_allow_html=True)
    pivot_table = pd.pivot_table(df, values='Survey', index='Pourashava')

    # Create the chart
    chart = alt.Chart(pivot_table.reset_index()).mark_bar().encode(
        x=alt.X('Pourashava', axis=alt.Axis(title=None)),
        y=alt.Y('Survey:Q', axis=alt.Axis(title='Score')),
        tooltip=['Pourashava', 'Survey:Q']
    ).properties(
        width=800,
        height=300
    )

    # Set the axis labels
    chart = chart.configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        labelAngle=-90
    )

    # Display the chart
    st.altair_chart(chart, use_container_width=True)

    ###### 8. Administrative Transparency
    st.markdown("<h2 style='font-size: 20px;'>Administrative Transparency (Max Score 6)</h2>", unsafe_allow_html=True)
    pivot_table = pd.pivot_table(df, values='Transparency', index='Pourashava')

    # Create the chart
    chart = alt.Chart(pivot_table.reset_index()).mark_bar().encode(
        x=alt.X('Pourashava', axis=alt.Axis(title=None)),
        y=alt.Y('Transparency:Q', axis=alt.Axis(title='Score')),
        tooltip=['Pourashava', 'Transparency:Q']
    ).properties(
        width=800,
        height=300
    )

    # Set the axis labels
    chart =chart.configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        labelAngle=-90
    )
    # Display the chart
    st.altair_chart(chart, use_container_width=True)

    ###### 9. Keeping Essential Pourashava Services Fuctional
    st.markdown("<h2 style='font-size: 20px;'>Keeping Essential Pourashava Services Fuctional (Max Score 14)</h2>", unsafe_allow_html=True)
    pivot_table = pd.pivot_table(df, values='Services', index='Pourashava')

    # Create the chart
    chart = alt.Chart(pivot_table.reset_index()).mark_bar().encode(
        x=alt.X('Pourashava', axis=alt.Axis(title=None)),
        y=alt.Y('Services:Q', axis=alt.Axis(title='Score')),
        tooltip=['Pourashava', 'Services:Q']
    ).properties(
        width=800,
        height=300
    )

    # Set the axis labels
    chart = chart.configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        labelAngle=-90
    )

    # Display the chart
    st.altair_chart(chart, use_container_width=True)
        
# Count the number of Pourashavas in each Grade category


###Pourashava Pefromance
elif option == 'Pourashava Pefromance':
   # Open the Google Sheet and select the "Overview" tab
    sheet = client.open('Pourashava_Dashboard_V3')
    worksheet = sheet.worksheet('Overview')

    # Convert the worksheet data to a Pandas dataframe
    data = worksheet.get_all_records(empty2zero=True)
    df = pd.DataFrame(data).dropna()

    # Define the options for the sidebar buttons
    options = ["Performance Overview", "Pourashava Wise Perfromance Evaluation"]

    # Create a sidebar with options to filter by pourashava
    selected_pourashava = st.sidebar.selectbox('Select a pourashava:', sorted(df['Pourashava'].unique()))

    # Filter the dataframe by pourashava
    filtered_df = df[df['Pourashava'] == selected_pourashava]

    
    # # Create the bar chart using plotly
    ### 1. Citizen Awareness and Participation
    fig = go.Figure()
    x_values = ['Citizen Awareness and Participation']
    y_values = filtered_df['Citizen'], filtered_df['Citizen Max Score']

    fig.add_trace(go.Bar(x=x_values, y=y_values[0], offsetgroup=0, name = 'Achievement', marker=dict(color='dark blue')))
    fig.add_trace(go.Bar(x=x_values, y=y_values[1], offsetgroup=1, name = 'Max Score', marker=dict(color='light blue')))

    fig.update_layout(title={'text': 'Performance Comparison for ' + selected_pourashava, 'font': {'size': 24}}, yaxis_title='Score')
    st.plotly_chart(fig, use_container_width=True)


    ### 2. Urban Planning
    fig = go.Figure()
    x_values = ['Urban Planning']
    y_values = filtered_df['Planning'], filtered_df['Planning Max Score']

    fig.add_trace(go.Bar(x=x_values, y=y_values[0], offsetgroup=0, name = 'Achievement', marker=dict(color='dark blue')))
    fig.add_trace(go.Bar(x=x_values, y=y_values[1], offsetgroup=1, name = 'Max Score', marker=dict(color='light blue')))

    fig.update_layout( yaxis_title='Score')
    st.plotly_chart(fig, use_container_width=True)


    ### 3. Equity and Inclusiveness of Women and Urban Poor
    fig = go.Figure()
    x_values = ['Equity and Inclusiveness of Women and Urban Poor']
    y_values = filtered_df['Equity'], filtered_df['Equity Max Score']

    fig.add_trace(go.Bar(x=x_values, y=y_values[0], offsetgroup=0, name = 'Achievement', marker=dict(color='dark blue')))
    fig.add_trace(go.Bar(x=x_values, y=y_values[1], offsetgroup=1, name = 'Max Score', marker=dict(color='light blue')))

    fig.update_layout( yaxis_title='Score')
    st.plotly_chart(fig, use_container_width=True)

    ### 4. Enhancement of Local Resource Mobilization 
    fig = go.Figure()
    x_values = ['Enhancement of Local Resource Mobilization ']
    y_values = filtered_df['Resources'], filtered_df['Resources Max Score']

    fig.add_trace(go.Bar(x=x_values, y=y_values[0], offsetgroup=0, name = 'Achievement', marker=dict(color='dark blue')))
    fig.add_trace(go.Bar(x=x_values, y=y_values[1], offsetgroup=1, name = 'Max Score', marker=dict(color='light blue')))

    fig.update_layout( yaxis_title='Score')
    st.plotly_chart(fig, use_container_width=True)

    ### 5. Financial Management, Accountibility and Sustainability 
    fig = go.Figure()
    x_values = ['Financial Management, Accountibility and Sustainability ']
    y_values = filtered_df['FIN MGT'], filtered_df['FIN MGT Max Score']

    fig.add_trace(go.Bar(x=x_values, y=y_values[0], offsetgroup=0, name = 'Achievement', marker=dict(color='dark blue')))
    fig.add_trace(go.Bar(x=x_values, y=y_values[1], offsetgroup=1, name = 'Max Score', marker=dict(color='light blue')))

    fig.update_layout( yaxis_title='Score')
    st.plotly_chart(fig, use_container_width=True)


    ### 6. Operation and Maintenance (O&M) and Management
    fig = go.Figure()
    x_values = ['Operation and Maintenance (O&M) and Management']
    y_values = filtered_df['O&M'], filtered_df['O&M Max Score']

    fig.add_trace(go.Bar(x=x_values, y=y_values[0], offsetgroup=0, name = 'Achievement', marker=dict(color='dark blue')))
    fig.add_trace(go.Bar(x=x_values, y=y_values[1], offsetgroup=1, name = 'Max Score', marker=dict(color='light blue')))

    fig.update_layout( yaxis_title='Score')
    st.plotly_chart(fig, use_container_width=True)


    ### 7. Condition Survey & Prepared Road and Drain Network and Other Assest Inventory 
    fig = go.Figure()
    x_values = ['Condition Survey & Prepared Road and Drain Network and Other Assest Inventory ']
    y_values = filtered_df['Survey'], filtered_df['Survey Max Score']

    fig.add_trace(go.Bar(x=x_values, y=y_values[0], offsetgroup=0, name = 'Achievement', marker=dict(color='dark blue')))
    fig.add_trace(go.Bar(x=x_values, y=y_values[1], offsetgroup=1, name = 'Max Score', marker=dict(color='light blue')))

    fig.update_layout( yaxis_title='Score')
    st.plotly_chart(fig, use_container_width=True)

    ### 8. Administrative Transparency
    fig = go.Figure()
    x_values = ['Administrative Transparency']
    y_values = filtered_df['Transparency'], filtered_df['Transparency Max Score']

    fig.add_trace(go.Bar(x=x_values, y=y_values[0], offsetgroup=0, name = 'Achievement', marker=dict(color='dark blue')))
    fig.add_trace(go.Bar(x=x_values, y=y_values[1], offsetgroup=1, name = 'Max Score', marker=dict(color='light blue')))

    fig.update_layout( yaxis_title='Score')
    st.plotly_chart(fig, use_container_width=True)


    ### 9. Keeping Essential Pourashava Services Fuctional 
    fig = go.Figure()
    x_values = ['Keeping Essential Pourashava Services Fuctional ']
    y_values = filtered_df['Services'], filtered_df['Services Max Score']

    fig.add_trace(go.Bar(x=x_values, y=y_values[0], offsetgroup=0, name = 'Achievement', marker=dict(color='dark blue')))
    fig.add_trace(go.Bar(x=x_values, y=y_values[1], offsetgroup=1, name = 'Max Score', marker=dict(color='light blue')))

    fig.update_layout( yaxis_title='Score')
    st.plotly_chart(fig, use_container_width=True)

elif option == 'Indicators':

    # Open the Google Sheet and select the "Overview" tab
    sheet = client.open('Pourashava_Dashboard_V3')
    worksheet = sheet.worksheet('Citizen')

    # Convert the worksheet data to a Pandas dataframe
    data = worksheet.get_all_records(empty2zero=True)
    df = pd.DataFrame(data).dropna()

    # Create a sidebar with options to filter by pourashava
    selected_pourashava = st.sidebar.selectbox('Select a pourashava:', sorted(df['Pourashava'].unique()))

    # Filter the dataframe by pourashava
    filtered_df = df[df['Pourashava'] == selected_pourashava]

    st.markdown(f"<h2 style='font-size: 20px;'>Indicators for {selected_pourashava}</h2>", unsafe_allow_html=True)
        
    st.markdown(f"<h2 style='font-size: 20px;'> Citizen Awareness and Participation</h2>", unsafe_allow_html=True)

    # Select the columns you want to show
    columns = ['TLCC Formation', 'TLCC Meetings per Year', 'TLCC Meeting Minutes', 'WC Formation', 'Meeting held in each Ward/3 months', 'WC Meeting Record', 'Citizen Charter Preparation', 'Citizen Charter Display', 'IGRC Fomration', 'Complaint Box Installation', 'GRC Meeting', 'GRC disclosed to TLCC']

    # Show the filtered data in a table without index
    st.table(filtered_df[columns].reset_index(drop=True).style.hide_index())

    ######## 2. Urban Planning 

    # Open the Google Sheet and select the "Overview" tab
    sheet = client.open('Pourashava_Dashboard_V3')
    worksheet = sheet.worksheet('Planning')

    # Convert the worksheet data to a Pandas dataframe
    data = worksheet.get_all_records(empty2zero=True)
    df = pd.DataFrame(data).dropna()

    # Filter the dataframe by pourashava
    filtered_df = df[df['Pourashava'] == selected_pourashava]

    st.markdown(f"<h2 style='font-size: 20px;'> Urban Planning </h2>", unsafe_allow_html=True)

    # Select the columns you want to show
    columns = ['PDP Status',	'Master Plan Status',	'Development Activities Control']

    # Show the filtered data in a table without index
    st.table(filtered_df[columns].reset_index(drop=True).style.hide_index())


    ######## 3. Equity and Inclusiveness of Women and Urban Poor

    # Open the Google Sheet and select the "Overview" tab
    sheet = client.open('Pourashava_Dashboard_V3')
    worksheet = sheet.worksheet('Equity')

    # Convert the worksheet data to a Pandas dataframe
    data = worksheet.get_all_records(empty2zero=True)
    df = pd.DataFrame(data).dropna()

    # Filter the dataframe by pourashava
    filtered_df = df[df['Pourashava'] == selected_pourashava]

    st.markdown(f"<h2 style='font-size: 20px;'> Equity and Inclusiveness of Women and Urban Poor </h2>", unsafe_allow_html=True)

    # Select the columns you want to show
    columns = ['STC Formation Status', 'STC Meeting', 'PRAP & GAP Status', 'PRAP & GAP Implementation Status', 'SIC Selection Status', 'SIC Formation Status', 'SIC Meeting']


    # Show the filtered data in a table without index
    st.table(filtered_df[columns].reset_index(drop=True).style.hide_index())



    ######## 4. Enhancement of Local Resource Mobilization 

    # Open the Google Sheet and select the "Overview" tab
    sheet = client.open('Pourashava_Dashboard_V3')
    worksheet = sheet.worksheet('Resources')

    # Convert the worksheet data to a Pandas dataframe
    data = worksheet.get_all_records(empty2zero=True)
    df = pd.DataFrame(data).dropna()

    # Filter the dataframe by pourashava
    filtered_df = df[df['Pourashava'] == selected_pourashava]

    st.markdown(f"<h2 style='font-size: 20px;'> Enhancement of Local Resource Mobilization </h2>", unsafe_allow_html=True)

    # Select the columns you want to show
    columns = ['Holding Tax Assessment in 5 year (if Due)', 'Interim Holding Tax Assessment every year','Increased Holding Tax Collection','Indirect Tax Status', 'Indirect Tax Collection','Tax Software Status','Tax Bil Procedue','Water Tariff Plan','Water Tariff Asset','Water Bill Collection']


    # Show the filtered data in a table without index
    st.table(filtered_df[columns].reset_index(drop=True).style.hide_index())


    ######## 5. Financial Management, Accountibility and Sustainability  

    # Open the Google Sheet and select the "Overview" tab
    sheet = client.open('Pourashava_Dashboard_V3')
    worksheet = sheet.worksheet('FIN MGT')

    # Convert the worksheet data to a Pandas dataframe
    data = worksheet.get_all_records(empty2zero=True)
    df = pd.DataFrame(data).dropna()

    # Filter the dataframe by pourashava
    filtered_df = df[df['Pourashava'] == selected_pourashava]

    st.markdown(f"<h2 style='font-size: 20px;'> Financial Management, Accountibility and Sustainability  </h2>", unsafe_allow_html=True)

    # Select the columns you want to show
    columns = ['Budget Peparation', 'Annual Financial Statement', 'Audit', 'Computerized Accounting System', 'Staff Salary Payment', 'Electric and Telephone Bills Payment', 'Loans Payment', 'Fixed Assed Inventory', 'Rental and lease Value Property', 'Fixed Asset Database']


    # Show the filtered data in a table without index
    st.table(filtered_df[columns].reset_index(drop=True).style.hide_index())


    ######## 6. Operation and Maintenance (O&M) and Management  

    # Open the Google Sheet and select the "Overview" tab
    sheet = client.open('Pourashava_Dashboard_V3')
    worksheet = sheet.worksheet('O&M')

    # Convert the worksheet data to a Pandas dataframe
    data = worksheet.get_all_records(empty2zero=True)
    df = pd.DataFrame(data).dropna()

    # Filter the dataframe by pourashava
    filtered_df = df[df['Pourashava'] == selected_pourashava]

    st.markdown(f"<h2 style='font-size: 20px;'> Operation and Maintenance (O&M) and Management </h2>", unsafe_allow_html=True)

    # Select the columns you want to show
    columns = ['O&M Plan', 'O&M Budget Spending', 'TLCC Satisfaction Level (O&M Plan)', 'Priority O&M Activities Implementation', 'Mobile Maintenance Team Fuctional', 'TLCC Satisfaction Level (O&M)']

    # Show the filtered data in a table without index
    st.table(filtered_df[columns].reset_index(drop=True).style.hide_index())



    ######## 7. Condition Survey & Prepared Road and Drain Network and Other Assest Inventory   

    # Open the Google Sheet and select the "Overview" tab
    sheet = client.open('Pourashava_Dashboard_V3')
    worksheet = sheet.worksheet('Survey')

    # Convert the worksheet data to a Pandas dataframe
    data = worksheet.get_all_records(empty2zero=True)
    df = pd.DataFrame(data).dropna()

    # Filter the dataframe by pourashava
    filtered_df = df[df['Pourashava'] == selected_pourashava]

    st.markdown(f"<h2 style='font-size: 20px;'> Condition Survey & Prepared Road and Drain Network and Other Assest Inventory  </h2>", unsafe_allow_html=True)

    # Select the columns you want to show
    columns = ['Condition Survey for Road', 'Condition Survey for Drains', 'Condition Survey for Other Assets']



    # Show the filtered data in a table without index
    st.table(filtered_df[columns].reset_index(drop=True).style.hide_index())


    ######## 8. Administrative Transparency    

    # Open the Google Sheet and select the "Overview" tab
    sheet = client.open('Pourashava_Dashboard_V3')
    worksheet = sheet.worksheet('Transparency')

    # Convert the worksheet data to a Pandas dataframe
    data = worksheet.get_all_records(empty2zero=True)
    df = pd.DataFrame(data).dropna()

    # Filter the dataframe by pourashava
    filtered_df = df[df['Pourashava'] == selected_pourashava]

    st.markdown(f"<h2 style='font-size: 20px;'> Administrative Transparency   </h2>", unsafe_allow_html=True)

    # Select the columns you want to show
    columns = ['SC Meeting', 'Training Program', 'Pourashava Website']

    # Show the filtered data in a table without index
    st.table(filtered_df[columns].reset_index(drop=True).style.hide_index())

    ######## 9. Keeping Essential Pourashava Services Fuctional    

    # Open the Google Sheet and select the "Overview" tab
    sheet = client.open('Pourashava_Dashboard_V3')
    worksheet = sheet.worksheet('Services')

    # Convert the worksheet data to a Pandas dataframe
    data = worksheet.get_all_records(empty2zero=True)
    df = pd.DataFrame(data).dropna()

    # Filter the dataframe by pourashava
    filtered_df = df[df['Pourashava'] == selected_pourashava]

    st.markdown(f"<h2 style='font-size: 20px;'> Keeping Essential Pourashava Services Fuctional </h2>", unsafe_allow_html=True)

    # Select the columns you want to show
    columns = ['SWM Action Plan', 'Solid Waste Collection', 'TLCC Satisfaction Assessment (SWM)', 'Drainage Maintenance Action Plan', 'Primary Drains Cleaning', 'TLCC Satisfaction Assessment (Drains)', 'Street Lighting Action Plan', 'Street Light Fuctional', 'TLCC Satisfaction Assessment (Streetlight)', 'Sanitation Action Plan', 'Pubic Toilets', 'TLCC Satisfaction (Public Toilets)']



    # Show the filtered data in a table without index
    st.table(filtered_df[columns].reset_index(drop=True).style.hide_index())


    

    
  

    
    







    pass
