''' 
This script performs GPT-based feature engineering and merges three datasets:
1. GPT-Rate variables dataset
2. HIV VAx Survey dataset
3. Policy dataset
The goal is to create an integrated dataset.
Survey payment log dataset can also be metged with the survey dataset on "record id"
'''

import os
import pandas as pd
from os import path
import numpy as np
import glob

if __name__ == "__main__":
    
    # *******************************
    # * Loading GPT rate variables *
    # *******************************
    
    gpt_df = pd.read_csv('/SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/2024/Twitter_GPTrates_2024.csv',  
                         dtype={'county_fips': str, 'state_fips': str})
    
    gpt_df = gpt_df[[ 'state', 'county_fips', 'state_fips', 'county_denominator', 'state_denominator',
           'county_info_any', 'county_inst3_any', 'county_inst4_any',
           'county_negt_any', 'county_random_hiv', 'state_info_any',
           'state_inst3_any', 'state_inst4_any', 'state_negt_any',
           'state_random_hiv']]
    
    gpt_df = gpt_df.drop_duplicates(subset='county_fips', keep='first')
    
    # ***********************
    # * Loading survey data *
    # ***********************
    
    survey0_df = pd.read_excel("/SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/HIV_Vax_Datasheet.xlsx",
                               sheet_name='PreScreen_Survey0')
    survey1_df = pd.read_excel("/SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/HIV_Vax_Datasheet.xlsx",
                               sheet_name='Survey1')
    # merge baseline and  follow-up
    survey_df = survey0_df.merge(survey1_df, on='Record ID', how='outer')

    # rename column
    survey_df.rename(columns={'fips_code':'county_fips'}, inplace=True)
    
    # Convert FIPS codes to 5-digit strings by padding 4-digit codes with a leading zero
    survey_df['county_fips'] = (pd.to_numeric(survey_df['county_fips'], errors='coerce')  
                      .apply(lambda x: str(int(x)).zfill(5) if pd.notnull(x) else np.nan))

    # drop duplicated columns
    cols_to_drop = [
        'First Name', 'Middle Name', 'Last Name', 'Email', 'Address', 'email', 'phone', 
        'firstname', 'midname', 'lastname', 'email2', 'zipcode', 'secondphone', 'address1', 
        'address2', 'address3', 'firstname.1', 'midname.1', 'lastname.1', 'email.1', 'email2.1',
        'phone.1', 'phone2', 'dob.1', 'age', 'address_street', 'address_state', 'address_zip',
        'socialhandle', 'secondname.1', 'second_phone2', 'secondemail2.1', 'city'
    ]
    
    existing_cols = [col for col in cols_to_drop if col in survey_df.columns]
    survey_df = survey_df.drop(columns=existing_cols)
    survey_df = survey_df.loc[:, ~survey_df.columns.str.startswith('Unnamed')]
    
    # Dictionary mapping state abbreviations to full names
    state_abbrev_to_name = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
    }
    
    # Assuming your DataFrame is called df and the column is named 'state'
    survey_df['state'] = survey_df['state'].map(state_abbrev_to_name)
    
    # ***********************
    # * Loading Policy data *
    # ***********************
    
    policy_df = pd.read_excel("/SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/Policy_Coding_Master_Sheet_17Feb25.xlsx",sheet_name='Master')
    policy_df.rename(columns={'State':'state'}, inplace=True)
        
    # **************************************************
    # * Merging Dataset & Creating Intergarted Dataset *
    # **************************************************
    
    merged_df = survey_df.merge(policy_df, on='state', how='left')
    integrated_df = merged_df.merge(gpt_df, on='county_fips', how='left')
    integrated_df = integrated_df.rename(columns={'state_x':'state'})
    
    # *****************************
    # * Saving Integrated Dataset *
    # *****************************
    integrated_df.to_csv('/SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/2024/Integrated_Data2024.csv', index=False)
    print('Done!')

# use this command to rn this file on Terminal:
# PYTHONPATH=$HOME/.local/lib/python3.10/site-packages python /SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/Create_Integrated_Dataset.py
