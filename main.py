import pandas as pd
import geopandas as gpd

## -------------------------------------------------- IMPORT DATASETS --------------------------------------------------
#region

# Import datasets
df_population = pd.read_csv('Population_Data.csv')
df_CIMD = pd.read_csv('CIMD_Variables.csv')
df_DAUID = pd.read_csv('City_DAUIDs.csv')
gdf_DA = gpd.read_file("Shapefile/Dissemination Areas.shp")

# Print datasets columns
print(df_population.columns)
print(df_CIMD.columns)
print(df_DAUID.columns)
print(gdf_DA.columns)

#endregion

## --------------------------------------------------- MERGE DATASETS --------------------------------------------------
#region

# Merge Census variables
print("Before merge:", len(df_CIMD))
df_census = df_CIMD.merge(df_population, on='DAUID', how='left')
print("After merge:", len(df_census))
print(df_census.columns)

# Limit dissemination areas to within municipal boundaries
print("Before limiting dissemination areas to within municipal boundaries:", len(df_census))
df_census = df_DAUID.merge(df_census, on='DAUID', how='left')
print("After limiting dissemination areas to within municipal boundaries:", len(df_census))

# Reduce the number of columns in the merged dataframe
df_census = df_census[['City', 'DAUID', 'Land Area in Square Kilometre', 'Population',
                       'Population Density per Square Kilometre', 'Residential instability Scores',
                       'Ethno-cultural composition Scores', 'Economic dependency Scores',
                       'Situational vulnerability Scores']]

# Remove DAs with a population density less than 400 or where population density is blank
print("Before filtering for population density less than 400:", len(df_census))
df_census = df_census[
    (df_census['Population Density per Square Kilometre'] >= 400) &
    (df_census['Population Density per Square Kilometre'].notna())
]
print("After filtering for population density less than 400:", len(df_census))

#endregion

## ------------------------------------------------ MERGE WITH SHAPEFILE -----------------------------------------------
#region

# Check data type
print(df_census['DAUID'].dtype)
print(gdf_DA['DAUID'].dtype)

# Convert DAUID column to int64
df_census['DAUID'] = df_census['DAUID'].astype('int64')
gdf_DA['DAUID'] = gdf_DA['DAUID'].astype('int64')

# Check updated data type
print(df_census['DAUID'].dtype)
print(gdf_DA['DAUID'].dtype)

# Merge with shapefile
print("Rows in dissemination area shapefile before trimming:", len(gdf_DA))

gdf_census = gpd.GeoDataFrame(
    df_census.merge(gdf_DA[['DAUID', 'geometry']], on='DAUID', how='left'),
    geometry='geometry',
    crs=gdf_DA.crs
)

print("Rows in dissemination area shapefile after trimming:", len(gdf_census))

#endregion

## ---------------------------------------- REMOVE ROWS WITH POPULATION OF ZERO ----------------------------------------
#region

