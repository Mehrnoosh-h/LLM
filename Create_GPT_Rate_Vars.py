'''
The perpuse of this script is to get the annotated tweets file and create the county and state GPT rate variables.
'''

import pandas as pd
import numpy as np
import os
import glob
import addfips
af = addfips.AddFIPS()


#  *************
#  * FUNCTIONS *
#  *************
def add_fips_codes(df):
    # Create state_fips column
    df['state_fips'] = df['state'].apply(lambda x: af.get_state_fips(x.strip()) if pd.notnull(x) else None)
    return df


# Function to standardize values
def clean_values(value):
    if isinstance(value, str):  # Ensure the value is a string
        value = value.strip().capitalize()  # Capitalize first letter and remove extra spaces
        if value.endswith('.'):  # Remove trailing period if it exists
            value = value[:-1]
    return value


# Genertae variables from prompt rsponses
def gen_any_cols(classified_df):
    """
    This function checks whether ChatGPT responds to the prompts and creates new columns:
        `info_any_ans`: Gets 'Yes' if the responses to any of the 3 `info_` prompts (1, 2, and 3) are "Yes."
        `inst3_any_ans`: Gets 'Yes' if the responses to any of the 3 `inst_` prompts (4, 5, and 7) are "Yes."
        `inst4_any_ans`: Gets 'Yes' if the responses to any of the 4 `inst_` prompts (4, 5, 6, and 7) are "Yes."
        `negt_any_ans`: Gets 'Yes' if the responses to any of the 2 `negt_` prompts (8 and 9) are "Yes."
        `random_hiv_ans`: Checks if the tweet contains HIV-related content (`if_sti_ans` == 'Yes') but lacks 
          any information or instructions related to HIV testing, prevention, or treatment.
    """

    df = classified_df.copy()
    # Create new columns using numpy

    df['info_any'] = 'No'
    df.loc[((df['q_info_sti_tst'] == 'Yes') | 
        (df['q_info_sti_prev'] == 'Yes') | 
        (df['q_info_sti_care'] == 'Yes')), 'info_any'] = 'Yes'
    
    df['inst3_any'] = 'No'
    df.loc[((df['q_inst_sti_tst'] == 'Yes') | 
        (df['q_inst_sti_prev'] == 'Yes') | 
        (df['q_inst_sti_care'] == 'Yes')), 'inst3_any'] = 'Yes'
    
    df['inst4_any'] = 'No'
    df.loc[((df['q_inst_sti_tst'] == 'Yes') | 
        (df['q_inst_sti_prev'] == 'Yes') | 
        (df['q_inst_sti_care'] == 'Yes') |
        (df['q_inst_sti_falseprev'] == 'Yes')), 'inst4_any'] = 'Yes'
   
    df['negt_any'] = 'No'
    df.loc[((df['q_negt_pub_hlt'] == 'Yes') | 
        (df['q_negt_sti_tst'] == 'Yes')), 'negt_any'] = 'Yes'

    df['random_hiv'] = 'No'
    df.loc[(df['q_if_sti'] == 'Yes') &
        (df['info_any'] == 'No') & 
        (df['inst4_any'] == 'No'), 'random_hiv'] = 'Yes'
    
    return df

    
#  *******************************
#  * Creating GPT rate variables *
#  *******************************

if __name__ == "__main__":
    
    #Read Twitter data
    df = pd.read_csv('/SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/2024/twitter2024_annotated.csv', dtype={'id_str': str})

    # Clean the df by dropping the '.' from the end of the values and ensuring they are in the format: Yes, No, and Unsure.
    # List of columns to clean
    columns_to_clean = ["q_info_sti_tst", "q_info_sti_prev", "q_info_sti_care", "q_inst_sti_tst", "q_inst_sti_prev", 
                        "q_inst_sti_falseprev", "q_inst_sti_care", "q_negt_sti_tst", "q_negt_pub_hlt", "q_if_sti"]
     
    df[columns_to_clean] = df[columns_to_clean].applymap(clean_values)
    df = gen_any_cols(df)
    
    df = df [['id_str', 'text', 'location_raw', 'state', 'county_fips', 'created_at',
           'quote_count', 'reply_count', 'retweet_count', 'favorite_count',
           'screen_name', 'description', 'professions', 'followers_count',
           'friends_count',  'info_any', 'inst3_any', 'inst4_any', 'negt_any',
           'random_hiv']]
    
    # add state/county fips code
    df = add_fips_codes(df)
        
    
    df['state_fips'] = (
        pd.to_numeric(df['state_fips'], errors='coerce')
        .apply(lambda x: str(int(x)).zfill(2) if pd.notnull(x) else np.nan)
    )
    
    # Convert FIPS codes to 5-digit strings by padding 4-digit codes with a leading zero
    df['county_fips'] = (pd.to_numeric(df['county_fips'], errors='coerce')  
                      .apply(lambda x: str(int(x)).zfill(5) if pd.notnull(x) else np.nan))
    
    # Make sure the sate names are in agood format and the same format as Policy data
    df['state'] = df['state'].str.title()
    df.loc[df['state']=='District Of Columbia', 'state'] = 'District of Columbia'
    df = df.drop(columns=['code'], errors='ignore')
    
    #  create 'county_denominator and 'state_denominator' which is the total number of tweets in each county and each state
    df['county_denominator'] = df['county_fips'].map(df['county_fips'].value_counts())
    df['state_denominator'] = df['state'].map(df['state'].value_counts())
    
    # Define columns of interest
    cols = ['info_any', 'inst3_any', 'inst4_any', 'negt_any', 'random_hiv']
    
    # Step 1: Convert 'Yes'/'No' to 1/0
    df_binary = df.copy()
    df_binary[cols] = df_binary[cols].applymap(lambda x: 1 if x == 'Yes' else 0)
    
    ### -------- County-Level Calculation -------- ###
    # Group by county and calculate numerators
    grouped_county = df_binary.groupby('county_fips')[cols].sum().reset_index()
    
    # Add county-level denominator (assumes one value per county)
    grouped_county['county_denominator'] = df.groupby('county_fips')['county_denominator'].first().values
    
    # Calculate proportions
    for col in cols:
        grouped_county[f'county_{col}'] = grouped_county[col] / grouped_county['county_denominator']
    
    # Keep only final columns
    result_county = grouped_county[['county_fips'] + [f'county_{col}' for col in cols]]
    
    ### -------- State-Level Calculation -------- ###
    # Group by state and calculate numerators
    grouped_state = df_binary.groupby('state')[cols].sum().reset_index()
    
    # Add state-level denominator (assumes one value per state)
    grouped_state['state_denominator'] = df.groupby('state')['state_denominator'].first().values
    
    # Calculate rates
    for col in cols:
        grouped_state[f'state_{col}'] = grouped_state[col] / grouped_state['state_denominator']
    
    # Keep only final columns
    result_state = grouped_state[['state'] + [f'state_{col}' for col in cols]]

       
    df1 = df.merge(result_county, on='county_fips', how='left')
    df2 = df1.merge(result_state, on='state', how='left')
    
    df2.rename(columns={'created_at':'tweet_date'})

    df.to_csv('/SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/2024/GPT_twitter2024.csv', index=False)
    print('Done!')
    
# use this command to rn this file on Terminal:
# PYTHONPATH=$HOME/.local/lib/python3.10/site-packages python /SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/Create_GPT_variables.py