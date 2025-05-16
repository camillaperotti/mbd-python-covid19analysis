import argparse
import pandas as pd
import os
import math

def main(path:str, output: str, start: str, end: str, countries: list):
    #Reading all individual files:
    index = pd.read_csv(f"{path}/index.zip")
    health = pd.read_csv(f"{path}/health.zip")
    vaccinations = pd.read_csv(f"{path}/vaccinations.zip")
    demographics = pd.read_csv(f"{path}/demographics.zip")
    epidemiology = pd.read_csv(f"{path}/epidemiology.zip")

    # Individual data processing and data quality checks:
    ## For index dataset
    index = index.drop(columns = ['locality_code', 'locality_name']) 
    index = index.drop(columns = ['subregion2_code', 'subregion2_name'])
    index = index.drop(columns = ['place_id', 'wikidata_id', 'datacommons_id']) 
    index = index.drop(columns = ['iso_3166_1_alpha_2', 'iso_3166_1_alpha_3', 'aggregation_level'])

    ## For health dataset
    health = health.dropna(axis = 'columns', how = 'all')
    
    ## For vaccinations datasetS
    vaccinations = vaccinations.dropna(axis = 'columns', how = 'all') 
    vaccinations = vaccinations.fillna(0) 
    vaccinations['date'] = pd.to_datetime(vaccinations['date'], format="%Y-%m-%d")
    vaccinations['date'] =  vaccinations['date'].dt.to_period("W")
    vaccinations= vaccinations.groupby(['date','location_key'])[['new_persons_fully_vaccinated', 'cumulative_persons_fully_vaccinated']].sum()
    vaccinations = vaccinations.reset_index()
    
    ## For demographics dataset
    demographics = demographics.dropna(axis = 'columns', how = 'all')
    demographics = demographics.drop(columns = ['population_density'])
    
    ## For epidemiology dataset
    epidemiology = epidemiology.drop(columns = ['new_tested', 'cumulative_tested'])
    epidemiology = epidemiology.drop(columns = ['new_recovered', 'cumulative_recovered'])
    # Step 1: Replace nulls in 'new_confirmed' by calculating its value from consecutive 'cumulative_confirmed' values
    for i in range(len(epidemiology)):
        if pd.isna(epidemiology.at[i, "new_confirmed"]) and epidemiology.at[i, "location_key"] == epidemiology.at[i - 1, "location_key"]:
            epidemiology.at[i, "new_confirmed"] = epidemiology.at[i, "cumulative_confirmed"] - epidemiology.at[i - 1, "cumulative_confirmed"]
    # Step 2: Handle rows with minimum dates
    min_date_indices = epidemiology.groupby('location_key')['date'].idxmin()
    min_date_rows = epidemiology.loc[min_date_indices].copy()
    min_date_rows.loc[min_date_rows['new_confirmed'].isnull(), 'new_confirmed'] = min_date_rows['cumulative_confirmed']
    epidemiology.update(min_date_rows)

    # Step 3: Sort by 'location_key' and 'date'
    epidemiology = epidemiology.sort_values(by=['location_key', 'date']).reset_index(drop=True)

    # Step 4: Forward-fill 'cumulative_deceased', leaving all-null groups as NaN
    epidemiology['cumulative_deceased'] = epidemiology.groupby('location_key')['cumulative_deceased'].transform(
        lambda group: group.ffill() if group.notna().any() else group
    )

    # Step 5: Calculate 'new_deceased', leaving all-null groups as NaN
    epidemiology['new_deceased'] = epidemiology.groupby('location_key')['cumulative_deceased'].transform(
        lambda group: group.diff() if group.notna().any() else group
    )

    # Step 6: Clip negative values
    epidemiology['new_deceased'] = epidemiology['new_deceased'].clip(lower=0)
    epidemiology['new_confirmed'] = epidemiology['new_confirmed'].clip(lower=0)

    # Step 7: Extract region code
    epidemiology['region'] = epidemiology['location_key'].str[3:5]

    # Step 8: Calculate 'x' (average of new_deceased / new_confirmed) per region and date
    region_date_avg = epidemiology.groupby(['region', 'date']).apply(
        lambda group: group['new_deceased'].sum() / group['new_confirmed'].sum()
        if group['new_confirmed'].sum() > 0 else 0
    ).rename('x').reset_index()

    # Step 9: Merge 'x' into the original DataFrame
    epidemiology = epidemiology.merge(region_date_avg, on=['region', 'date'], how='left')

    # Step 10: Impute missing 'new_deceased' values using 'x * new_confirmed'
    epidemiology['new_deceased'] = epidemiology.apply(
        lambda row: (
            math.ceil(row['x'] * row['new_confirmed']) 
            if (row['x'] * row['new_confirmed']) % 1 > 0.05 
            else round(row['x'] * row['new_confirmed'])
        ) if pd.isna(row['new_deceased']) else row['new_deceased'],
        axis=1
    )

    # Step 11: Drop temporary columns
    epidemiology.drop(columns=['region', 'x'], inplace=True)

    # Step 12: Recalculate 'cumulative_deceased'
    epidemiology['cumulative_deceased'] = epidemiology.groupby('location_key')['new_deceased'].transform(lambda group: group.cumsum())

    # Final sorting
    epidemiology = epidemiology.sort_values(by=['location_key', 'date']).reset_index(drop=True)
    epidemiology['date'] = pd.to_datetime(epidemiology['date'], format="%Y-%m-%d")
    epidemiology['date'] =  epidemiology['date'].dt.to_period("W") 
    epidemiology= epidemiology.groupby(['date','location_key'])[['new_confirmed', 'new_deceased', 'cumulative_confirmed', 'cumulative_deceased']].sum()
    epidemiology = epidemiology.reset_index() 
    
    # Merging and grouping all the individual tables together --> creating the macrotable
    merged1 = pd.merge(index, demographics , on=["location_key"], how="left")
    intermediate_static = pd.merge(merged1, health, on=["location_key"], how="left")
    grouped_intermediate_static = intermediate_static.groupby('country_code').agg({             
    'population': "sum",                                 
    'population_male': "sum",                         
    'population_female': "sum",                       
    'population_age_00_09': "sum",                   
    'population_age_10_19': "sum",                    
    'population_age_20_29': "sum",                     
    'population_age_30_39': "sum",                     
    'population_age_40_49': "sum",                     
    'population_age_50_59': "sum",                     
    'population_age_60_69': "sum",                     
    'population_age_70_79': "sum",                     
    'population_age_80_and_older': "sum",           
    'life_expectancy': "mean", 
    }).reset_index()
    intermediate_dynamic =  pd.merge(epidemiology, vaccinations, on=['date', "location_key"], how="left")
    intermediate_dynamic['country_code'] = intermediate_dynamic['location_key'].str[:2]
    grouped_intermediate_dynamic = intermediate_dynamic.groupby(['country_code', 'date']).sum().reset_index()
    macrotable =  pd.merge(grouped_intermediate_dynamic, grouped_intermediate_static, on= ["country_code"], how="left")

    # Applying some transformations to fix the macrotable
    macrotable = macrotable.drop(columns = ['location_key', 'cumulative_confirmed', 'cumulative_deceased', 'cumulative_persons_fully_vaccinated'])
    macrotable['country_code'] = macrotable['country_code'].replace({
    'DE': 'Germany',
    'US': 'United States',
    'ES': 'Spain',
    'IT': 'Italy'
    })
    macrotable = macrotable.rename(columns={'country_code': 'country_name'})
    new_order = ['date',
            'country_name', 
            'population',
            'population_male',	
            'population_female',
            'population_age_00_09',	
            'population_age_10_19',	
             'population_age_20_29',	
            'population_age_30_39',	
             'population_age_40_49',	
             'population_age_50_59',	
             'population_age_60_69',	
            'population_age_70_79',	
            'population_age_80_and_older',	
            'life_expectancy',
             'new_confirmed',	
             'new_deceased',	
            'new_persons_fully_vaccinated']
    macrotable = macrotable[new_order]
    macrotable = macrotable.rename(columns={'date': 'week'})

    # Creating filter to be able to filter by country when executing the script in the terminal
    if countries:
        print(f"Filtering data for countries: {countries}")  # Debugging
        macrotable = macrotable[macrotable['country_name'].isin(countries)]

    # Creat start & date filter to be able to filter by date when executing the script in the terminal
    start = pd.Period(start, freq="W")
    end = pd.Period(end, freq="W")
    macrotable = macrotable[(macrotable['week'] >= start) & (macrotable['week'] <= end)]

    #Saving/writing the macrotable to a csv file
    group10_macrotable = macrotable.to_csv(f'{output}/group10_macrotable.csv', header=True, index = False)

# Only execute main() if it's being executed from command line
if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    # the arguments we want to catch go here
    parser.add_argument("path", type=str, help="this is the input path")
    parser.add_argument("--output", type=str, required=False, help="this is the path where the macrotable will be saved; if not specified, it will be saved in the cwd", default=os.getcwd())
    parser.add_argument("--start", type=str, required=False, default="2020-01-02", help="Start date to filter data (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, required=False, default="2022-08-22", help="End date to filter data (YYYY-MM-DD)")
    parser.add_argument("--countries", type=str, required=False, nargs="+", help="List of countries to include in the macrotable")


    args = parser.parse_args()

    main(args.path, args.output, args.start, args.end, args.countries)