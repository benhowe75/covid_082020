# -*- coding: utf-8 -*-
"""
Created on Fri Jul  31 20:43:51 2020
Updated on Thu Aug  17 16:06:00 2020

@author: benhowe
"""

#this program produces data table of seven day running average
# of new cases in U.S. states and globally
#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# I'm trying something totally new here

#%%
# create a timestamp to append to exported files and images
import time
datestr = time.strftime("%m-%d-%Y-%H-%M-%S")

#%%
# get the data from the Github repository
filepathA = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
filepathB = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"
filepathC = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
filepathD = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"

#%%
# gwt user input to determine which csv file to query
while True:
    selection = input("Choose the database. \n"
                  "A: U.S. cases \n"
                  "B: U.S. deaths \n"
                  "C: Global cases \n"
                  "D: Global deaths \n").lower()
    try:
        selection = ord(selection)
        if selection < 97 or selection > 100:
            print("You chose incorrectly. Try again.")
            continue
        break
    except ValueError:
        print("Error")
print(chr(selection))

#%%
# this section could be more error resistant ...
# i fixed this in the cell above
if selection == 97:
    filepath = filepathA
elif selection == 98:
    filepath = filepathB
elif selection == 99:
    filepath = filepathC
else:
    filepath = filepathD # by default, just get global deaths
#%%
#get name of place to study
plabel = "states" if selection == 97 or selection == 98 else "countries"
places = input("Enter names of %s, separated by commas. \n"
               "Use proper capitalization. " %plabel)
places = places.split(',')
#%%
# this gets rid of any extra spaces before or after any names
places2 = []
for item in range(len(places)):
    itemz = places[item].strip()
    places2.append(itemz)
#%%
# this function takes a string and gets those values from the csv file
def raw_data(string):
    df = pd.read_csv(filepath)
    if selection == 97 or selection == 98:
        df1 = df.loc[df['Province_State'] == string]
        df1 = df1.iloc[:,12:] # get rid of all the leading columns with metadata
    else:
        df1 = df.loc[df['Country/Region'] == string] # select the rows for each place
        df1 = df1.iloc[:,4:] #select just columns with data
    df1.loc[string,:] = df1.sum(axis=0) # sum the columns
    df1 = df1.iloc[-1,:] # drop all except sums row
    df2 = pd.DataFrame(df1) # I don't know why this is necessary, but otherwise creates a series
    return(df2)
#%%
# this cell gets the data using the function from the previous cell
multi_df = pd.DataFrame()
for item in places2:
    data = raw_data(item) # this line uses the function above to actually get the data
    multi_df = pd.concat([multi_df,data], axis=1)
#%%
# We need speciifc values for proper iteration and list lengths
N = len(multi_df)
L = len(places2)
#%%
# this function computes the difference between each day and the previous day
def daily(series):
    daily = np.zeros(N)
    for i in range(N-1):
        daily[i+1] = series.iloc[i+1] - series.iloc[i]
    return(daily)
#%%
# this function generates the three day averages
def three_day(series):
    three_day = np.zeros(N)
    for i in range(N-2):
        three_day[i+2] = (series.iloc[i] + series.iloc[i+1] + series.iloc[i+2])/3
    return(three_day)
#%%
# this function generates the five day averages
def five_day(series):
    five_day = np.zeros(N)
    for i in range(N-4):
        five_day[i+4] = (series.iloc[i] + series.iloc[i+1] + series.iloc[i+2] + series.iloc[i+3] + series.iloc[i+4])/5
    return(five_day)
#%%
# this function computes the seven day averages
def seven_day(series):
    seven_day = np.zeros(N)
    for i in range(N-6):
        seven_day[i+6] = (series.iloc[i]+series.iloc[i+1]+series.iloc[i+2]+series.iloc[i+3]+series.iloc[i+4]+series.iloc[i+5]+series.iloc[i+6])/7
    return(seven_day)
#%%
# These next four cells compute the various averages
# I have the function definitons but had a hard time 
# writing a loop that would call them one at a time 
# for each column in the df.
# The problem is that the shape of the df keeps changing
    
#%%
# this cell adds a column for the daily increase
for index in range(multi_df.shape[1]):
    thisColumn = multi_df.iloc[:,index]
    thatColumn = daily(thisColumn)
    thatColumnName = 'daily ' + multi_df.columns[index]
    multi_df.loc[:,thatColumnName] = thatColumn
#%%
# in this cell, I add the new column for 3-day averages    
for index in range(L, multi_df.shape[1]):
    thisColumn = multi_df.iloc[:,index]
    thatColumn = three_day(thisColumn)
    thatColumnName = '3-day ' + multi_df.columns[index-L]
    multi_df.loc[:,thatColumnName] = thatColumn
#%%
# in this cell, I add the new column for 5-day averages
for index in range(L, multi_df.shape[1]-L):
    thisColumn = multi_df.iloc[:,index]
    thatColumn = five_day(thisColumn)
    thatColumnName = '5-day ' + multi_df.columns[index-L]
    multi_df.loc[:,thatColumnName] = thatColumn
    #%%
# in this cell, I add the new column for 7-day averages
for index in range(L, multi_df.shape[1]-2*L):
    thisColumn = multi_df.iloc[:,index]
    thatColumn = seven_day(thisColumn)
    thatColumnName = '7-day ' + multi_df.columns[index-L]
    multi_df.loc[:,thatColumnName] = thatColumn
#%%
days = [i for i in range(1,N+1)] # create x values for plot
#%%
# this is for the totals used in the plot legend
totals = list()
for i in range(len(places2)):
    tally = int(multi_df.iloc[-1,i])
    totals.append(tally)

#%%
abbrev_path = "https://raw.githubusercontent.com/benhowe75/covid-phys403-sp2020/benhowe75-revised-code/state_table.csv"
abbrev = pd.read_csv(abbrev_path)
abbrev_path2 = "https://raw.githubusercontent.com/umpirsky/country-list/master/data/en_US/country.csv"
abbrev2 = pd.read_csv(abbrev_path2)
#%%
places2a = []
if selection == 97 or selection == 98:
    for item in places2:
        abb = abbrev.loc[abbrev['name'] == item, 'abbreviation'].iloc[0]
        places2a.append(abb)
else:
    for item in places2:
        try:
            abb = abbrev2.loc[abbrev2['value'] == item, 'id'].iloc[0]
            places2a.append(abb)
        except:
            places2a.append(item)
#%%
# more stuff for the legend
legends = []
for g,h in zip(places2a,totals):
    h = format(h, "9,d" )
    item = g + " " + str(h).strip()
    legends.append(item)
slabel = "New Deaths" if selection == 98 or selection == 100 else "New Cases"
#%%
def interleave(*iterables):
    return [x for y in zip(*iterables) for x in y]
#spaces = ' '*L
places3 =[]
for item in places2a:
    itemz = item + " smooth"
    places3.append(itemz)
legends2 = interleave(legends,places3)

#%%
# set start date
from datetime import datetime
zero_date = datetime(2020,1,22).date()
today = datetime.today().date()
#%%
while True:
    try:
        start_date = input("Start date as mm-dd-yy: \n")
        start_date = datetime.strptime(start_date, "%m-%d-%y").date()
        #start_date = datetime(start_date).strftime('%Y-%m-%d')
        if start_date < zero_date or start_date > today:
            print("Try again.")
            continue
        break
        print("Enter a date from Jan 22, 2020 through today.")
    except ValueError:
        print("Error")
print(start_date)
#%%
ndays = (start_date - zero_date).days # return integer number of days

#%%
# set the plot range
user = input("Which average do you want to plot? Enter 1,3,5, or 7. ")
if int(user) == 1:
    pval = L
elif int(user) == 3:
    pval = 2*L
elif int(user) == 5:
    pval = 3*L
elif int(user) == 7:
    pval = 4*L
else:
    pval = 0
#%%
while True:
    fit = input("What degree polynomial for fit? ")
    try:
        nfit = int(fit)
        if nfit < 1 or nfit > 10:
            print("Try again; choose a number between 1 and 10. ")
            continue
        break
    except ValueError:
        print("I am afraid %s is not a number" % fit)
print(nfit)
#%%
plot_df = multi_df.iloc[ndays:,:]
p_days = days[:-ndays]
datelist = pd.date_range(start_date, periods=len(p_days)).tolist()
#dlist = [d.date() for d in datelist]
dlist = [d.strftime("%b %d") for d in datelist]
fig, ax = plt.subplots()
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
# I borrowed the line above from https://preinventedwheel.com/matplotlib-thousands-separator-1-step-guide/
plt.title("Coronavirus %s-day Average %s" %(user,slabel))
for index in range(pval, pval+L):   
    #plt.plot(p_days,plot_df.iloc[:,index], linestyle = (0,(5,5)), marker='.')
    #fit = int(input("What degree polynomial for fit? "))
    poly = np.polyfit(p_days,plot_df.iloc[:,index],nfit) 
    poly_y = np.poly1d(poly)(p_days) # generate a polynomial fit    
    plt.plot(dlist,plot_df.iloc[:,index])
    plt.plot(dlist,poly_y)
#plt.xlabel('days starting at %s' %start_date.strftime("%b %d, %Y"))
plt.xlabel("Date")
plt.ylabel('# of %s' %slabel.lower())
divx = len(p_days) // 7
ax.set_xticks(p_days[0::divx])
ax.set_xticklabels(dlist[0::divx])
#plt.legend(legends)
ax.legend(legends2, loc = 'upper center', bbox_to_anchor=(0.5,-0.15), ncol = len(places2))
plt.grid()
#plt.savefig("plot_%s_%s.png" %(slabel,datestr),dpi=(300), bbox_inches='tight')
plt.show
#%%
#export = multi_df.to_csv("data_%s_%s.csv" %(slabel, datestr))
    