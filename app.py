# streamlit run app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px
from PIL import Image

session = st.sidebar.selectbox("Section", ["Welcome!", "Overview", "Features", "Debt and Salary"])
st.title('PhD Dashboard')

if session == "Welcome!":

    st.sidebar.subheader("Welcome to my dashboard!")

    # image
    image = Image.open('phd.jpg')
    st.image(image, width = 700)
    st.subheader("Introduction")
    st.write("""
    This is a dashboard about doctorate in the United States. The main goal is to answer the following questions:

    - The number of doctorate-granting institutions and doctorate recipients over time.
    - The distribution of educational resources by states in 2017.
    - The debt level of doctorate recipients for each field of study over time.
    - The proportion of sex and field of study for doctorate recipients over time.
    - The median expected salary for doctorate recipients by employment sectors.
    
    This dashboard is divided into the following four parts:
    - Welcome!
    - Overview
    - Features
    - Debt and Salary
    
    The codes can be found at Mingxuan Yang's [Github repository](https://github.com/Mingxuan-Yang/PhD-Dashboard).""")
    
if session == "Overview":
    
    df1 = pd.read_excel('Data/sed17-sr-tab002.xlsx').iloc[4:, :-2].reset_index(drop = True)
    df1.columns = ['Year', 'No. of Institutions', 'No. of Doctorates']

    #sidebar
    st.sidebar.subheader("Overview")
    year_range =  st.sidebar.slider('Range of Years:', min(df1['Year']), max(df1['Year']), (min(df1['Year']), max(df1['Year'])))

    years = []
    year = year_range[0]
    while year <= year_range[1]:
        years.append(year)
        year += 1
    df1 = df1[df1['Year'].isin(years)]

    # figure
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(go.Scatter(x = df1['Year'],
                            y = df1['No. of Institutions'],
                            marker = dict(color='#0099ff'),
                            mode='lines+markers',
                            name = 'Number of Institutions'),secondary_y = False)
    fig1.add_trace(go.Scatter(x = df1['Year'],
                            y = df1['No. of Doctorates'],
                            marker = dict(color='#404040'),
                            mode='lines+markers',
                            name = 'Number of Doctorates'), secondary_y = True)
    fig1.update_xaxes(title_text = 'Year', gridcolor = 'whitesmoke', linecolor = 'black')
    fig1.update_yaxes(title_text = 'No. of Doctorate-granting Institutions', secondary_y = False, 
                    gridcolor = 'whitesmoke', linecolor = 'black')
    fig1.update_yaxes(title_text = 'No. of Doctorate Recipients', secondary_y = True, 
                    linecolor = 'black')
    fig1.update_layout({'plot_bgcolor': 'rgb(255,255,255)', 'paper_bgcolor': 'rgb(255,255,255)'},
                        width = 700, height = 450,)

    st.subheader('Doctorate-granting Institutions and Doctorate Recipients in the US')
    st.plotly_chart(fig1)

if session == 'Features':

    # import data
    df2 = (
        pd.read_excel('Data/sed17-sr-tab006.xlsx').
        iloc[5:, :].
        reset_index(drop = True).
        replace({'D': None}).
        rename(columns = {'Table 6': 'State'})
    )

    # combine male and female columns
    name = ['Total', 'Life Sciences', 'Physical Sciences and Earth Sciences', 'Mathematics and Computer Sciences', 
            'Psychology and Social Sciences', 'Engineering', 'Education', 'Humanities and Arts', 'Other']
    for i in range(9):
        df2[name[i]] = df2.iloc[:, (i*2+1):(i*2+3)].sum(axis = 1, skipna = False) 
    df2 = df2[['State'] + name]

    # add state code
    state_code = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv')[['code', 'state']]
    df2 = pd.merge(state_code, df2, left_on = 'state', right_on = 'State').drop('state', axis = 1)

    colors = ['#FEFFFE', '#E9EBF8', '#B4B8C5', '#A5A299', '#8D818C', '#3C4F76', '#383F51', '#2E6171', '#7F557D']
    df3b = pd.read_excel('Data/sed17-sr-tab015.xlsx').iloc[[49, 53, 57, 60, 67, 77, 83, 88, 94,98, 102, 105, 112, 122, 128, 133], 1:-1].reset_index(drop = True)
    df3b.columns = [str(i) for i in range(2008, 2018)]
    df3b['Field of Study'] = name[1:]*2
    df3b['Sex'] = ['Male']*len(name[1:]) + ['Female']*len(name[1:])

    # sidebar
    st.sidebar.subheader("Map Parameter:")
    field = st.sidebar.selectbox("Field of Study:", name)
    st.sidebar.subheader("Pie Chart Parameter:")
    year2 =  st.sidebar.slider('Year:', 2008, 2017, 2017)
    
    # figure
    dff = df2[['code', 'State', field]].dropna(axis = 0)
    
    fig2 = go.Figure(data = go.Choropleth(
        locations = dff['code'],
        z = dff[field].astype(float),
        locationmode = 'USA-states',
        colorscale = 'Reds',
        autocolorscale = False,
        marker_line_color = 'black',
        text = '<b>' + dff['State'] + '</b><br>' + field + ' Field: ' + dff[field].astype(int).astype(str)
    ))
    
    fig2.update_layout(
        width = 700, height = 500,
        geo = dict(
            scope = 'usa',
            projection = go.layout.geo.Projection(type = 'albers usa'),
            showlakes = True, lakecolor = 'rgb(255, 255, 255)')
    )

    fig3 = px.sunburst(df3b, path = ['Sex', 'Field of Study'], values = str(year2), color = 'Field of Study',
                      color_discrete_map = dict(zip(name[1:] + ['(?)'], colors)))
    fig3.update_layout(width = 600, height = 600)

    st.subheader('Number of Doctorate recipients in the US by State in 2017')
    st.plotly_chart(fig2)

    st.subheader('Proportion of Sex and Major Field')
    st.plotly_chart(fig3)

if session == 'Debt and Salary':

    name = ['Total', 'Life Sciences', 'Physical Sciences and Earth Sciences', 'Mathematics and Computer Sciences', 
            'Psychology and Social Sciences', 'Engineering', 'Education', 'Humanities and Arts', 'Other']
    df3a_ = pd.read_excel('Data/sed17-sr-tab039.xlsx').iloc[8:, :]
    df3a = df3a_.iloc[1::5, :]
    for i in range(2, 5):
        df3a = pd.concat([df3a, df3a_.iloc[i::5, :]])
    df3a.columns = ['Debt Level'] + [str(i) for i in range(2008, 2018)]
    df3a['Field of Study'] = name[1:] * 4
    df3a = df3a.reset_index(drop = True).replace({'$10,001–$30,000': '$10,001 - 30,000'})


    df4 = pd.read_excel('Data/sed17-sr-tab049.xlsx').iloc[[5,9,13,14,18,20,21,22,23], :].reset_index(drop = True)
    df4.columns = ['Field of Study', 'Academe', 'Industry or Business', 'Government', 'Nonprofit Organization', 'Other or Unknown']
    df4 = df4.replace({'Other non-S&E fieldsd': 'Other'}).melt(id_vars = 'Field of Study', var_name = 'Employment Sector', value_name = 'Median Expected Salary')
    sectors = list(df4['Employment Sector'].unique())

    # sidebar
    st.sidebar.subheader("Bar Plot Parameter:")
    year3 =  st.sidebar.slider('Year:', 2008, 2017, 2017)
    st.sidebar.subheader("Scatter Plot Parameter:")
    secs = st.sidebar.multiselect('Employment Sectors:', sectors, default = sectors)
    
    # figure
    ddf = df3a[['Debt Level', str(year3), 'Field of Study']]
    ddf = pd.merge(ddf, ddf.groupby('Field of Study').agg(np.sum).reset_index(), on = 'Field of Study')
    ddf[str(year3)] = round(ddf[str(year3) + '_x']/ddf[str(year3) + '_y']*100, 2)
    fig4 = px.bar(ddf[['Debt Level', str(year3), 'Field of Study']],
                 x = 'Field of Study', 
                 y = str(year3), 
                 color = "Debt Level", 
                 template = 'plotly_white',
                 color_discrete_map = {'No debt':'#D4AFB9', '$10,000 or less':'#D1CFE2', '$10,001 - 30,000':'#9CADCE', '$30,001 or more': '#837A75'}
                )
    fig4.update_yaxes(title_text = "Percentage of Debt Level in " + str(year3))
    fig4.update_xaxes(title_text = '')

    dff2 = df4[df4['Employment Sector'].isin(secs)]
    
    fig5 = px.scatter(
        data_frame = dff2,
        x = dff2['Field of Study'],
        y = dff2['Median Expected Salary'],
        color = dff2['Employment Sector'],
        template = 'plotly_white'
    )
    
    fig5.update_yaxes(linecolor = 'black')
    fig5.update_xaxes(linecolor = 'black')
    fig5.update_layout(width = 700, height = 550)
    
    st.subheader('Debt Level for Each Field of Study')
    st.plotly_chart(fig4)

    st.subheader('Median Expected Salary for Doctorate Recipients in the US')
    st.plotly_chart(fig5)