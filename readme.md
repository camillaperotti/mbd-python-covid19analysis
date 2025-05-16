# Python Group Assignment - Group 10 - S1

The goal of this project is to process data related to COVID-19 and do exploratory data analysis, ultimately to create a weekly death predictor by country in a next project. The purpose of this file is to give an overview over the [ETL Process](#0), [EDA](#1) as well the [Execution Script](#2). 

<a id='0'></a>
## **ETL Process**

In order to extract, transform and load the 6 provided CSV files, the following steps were taken:

## 1. Cleaning of each file in a separate notebook
    
* **Checking for duplicates:** none were found in any files

* **Checking for missing values:** decisions were taken to either impute missing values or drop the values where imputation was not possible or the value had no importance for the COVID analysis and predictor

**Imputation:** for the epidemeology dataset we decided to impute the new_confirmed and new_deceased columns, for the first one we decided to do the math with the cumulative_confirmed and for the values that couldn't be filled with the math to use ffill to fill this values. For new_deceased we obtain the region for each location_key, for each region and date we calculated the ratio of new_deceased/new_confirmed and then we used that ratio to multiply by the new_confirmed value of every row that had a null value of new_deceased. After imputing the value we had toround it up to an integer number, where we decided to use the ceil. function for every value above .05 so that it becomes a more realistic value of deaths.

* **Checking the correct data types:** transformation where needed to ensure correct data types.
    
* **Preparation for merging:** the final macrotable should be aggregated by week and country, which is why we ensured each table to contain week and formatted the index.

## 2. Merging of the files
* **Creating the index in the first join (merge, left)**
* **Joining further tables**: We're distinguishing here between tables containing dynamic values (e.g. new_deceased) and static values (e.g. population number) to merge tables successfully.
    
## 3. Additional cleaning step
* Reordering of columns, deletion of columns with no value add for analysis, such as cumulative values.


<a id='1'></a>
## **Conclusions of the EDA**


<a id='2'></a>
## **Execution of the Script**

### 1. Basic Execution
Open your preferred terminal (bash, powershell, etc.) and change the directory to where the etl.py document is located (i.e., change the directory to within the GroupAssignment_Group10 folder).

Run the script using the following command (i.e., type this in the terminal):
```
python etl.py <path_to_data>
```
- Replace `<path_to_data>` with the folder containing the input `.zip` files. (Within the GroupAssignment_Group10 folder, it is the 'data' folder that contains all the input files)

- **Default behavior**: 
  - The output file (`group10_macrotable.csv`) will be saved in the current working directory.
  - The date range defaults to `2020-01-02` to `2022-08-22`.
  - All available countries will be included.

---

### 2. Specify an Output Directory
To save the output file in a specific directory, use the `--output` argument:
```
python etl.py <path_to_data> --output <output_directory>
```
Example:
```
python etl.py data --output ./results
```
This saves the macrotable to the `results` folder.

---

### 3. Filter by Start and End Dates
You can filter the data by specifying a start and end date using `--start` and `--end`:
```
python etl.py <path_to_data> --start "YYYY-MM-DD" --end "YYYY-MM-DD"
```
Example:
```
python etl.py data --start "2021-01-01" --end "2021-12-31"
```
- Filters data from January 1, 2021, to December 31, 2021.

---

### 4. Filter by Countries
To include specific countries, use the `--countries` argument followed by a list of country names:
```
python etl.py <path_to_data> --countries Country1 Country2 ...
```
Example:
```
python etl.py data --countries Spain Germany
```
- Filters the macrotable to include only `Spain` and `Germany`.

---

### 5. Combine Arguments
You can combine all optional arguments:
```
python etl.py <path_to_data> --output <output_directory> --start "YYYY-MM-DD" --end "YYYY-MM-DD" --countries Country1 Country2
```

Example:
```
python etl.py data --output ./results --start "2021-01-01" --end "2021-12-31" --countries Spain Germany
```
- Reads input files from the `data` folder.
- Filters data between `2021-01-01` and `2021-12-31`.
- Includes only `Spain` and `Germany`.
- Saves the output file to the `./results` directory.

---

### Output
The script generates a CSV file named **`group10_macrotable.csv`** and saves it to the specified `--output` directory. If no `--output` is provided, the file will be saved in the **current working directory**.

## **Exploratory Data Analysis**

## Graph Analyses

1. **Weekly Trend of New Confirmed Cases by Country**:
   - A line chart depicting the weekly number of confirmed cases across different countries.
   - Highlights the fluctuation of the number of cases and the peaks (specially January 2022 in US).

2. **Total Deceased Cases per Week by Country**:
   - A line chart displaying weekly totals of deceased individuals across different countries.
   - Useful for observing mortality trends and comparing between nations, we can analyse that the peaks are all at the same time for every country.

3. **Weekly Deceased-Confirmed Ratio by Country**:
   - A line chart showing the ratio of deceased to confirmed cases weekly for each country.
   - Indicates the severity or lethality of outbreaks over time, specially the so called 'first-wave'.

4. **New People Fully Vaccinated in the United States**:
   - A line chart focusing on the weekly count of newly fully vaccinated individuals in the US.
   - Highlights vaccination rollout and its trends.

5. **Distribution of Deceased-Confirmed Ratio (Outliers Removed)**:
   - A box plot for deceased-confirmed ratios, excluding outliers, grouped by country.
   - Helps to analyze the spread and consistency of lethality metrics.

6. **Age Group Distribution by Country**:
   - A stacked bar chart showing the distribution of population across different age groups for each country.
   - Useful for understanding demographic structures.

7. **Deaths per Population vs Share of Older Population**:
   - A bar chart comparing death rates and the proportion of older individuals in each country.
   - Highlights the potential correlation between an aging population and mortality rates.

8. **Daily Vaccination Rate vs New Confirmed Cases**:
   - A scatter plot showing the relationship between vaccination rates and confirmed cases in the US.
   - Indicates the impact of vaccination on case numbers.

9. **New Confirmed vs New Deceased Cases (Percentage of Population)**:
   - A scatter plot comparing confirmed and deceased cases as a percentage of the population for different countries.
   - Highlights disparities in infection and mortality rates relative to population size.

---

## Overall Analysis

The graphs provide a comprehensive exploration of pandemic data across the countries, focusing on case trends, mortality, vaccination efforts, demographic impacts, and country-specific variations. Key insights include:
- Variability in case and death trends across countries and time.
- The share of the elderly population, vaccination rates, and trends in deceased-to-confirmed ratios are critical predictors of future death cases.
- By monitoring these variables, governments can proactively manage healthcare resources and tailor public health measures to mitigate mortality.

These conclusions align with the goal of understanding the factors influencing deaths during the pandemic.

