import os
files=os.listdir()

import pandas as pd
from scipy.io import loadmat
import matplotlib.pyplot as plt

def load_data(battery):
  mat = loadmat( battery + '.mat')
  print('Total data in dataset: ', len(mat[battery][0, 0]['cycle'][0]))
  counter = 0
  dataset = []
  
  for i in range(41, len(mat[battery][0, 0]['cycle'][0])):
    row = mat[battery][0, 0]['cycle'][0, i]
    condition = row['type'][0]
    
    if condition == 'discharge' and mat[battery][0, 0]['cycle'][0, i+1]['type'][0] == 'impedance' and mat[battery][0, 0]['cycle'][0, i-2]['type'][0] == 'charge':


      data = row['data']
      voltage_measured=[]
      current_measured=[]
      capacity = data[0][0][6]
      time_discharge=[]

      for j in range(len(data[0][0][0][0])):
        voltage_measured.append(data[0][0][0][0][j])
        current_measured.append(data[0][0][1][0][j])
        time_discharge.append(data[0][0][5][0][j])

      
      temperature_discharge = (data[0][0][2][0][len(data[0][0][2][0])-1]+data[0][0][2][0][len(data[0][0][2][0])-2]+data[0][0][2][0][len(data[0][0][2][0])-3])/3


      power_out=[]
      for k in range(len(data[0][0][0][0])):
        power_out.append(abs(data[0][0][0][0][k]*data[0][0][1][0][k]))
      
      energy_out=0
      for k in range(1, len(power_out)):
        energy_out+=power_out[k]*(time_discharge[k]-time_discharge[k-1])
        

      time_end = data[0][0][5][0][len(data[0][0][5][0])-1]
        #print(time_end)

      row_new = mat[battery][0, 0]['cycle'][0, i+1]
      data_new = row_new['data']

      Re = data_new[0][0][5]
      Rct = data_new[0][0][6]
      imp = []
      for k in range(len(data_new[0][0][4])):
        #print(abs(data_new[0][0][4][k]), k)
        imp.append(abs(data_new[0][0][4][k]))
      
      imp=sum(imp)/len(imp)

      row_new=mat[battery][0, 0]['cycle'][0, i-2]
      data_new=row_new['data']
      time_charge=data_new[0][0][5][0][len(data_new[0][0][5][0])-1]
      charging_voltage=data_new[0][0][0][0]
      charging_current=data_new[0][0][1][0]
      power_in=[]
      energy_in=0

      temp_charge=(data_new[0][0][2][0][len(data_new[0][0][2][0])-1]+data_new[0][0][2][0][len(data_new[0][0][2][0])-2]+data_new[0][0][2][0][len(data_new[0][0][2][0])-3])/3

      for k in range(len(charging_voltage)):
        power_in.append(abs(charging_voltage[k]*charging_current[k]))
        try:
          energy_in+=abs(charging_voltage[k]*charging_current[k])*(data_new[0][0][5][0][k]-data_new[0][0][5][0][k-1])
        except:
          pass


        #print(time_charge)

      dataset.append([counter + 1,  time_charge, time_end, capacity, imp,
                      sum(voltage_measured)/len(voltage_measured), sum(current_measured)/len(current_measured),
                        sum(charging_voltage)/len(charging_voltage), sum(charging_current)/len(charging_current),
                          sum(power_out)/len(power_out), sum(power_in)/len(power_in), temperature_discharge, temp_charge, energy_out, energy_in])
      counter = counter + 1
   
  #print(dataset[0])
  return pd.DataFrame(data=dataset,
                    columns=['cycle', 'time_charge', 'time_discharge',
                             'capacity', 'imp', 'Discharge voltage_measured', 
                             'Discharge current_measured', 'Charging Voltage', 
                             'Charging Current', 'Power Out', 'Power In', 
                             'Temp Discharge', 'Temp Charge', 'Output Energy', 'Input Energy'])

dataframe=pd.DataFrame()


for file in files:
    try:
        dataset=load_data(file[:len(file)-4])
        dataset['capacity'] = dataset['capacity'].apply(lambda x: x[0])
        cap=list(dataframe['capacity'])

        # Create ratios
        dataset['cap_ratio'] = dataset['capacity'] / dataset['capacity'][0]
        dataset['imp_ratio'] = dataset['imp'] / dataset['imp'][0]

        # Drop original columns
        dataset.drop(columns=['capacity', 'imp'], inplace=True)

        # Initialize final_df with the first row as a list
        final_df = [list(dataset.iloc[0])]

        # Iterate through dataset and append only rows where cycle number changes
        for i in range(1, len(dataset)):
            if dataset['cycle'][i] != dataset['cycle'][i-1]:
                final_df.append(list(dataset.iloc[i]))  # Extract row as list and append

        # Convert final_df back to a DataFrame with the correct column names
        final_df = pd.DataFrame(data=final_df, columns=['cycle', 'time_charge', 'time_discharge', 
                                                        'Discharge voltage_measured', 'Discharge current_measured', 
                                                        'Charging Voltage', 'Charging Current',  # Added missing comma
                                                        'Power Out', 'Power In', 'Temp Discharge', 'Temp Charge',
                                                        'Output Energy', 'Input Energy', 'cap_ratio', 'imp_ratio'])  # Added new columns here
        plt.plot(final_df['cycle'], cap)
        plt.show()

        # If dataframe is not defined, initialize an empty one, then concatenate
        if 'dataframe' not in locals():
            dataframe = pd.DataFrame()  # Initialize empty dataframe

        # Concatenate the new final_df with the existing dataframe
        dataframe = pd.concat([dataframe, final_df], ignore_index=True)

    except:
        print(f'can not read {file}')

dataframe.to_csv('output.csv')