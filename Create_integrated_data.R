# This script performs GPT-based feature engineering and merges three datasets:
# 1. GPT-Rate variables dataset
# 2. HIV Vax Survey dataset
# 3. Policy dataset
# The goal is to create an integrated dataset.
install.packages("readxl")

library(dplyr)
library(readr)
library(readxl)
library(stringr)

# -----------------------------
# Load GPT Rate Dataset
# -----------------------------
gpt_df <- read_csv("/SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/2024/Twitter_GPTrates_2024.csv",
                   col_types = cols(county_fips = col_character(), state_fips = col_character()))

gpt_df <- gpt_df %>%
  select(state, county_fips, state_fips, county_denominator, state_denominator,
         county_info_any, county_inst3_any, county_inst4_any,
         county_negt_any, county_random_hiv, state_info_any,
         state_inst3_any, state_inst4_any, state_negt_any,
         state_random_hiv) %>%
  distinct(county_fips, .keep_all = TRUE)

# -----------------------------
# Load Survey Dataset
# -----------------------------

# Read baseline and  follow-up
survey0_df <- read_excel("/SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/HIV_Vax_Datasheet.xlsx", sheet = "PreScreen_Survey0")
survey1_df <- read_excel("/SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/HIV_Vax_Datasheet.xlsx", sheet = "Survey1")

# Merge baseline and follow-up (outer join)
survey_df <- full_join(survey0_df, survey1_df, by = "Record ID")

# Rename column
survey_df <- survey_df %>%
  rename(county_fips = fips_code)

survey_df$county_fips <- str_pad(as.character(survey_df$county_fips), 5, pad = "0")

cols_to_drop <- c('First Name', 'Middle Name', 'Last Name', 'Email', 'Address', 'email', 'phone', 
                  'firstname', 'midname', 'lastname', 'email2', 'zipcode', 'secondphone', 'address1', 
                  'address2', 'address3', 'firstname.1', 'midname.1', 'lastname.1', 'email.1', 'email2.1',
                  'phone.1', 'phone2', 'dob.1', 'age', 'address_street', 'address_state', 'address_zip',
                  'socialhandle', 'secondname.1', 'second_phone2', 'secondemail2.1', 'city')

survey_df <- survey_df %>% select(-any_of(cols_to_drop))
survey_df <- survey_df[, !str_detect(names(survey_df), "^Unnamed")]

# -----------------------------
# State abbreviation to full name mapping
# -----------------------------
state_abbrev_to_name <- c(
  'AL'='Alabama', 'AK'='Alaska', 'AZ'='Arizona', 'AR'='Arkansas',
  'CA'='California', 'CO'='Colorado', 'CT'='Connecticut', 'DE'='Delaware',
  'FL'='Florida', 'GA'='Georgia', 'HI'='Hawaii', 'ID'='Idaho',
  'IL'='Illinois', 'IN'='Indiana', 'IA'='Iowa', 'KS'='Kansas',
  'KY'='Kentucky', 'LA'='Louisiana', 'ME'='Maine', 'MD'='Maryland',
  'MA'='Massachusetts', 'MI'='Michigan', 'MN'='Minnesota', 'MS'='Mississippi',
  'MO'='Missouri', 'MT'='Montana', 'NE'='Nebraska', 'NV'='Nevada',
  'NH'='New Hampshire', 'NJ'='New Jersey', 'NM'='New Mexico', 'NY'='New York',
  'NC'='North Carolina', 'ND'='North Dakota', 'OH'='Ohio', 'OK'='Oklahoma',
  'OR'='Oregon', 'PA'='Pennsylvania', 'RI'='Rhode Island', 'SC'='South Carolina',
  'SD'='South Dakota', 'TN'='Tennessee', 'TX'='Texas', 'UT'='Utah',
  'VT'='Vermont', 'VA'='Virginia', 'WA'='Washington', 'WV'='West Virginia',
  'WI'='Wisconsin', 'WY'='Wyoming', 'DC'='District of Columbia')

survey_df$state <- state_abbrev_to_name[survey_df$state]

# -----------------------------
# Load Policy Dataset
# -----------------------------
policy_df <- read_excel("/SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/Policy_Coding_Master_Sheet_17Feb25.xlsx",
                        sheet = "Master") %>%
  rename(state = State)

# -----------------------------
# Merge Datasets
# -----------------------------
merged_df <- left_join(survey_df, policy_df, by = "state")
integrated_df <- left_join(merged_df, gpt_df, by = "county_fips")

# -----------------------------
# Save Final Dataset
# -----------------------------
write_csv(integrated_df, "/SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/2024/integrated_data2024.csv")

cat("Integrated dataset saved successfully.\n")
