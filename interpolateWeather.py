import pandas as pd
from scipy.interpolate import griddata
import numpy as np
from multiprocessing import Pool

def interpolate_single_time(item):
    time, hours_ahead, data_block_id, origin_datetime, interp_points_arr, interpolationFeat, timeSlice, interp_points, points = item
    allIntFeat = {}
    allIntFeat['latitude'] = interp_points_arr[:,0]
    allIntFeat['longitude'] = interp_points_arr[:,1]
    allIntFeat['County'] = np.linspace(0,15,16).astype('int')
    allIntFeat['forecast_datetime'] = time
    allIntFeat['hours_ahead']       = hours_ahead[0]
    allIntFeat['data_block_id']     = data_block_id[0]
    allIntFeat['origin_datetime']   = origin_datetime[0]
    for feat in interpolationFeat:
      # Values at the known points
      values_feat = timeSlice[feat].values

      # Linear interpolation for temperature
      result = griddata(points, values_feat, interp_points, method='linear')

      allIntFeat[feat+'int'] = result
      df = pd.DataFrame(allIntFeat)
  
    return df

if __name__ == "__main__":
    weatherPred = pd.read_csv("../data/forecast_weather.csv")
    weatherPred = weatherPred.loc[(weatherPred.hours_ahead > 23) & (weatherPred.hours_ahead < 48)]

    # Number of processes to run in parallel
    num_processes = 2

    

    interpolatedVal = []
    interpolationFeat = [
           'temperature', 'dewpoint', 'cloudcover_high', 'cloudcover_low',
           'cloudcover_mid', 'cloudcover_total', '10_metre_u_wind_component',
           '10_metre_v_wind_component',
           'direct_solar_radiation', 'surface_solar_radiation_downwards',
           'snowfall', 'total_precipitation'
    ]

    # Coordinates of points where you want to interpolate
    interp_points = np.array([
        [59.31092599057606, 24.924347516442776],#"HARJUMAA",        # index = county id
        [58.89325336822078, 22.61868018616204], #"HIIUMAA",         # index = county id
        [59.177732657186525, 27.327483563720584], #"IDA-VIRUMAA",   # index = county id
        [58.9401960343481, 25.66666660100041],#   "JÄRVAMAA",       # index = county id
        [58.722190565952324, 26.536903689900708],#"JÕGEVAMAA",      # index = county id
        [59.265951945347595, 26.355665774943418],#"LÄÄNE-VIRUMAA",  # index = county id
        [58.90131388796995, 23.760348418177717],#"LÄÄNEMAA",         # index = county id
        [58.39642190189904, 24.550321648922793],#"PÄRNUMAA",         # index = county id
        [58.043991137798386, 27.162798202382948],#"PÕLVAMAA",        # index = county id
        [58.923144729594874, 24.70288373555266],#"RAPLAMAA",         # index = county id
        [58.39256707482195, 22.537559658585536],#"SAAREMAA",         # index = county id
        [58.392720495713554, 26.82996683757416],#"TARTUMAA",         # index = county id
        [58.5975, 24.9873], #"UNKNOWN", = center of the country      # index = county id
        [57.93303855829815, 26.14302669183717], #"VALGAMAA",         # index = county id
        [58.336987487787404, 25.558364059539933],#"VILJANDIMAA",     # index = county id
        [57.74795525256318, 26.91115291686715], #"VÕRUMAA"           # index = county id
      ])
    # Convert to a 2D array
    interp_points_arr = np.vstack(interp_points)


    print('unique days', len(weatherPred.forecast_datetime.unique())/24)
    for time_id,time in enumerate(weatherPred.forecast_datetime.unique()):
      timeSlice = weatherPred.loc[weatherPred.forecast_datetime == time]
      points = timeSlice[['latitude', 'longitude']].values
    
      if (len(points)) != 112:
        print('more datapoints than we should have', time_id, time)
        break

      hours_ahead = timeSlice['hours_ahead'].unique()
      data_block_id = timeSlice['data_block_id'].unique()
      origin_datetime = timeSlice['origin_datetime'].unique()

      if len(hours_ahead) != 1 or len(data_block_id) != 1 or len(origin_datetime) != 1:
        print('more than one unique value', hours_ahead, data_block_id, origin_datetime)
    

      item = time, hours_ahead, data_block_id, origin_datetime, interp_points_arr, interpolationFeat, timeSlice, interp_points, points

      # Create a pool of processes
        with Pool(num_processes) as pool:
            # Use the map function to apply the process_item function to each item in parallel
            result = pool.map(interpolate_single_time, data)


    
            interpolatedVal.append(result)

    intWeatherPred = pd.concat(interpolatedVal)
