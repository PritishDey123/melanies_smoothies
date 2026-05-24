# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import requests
import json

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get both columns (IMPORTANT)
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert to pandas
pd_df = my_dataframe.to_pandas()

# Multiselect
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),   # ✅ FIX: use list
    max_selections=5
)

if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get SEARCH_ON value
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'
        ].iloc[0]

        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition Information')

        # ✅ FIX: use search_on (not fruit_chosen)
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        # ✅ FIX: avoid .json() error
        sf_df = st.dataframe(
            data=json.loads(smoothiefroot_response.text),
            use_container_width=True
        )

    # Insert query
    my_insert_stmt = """ 
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('""" + ingredients_string + """','""" + name_on_order + """')
    """

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
