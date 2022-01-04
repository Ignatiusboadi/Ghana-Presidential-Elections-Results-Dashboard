from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash
import dash_daq as daq
import pandas as pd
import plotly.express as px

ghana = pd.read_excel('Ghana Elections 1992-2008.xlsx', sheet_name=None)
ghana_add = pd.read_excel('Ghana Elections data.xlsx', sheet_name = None)

for key in ghana.keys():
    gh_data = pd.DataFrame(columns=['Candidate', 'Votes', 'Share%', 'Constituency', 'Year', 'Region', 'Party', 'Rank'])
    cur_data = ghana[key]
    for group, frame in cur_data.groupby('Constituency'):
        frame['Rank'] = frame['Share%'].rank(ascending=False)
        gh_data = pd.concat([gh_data, frame])
    ghana[key] = gh_data
    
for key in ghana_add.keys():
    cur_data = ghana_add[key]
    if key != '2020':
        cur_data.replace({'ahafo':'brongahafo', 'bono':'brongahafo','bonoeast':'brongahafo', 'westernnorth':'western',
                   'northeast':'northern', 'savannah':'northern','oti':'volta'}, inplace=True)
    
    cur_data['Year'] = [key for i in range(cur_data.shape[0])]
    ghana[key] = cur_data
    
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                title='Ghana Election Results', update_title='Loading...') 

years = ['1996', '2000', '2000a', '2004', '2008', '2008a', '2012', '2016', '2020']

options = [{'label':year[:-1]+' Round Off', 'value':year} if year.endswith('a') else {'label':year, 'value':year}\
           for year in years]

region_values = ['ashanti', 'brongahafo', 'central', 'eastern', 'greateraccra', 'northern', 'uppereast',
           'upperwest', 'volta', 'western']

region_labels = ['Ashanti', 'Brong-Ahafo', 'Central', 'Eastern', 'Greater Accra', 'Northern', 'Upper East', 'Upper West',
               'Volta', 'Western']

new_region_labels = ['Ashanti', 'Ahafo', 'Bono', 'Central', 'Eastern', 'Northern', 'Western', 'North East', 'Upper East', 
               'Upper West','Greater Accra', 'Volta', 'Bono East', 'Savannah', 'Oti', 'Western North']

new_region_values = ['ashanti', 'ahafo', 'bono', 'central', 'eastern', 'northern', 'western', 'northeast', 'uppereast', 
                     'upperwest', 'greateraccra','volta', 'bonoeast', 'savannah', 'oti', 'westernnorth']

region_options = [{'label':region_labels[i], 'value':region_values[i]} for i in range(10)]

new_region_options = [{'label':new_region_labels[i], 'value':new_region_values[i]} for i in range(16)]

regional_options = {'1996': region_options,'2000': region_options,'2000a': region_options,'2004': region_options,
 '2008': region_options,'2008a': region_options,'2012': region_options,'2016': region_options,
 '2020': new_region_options}


colors = {'toggle':'#B8860B', 'paperbg':'AliceBlue', 'plotbg':'#F0FFFF'}

app.layout = html.Div(style={'background-color':'lavender', 'height':'85%', 'borderTopRightRadius':'15px', 
                             'border':'2px solid', 'borderTopLeftRadius':'15px'}, 
                      
    children=[html.Div(style={'borderTopRightRadius':'15px', 'border':'2px solid','background-color':'gold',
                              'borderTopLeftRadius':'15px'},
                                         
    children=[html.Img(src='/assets/ghana1.jpg', alt='Ghana Flag', className='two Columns',
                       style={'width':'15%', 'height':'7%', 'float':'left','borderTopLeftRadius':'15px'}),
              
     html.H1(children='RESULTS OF PRESIDENTIAL ELECTIONS IN GHANA FROM 1996 TO 2008', style={'textAlign':'center', 
            'font-size':'300%', 'verticalAlign':'center'}, className='eight columns'),
              
    html.Img(src='/assets/ghana1.jpg', alt='Ghana Flag', className='two Columns',
                       style={'width':'15%', 'height':'7%', 'float':'right','borderTopRightRadius':'15px'})], className='row'),
    html.Hr(),
    html.Div(children=[
                    html.Div([dcc.Dropdown(id='year_select', options=options, value='2020', clearable=False)], 
                                 className='four columns'),
                       
                    html.Div([dcc.Dropdown(id='region_select', placeholder='Select a Region', clearable=False)], 
                                 className='four columns'),

                    html.Div([dcc.Dropdown(id='constituency_select', placeholder='Select a Constituency', clearable=False)], 
                                 className='four columns')],
             className='row'),
    html.Hr(),
    html.Div(children=[
    html.Div([daq.ToggleSwitch(id='nat_switch', value=False, label=['Bar Chart', 'Pie Chart'], style={'width':'70%'},
                                color=colors['toggle']),
              dcc.Graph(id='national_graph', style={'height':'100%'})], className='four columns'), 

    html.Div([daq.ToggleSwitch(id='reg_switch', value=False, label=['Bar Chart', 'Pie Chart'], 
                                              style={'width':'70%'}, color=colors['toggle']),
              dcc.Graph(id='regional_graph', style={'height':'100%'})], className='four columns'),

    html.Div([daq.ToggleSwitch(id='const_switch', value=False, label=['Bar Chart', 'Pie Chart'], 
                                              style={'width':'70%'}, color=colors['toggle']),
              dcc.Graph(id='constituency_graph', style={'height':'100%'})], className='four columns')],
             
             className='row')
])

@app.callback(Output(component_id='region_select', component_property='options'),
              Output(component_id='region_select', component_property='value'),
              Output(component_id='constituency_select', component_property='options'),
              Output(component_id='constituency_select', component_property='value'),
              Input(component_id='region_select', component_property='value'),
              Input(component_id='year_select', component_property='value'))
def set_constituencies(region, year):
    reg_options = regional_options[year]

    if region == None or region not in ghana[year]['Region'].to_list():
        region = 'ashanti'

    const = ghana[year][ghana[year]['Region'] == region]['Constituency'].unique()
    const_options = [{'label':consts, 'value':consts} for consts in const]
    
    return reg_options, region, const_options, const_options[0]['label']


@app.callback(Output(component_id='national_graph', component_property='figure'),
                Output(component_id='regional_graph', component_property='figure'),
                Output(component_id='constituency_graph', component_property='figure'),
                Input(component_id='year_select', component_property='value'),
                Input(component_id='region_select', component_property='value'),
                Input(component_id='constituency_select', component_property='value'),
                Input(component_id='nat_switch', component_property='value'),
                Input(component_id='reg_switch', component_property='value'),
                Input(component_id='const_switch', component_property='value'))                
def display_graph(year, region, constituency, nat_switch, reg_switch, const_switch):
    const_data = ghana[year][ghana[year]['Constituency'] == constituency].sort_values('Candidate', ascending=False)
    cand_parties = dict(zip(const_data['Candidate'], const_data['Party']))
    
    regional_data = ghana[year][ghana[year]['Region'] == region].groupby('Candidate')['Votes'].sum().reset_index()
    regional_data['Share%'] = regional_data['Votes'].apply(lambda x:100*x/regional_data['Votes'].sum())
    regional_data['Party'] = regional_data['Candidate'].apply(lambda x:cand_parties[x])
    regional_data.sort_values('Candidate', ascending=False, inplace=True)
    
    national_data = ghana[year].groupby('Candidate')['Votes'].sum().reset_index()
    national_data['Share%'] = national_data['Votes'].apply(lambda x:100*x/national_data['Votes'].sum())
    national_data['Party'] = national_data['Candidate'].apply(lambda x:cand_parties[x])
    national_data.sort_values('Candidate', ascending=False, inplace=True)
        
    if const_switch:
        const_fig = px.pie(const_data, 'Candidate', 'Votes', hover_data=['Party'], title='Constituency Results')
    else:
        const_fig = px.bar(const_data, 'Candidate', 'Votes', hover_data=['Party', 'Share%'], title='Constituency Results',
                       text='Votes')
    if reg_switch:
        reg_fig = px.pie(regional_data, 'Candidate', 'Votes', hover_data=['Party'], title='Regional Results')
    else:
        reg_fig = px.bar(regional_data, 'Candidate', 'Votes', hover_data=['Party', 'Share%'], title='Regional Results',
                     text='Votes')
    if nat_switch:
        nat_fig = px.pie(national_data, 'Candidate', 'Votes', hover_data=['Party'], title='National Results')
    else:
        nat_fig = px.bar(national_data, 'Candidate', 'Votes', hover_data=['Party', 'Share%'], title='National Results',
                     text='Votes')
    
    const_fig.update_layout(plot_bgcolor=colors['paperbg'], paper_bgcolor=colors['plotbg'], margin={'l':0,'r':15})
    reg_fig.update_layout(plot_bgcolor=colors['paperbg'], paper_bgcolor=colors['plotbg'], margin={'l':0,'r':15})
    nat_fig.update_layout(plot_bgcolor=colors['paperbg'], paper_bgcolor=colors['plotbg'], margin={'l':0,'r':15})
    
    return nat_fig, reg_fig, const_fig

if __name__ == '__main__':
    app.run_server()
