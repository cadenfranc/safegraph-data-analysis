import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title('Coding Challenge')

@st.cache
def initialize_data() -> pd.DataFrame:
    device_type = pd.read_parquet('parquet/device_type.parquet')
    poi = pd.read_parquet('parquet/poi.parquet')
    popularity_by_hour = pd.read_parquet('parquet/popularity_by_hour.parquet')
    related_same_day_brand = pd.read_parquet('parquet/related_same_day_brand.parquet')

    poi = pd.merge(poi, device_type, on='placekey', how='left')
    poi['location_name'] = poi['location_name'].apply(lambda name: name.lower())

    popularity_by_hour = pd.merge(popularity_by_hour, poi[['placekey', 'location_name']], on='placekey', how='left')
    related_same_day_brand = pd.merge(related_same_day_brand, poi[['placekey', 'location_name']], on='placekey', how='left')

    poi_lds = poi[(poi['location_name'].isin([
        'church of jesus christ of latter day saints',
        'the church of jesus christ of latter day saints']))]

    pbh_lds = popularity_by_hour[(popularity_by_hour['location_name'].isin([
        'church of jesus christ of latter day saints',
        'the church of jesus christ of latter day saints']))].groupby(by='hour').mean().reset_index()

    pbh_other = popularity_by_hour[(~popularity_by_hour['location_name'].isin([
        'church of jesus christ of latter day saints',
        'the church of jesus christ of latter day saints']))].groupby(by='hour').mean().reset_index()

    rsdb_lds = related_same_day_brand[(related_same_day_brand['location_name'].isin([
        'church of jesus christ of latter day saints',
        'the church of jesus christ of latter day saints']))]

    rsdb_other = related_same_day_brand[~(related_same_day_brand['location_name'].isin([
        'church of jesus christ of latter day saints',
        'the church of jesus christ of latter day saints']))]

    rsdb_lds_head = rsdb_lds.groupby(by='related_same_day_brand').sum().reset_index().sort_values(by='value', ascending=False).head(10)
    rsdb_other_head = rsdb_other.groupby(by='related_same_day_brand').sum().reset_index().sort_values(by='value', ascending=False).head(10)

    return poi_lds, pbh_lds, pbh_other, rsdb_lds_head, rsdb_other_head


def get_code(prompt : str) -> str:

    if prompt == 'Visits by Device Type':
        return """
poi = pd.read_parquet('parquet/poi.parquet')
device_type = pd.read_parquet('parquet/device_type.parquet')
poi = pd.merge(poi, device_type, on='placekey', how='left')
poi['location_name'] = poi['location_name'].apply(lambda name: name.lower())

poi = poi[(poi['location_name'].isin([
    'church of jesus christ of latter day saints',
    'the church of jesus christ of latter day saints']))]
"""

    if prompt == 'Popularity by Hour':
        return """
poi = pd.read_parquet('parquet/poi.parquet')
poi['location_name'] = poi['location_name'].apply(lambda name: name.lower())
popularity_by_hour = pd.read_parquet('parquet/popularity_by_hour.parquet')
popularity_by_hour = pd.merge(popularity_by_hour, poi[['placekey', 'location_name']], on='placekey', how='left')

pbh_lds = popularity_by_hour[(popularity_by_hour['location_name'].isin([
'church of jesus christ of latter day saints',
'the church of jesus christ of latter day saints']))].groupby(by='hour').mean().reset_index()

pbh_other = popularity_by_hour[(~popularity_by_hour['location_name'].isin([
'church of jesus christ of latter day saints',
'the church of jesus christ of latter day saints']))].groupby(by='hour').mean().reset_index()
"""

    if prompt == 'Related Same Day Brands':
        return """
poi = pd.read_parquet('parquet/poi.parquet')
poi['location_name'] = poi['location_name'].apply(lambda name: name.lower())
related_same_day_brand = pd.read_parquet('parquet/related_same_day_brand.parquet')
related_same_day_brand = pd.merge(related_same_day_brand, poi[['placekey', 'location_name']], on='placekey', how='left')

rsdb_lds = related_same_day_brand[(related_same_day_brand['location_name'].isin([
    'church of jesus christ of latter day saints',
    'the church of jesus christ of latter day saints']))]

rsdb_other = related_same_day_brand[~(related_same_day_brand['location_name'].isin([
    'church of jesus christ of latter day saints',
    'the church of jesus christ of latter day saints']))] 

rsdb_lds_head = rsdb_lds.groupby(by='related_same_day_brand').sum().reset_index().sort_values(by='value', ascending=False).head(10)
rsdb_other_head = rsdb_other.groupby(by='related_same_day_brand').sum().reset_index().sort_values(by='value', ascending=False).head(10)

"""

    else:
        return ''

def main():
    poi_lds, pbh_lds, pbh_other, rsdb_lds_head, rsdb_other_head = initialize_data()

    prompt = st.selectbox('Coding Challenge Question', 
        ['Visits by Device Type', 
         'Popularity by Hour',
         'Related Same Day Brands'])

    st.header('Data Visualization')

    if prompt == 'Visits by Device Type':
        dt_fig = go.Figure()
        dt_fig.add_trace(go.Box(y = poi_lds[poi_lds['region'] == 'UT']['value'].values, 
                                x = poi_lds[poi_lds['region'] == 'UT']['device_type'].values,
                                name = 'Utah',
                                boxpoints=False))

        dt_fig.add_trace(go.Box(y = poi_lds[poi_lds['region'] == 'GA']['value'].values, 
                                x = poi_lds[poi_lds['region'] == 'GA']['device_type'].values,
                                name = 'Georgia',
                                boxpoints=False))

        dt_fig.update_yaxes(range=[-5, 45])

        dt_fig.update_layout(
            title='Visits by Device Type in Utah and Georgia<br><sup>Double click on graph to toggle zoom level.</sup>',
            xaxis_title='Device Type',
            yaxis_title='Number of Visitors',
            boxmode='group'
            )

        st.write("""This figure is a representation of the number of visitors to The Church of Jesus Christ of Latter-day Saints buildings
                    by device type. """)

        st.write(dt_fig)

        st.write('Places of Interest')
        st.write(poi_lds.head(5))

    if prompt == 'Popularity by Hour':
        pbh_fig = go.Figure()

        pbh_fig.add_trace(go.Scatter(x=pbh_lds['hour'], y=pbh_lds['popularity_by_hour'],
                            mode='lines+markers',
                            name='The Church of Jesus Christ<br>of Latter Day Saints',
                            line_shape='spline'))

        pbh_fig.add_trace(go.Scatter(x=pbh_other['hour'], y=pbh_other['popularity_by_hour'],
                            mode='lines+markers',
                            name='Other Churches',
                            line_shape='spline'))

        pbh_fig.update_layout(title='Popularity by Hour of Churches',
                    xaxis_title='Hour',
                    yaxis_title='Average Number of Visitors')

        st.write("""This visualization depicts the difference between the average number
                    of visitors to the Church of Jesus Christ of Latter Day Saints and
                    other churches. """)

        st.write(pbh_fig)

        col1, col2 = st.columns(2)
        col1.write("The Church of Jesus Christ of Latter Day Saints")
        col1.write(pbh_lds.head(5))
        col2.write("Other Churches")
        col2.write(pbh_other.head(5))


    if prompt == 'Related Same Day Brands':
        rsdb_fig = go.Figure()

        rsdb_fig.add_trace(go.Bar(x=rsdb_other_head['related_same_day_brand'].values,
                                y=rsdb_other_head['value'].values,
                                name='Other Churches'))

        rsdb_fig.add_trace(go.Bar(x=rsdb_lds_head['related_same_day_brand'].values,
                                y=rsdb_lds_head['value'].values,
                                name='The Church of Jesus Christ<br>of Latter Day Saints'))

        rsdb_fig.update_layout(
            title='Top 10 Related Same Day Brand Visits by Church<br><sup>Data Collected from 10/1/2021 to 01/01/2022.</sup>',
            xaxis_title='Location',
            yaxis_title='Total Number of Visitors',
            boxmode='group'
            )

        st.write("""This visual depicts the total number of visitors to some
                    of the most visited locations for the Church of Jesus Christ of Latter Day Saints
                    and other churches.""")

        st.write(rsdb_fig)

        col1, col2 = st.columns(2)
        col1.write("The Church of Jesus Christ of Latter Day Saints")
        col1.write(rsdb_lds_head.head(5))
        col2.write("Other Churches")
        col2.write(rsdb_other_head.head(5))

        st.write(""" This analysis might also be conducted on the different 
        brands visited between temples, seminary buildings, and meetinghouses. Although
        there is no feature that strictly differentiates these, we might be able to 
        deduce the difference through their open hours, popularity by hour, 
        or the average number of visitors to each.
        """)

    st.header('**Data Wrangling**')
    st.code(get_code(prompt), language='python')

if __name__ == "__main__":
    main()

