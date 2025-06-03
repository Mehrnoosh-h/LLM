# Purpose: processing annotated tweets and generating county/state GPT rate variables

library(dplyr)
library(stringr)
library(readr)
library(tidyr)

# Helper function: Add state FIPS codes (replace this with your own lookup if needed)
get_state_fips <- function(state_name) {
  # Use a named vector for state names to FIPS (partial example)
  fips_lookup <- c("California" = "06", "New York" = "36", "Texas" = "48")
  return(fips_lookup[state_name])
}

# Function to clean values
clean_values <- function(value) {
  value <- str_trim(value)
  value <- str_to_title(value)
  value <- ifelse(str_ends(value, "\\."), str_sub(value, 1, -2), value)
  return(value)
}


# Function to generate "any" variables
gen_any_cols <- function(df) {
  df <- df %>%
    mutate(
      info_any = if_else(q_info_sti_tst == "Yes" | q_info_sti_prev == "Yes" | q_info_sti_care == "Yes", "Yes", "No"),
      inst3_any = if_else(q_inst_sti_tst == "Yes" | q_inst_sti_prev == "Yes" | q_inst_sti_care == "Yes", "Yes", "No"),
      inst4_any = if_else(q_inst_sti_tst == "Yes" | q_inst_sti_prev == "Yes" | q_inst_sti_care == "Yes" | q_inst_sti_falseprev == "Yes", "Yes", "No"),
      negt_any = if_else(q_negt_pub_hlt == "Yes" | q_negt_sti_tst == "Yes", "Yes", "No"),
      random_hiv = if_else(q_if_sti == "Yes" & info_any == "No" & inst4_any == "No", "Yes", "No")
    )
  return(df)
}

# Read data
df <- read_csv("/SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/2024/twitter2024_annotated.csv", 
               col_types = cols(id_str = col_character()))

# Clean relevant columns
cols_to_clean <- c("q_info_sti_tst", "q_info_sti_prev", "q_info_sti_care", "q_inst_sti_tst", 
                   "q_inst_sti_prev", "q_inst_sti_falseprev", "q_inst_sti_care", 
                   "q_negt_sti_tst", "q_negt_pub_hlt", "q_if_sti")
df[cols_to_clean] <- lapply(df[cols_to_clean], function(col) sapply(col, clean_values))

# Generate new columns
df <- gen_any_cols(df)

# Select final columns
df <- df %>% select(id_str, text, location_raw, state, county_fips, created_at,
                    quote_count, reply_count, retweet_count, favorite_count,
                    screen_name, description, professions, followers_count,
                    friends_count, info_any, inst3_any, inst4_any, negt_any, random_hiv)

# Add state FIPS
state_fips <- sapply(df$state, get_state_fips)
df$state_fips <- ifelse(!is.na(state_fips), str_pad(state_fips, 2, pad = "0"), NA)

# Format FIPS codes
df$county_fips <- ifelse(!is.na(df$county_fips), str_pad(df$county_fips, 5, pad = "0"), NA)
df$state <- str_to_title(df$state)
df$state[df$state == "District Of Columbia"] <- "District of Columbia"

# Add tweet counts by region
df <- df %>%
  group_by(county_fips) %>%
  mutate(county_denominator = n()) %>%
  ungroup() %>%
  group_by(state) %>%
  mutate(state_denominator = n()) %>%
  ungroup()

# Convert Yes/No to binary for analysis
cols <- c("info_any", "inst3_any", "inst4_any", "negt_any", "random_hiv")
df_bin <- df %>%
  mutate(across(all_of(cols), ~ if_else(. == "Yes", 1, 0)))

# County-level aggregation
county_summary <- df_bin %>%
  group_by(county_fips) %>%
  summarise(across(all_of(cols), sum), county_denominator = first(county_denominator)) %>%
  mutate(across(all_of(cols), ~ . / county_denominator, .names = "county_{.col}")) %>%
  select(county_fips, starts_with("county_"))

# State-level aggregation
state_summary <- df_bin %>%
  group_by(state) %>%
  summarise(across(all_of(cols), sum), state_denominator = first(state_denominator)) %>%
  mutate(across(all_of(cols), ~ . / state_denominator, .names = "state_{.col}")) %>%
  select(state, starts_with("state_"))

# Merge summaries
df_final <- df %>%
  left_join(county_summary, by = "county_fips") %>%
  left_join(state_summary, by = "state") %>%
  rename(tweet_date = created_at)


head(df_final, 5)

# Export
#write_csv(df_final, "/SALData/homeshare/mhasanzade@asc.upenn.edu/geo_tweets/2024/GPT_twitter2024.csv")

cat("Done!\n")