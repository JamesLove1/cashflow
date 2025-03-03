import pandas as pd
import time
from datetime import datetime
import calendar
import math

from processedData import processedData

def rpi_multiplyer(present_year):
    return (1+RPI)**(present_year - startYear)

# ====== Input Data===========
Property_Location = "Greater London"                   # turn into an enum
Property_Type = "Apartment"                            # turn into an enum
Property_Value_GBP = 650000
Monthly_Gross_Rent_GBP = 2750
Annual_Ground_Rent_and_Service_Charge_GBP = 0
Your_Place_of_Residency = "UK Resident"                # turn into an enum
What_Entity_is_Purchasing_the_Property = "Company"     # turn into an enum
Are_you_financing_the_Property_with_a_Mortgage = "Yes" # turn into an enum

# ====== Key Financial Assumptions ============

RPI = 0.0325
# Purchasers_Costs = None
# Monthly_Gross_Rent_GBP = None
# Expected_Annual_Vacancy = None
# Management_and_Letting_Fees_pa = None
# Ground_Rent_and_Service_Charges_pa = None
# Property_Insurance_pa = None
# Maintenaince_Cost_pa = None
# Interest_Rate_on_Borrowings = None
# Expected_Rental_Growth_pa = None
# Expected_Capital_Growth_pa = None

def add_rent(df):

    df["Gross Rent (Full Occupancy)"] = (Monthly_Gross_Rent_GBP * rpi_multiplyer(df.index.year)).round(0)
    df["Gross Rent (Full Occupancy)"] = df["Gross Rent (Full Occupancy)"].astype(int)

def add_man_and_letting_fees(df):
    
    fees =  processedData[Property_Location]["Average Property Management & Letting Fees"]
    fees = fees / 100

    inflationAdjFees = fees * rpi_multiplyer(df.index.year)

    newColExFeesAdj =  df["Void (Vacancy)"] + df["Gross Rent (Full Occupancy)"]

    df["Property Management and Letting Fees"] = - newColExFeesAdj * inflationAdjFees
    df["Property Management and Letting Fees"] = df["Property Management and Letting Fees"].astype(int)

def add_vacancy(df):

    percentageVacancyRate = processedData[Property_Location]["Average Annual Vacancy"]

    df["Void (Vacancy)"] = - round(df["Gross Rent (Full Occupancy)"] * (percentageVacancyRate/100),0)
    df["Void (Vacancy)"] = df["Void (Vacancy)"].astype(int)

def add_ground_rent(df, Annual_Ground_Rent_and_Service_Charge_GBP):
    
    if Annual_Ground_Rent_and_Service_Charge_GBP is None:
        return
    
    if Annual_Ground_Rent_and_Service_Charge_GBP == 0:
        return

    amortized_yearly_ground_rent = Annual_Ground_Rent_and_Service_Charge_GBP / 12 

    res = amortized_yearly_ground_rent * rpi_multiplyer(df.index.year) 

    df["Ground Rent Charges (if any)"] = res
    
def add_Net_Rent(df):
    rentPlusVoid = df["Gross Rent (Full Occupancy)"] + df["Void (Vacancy)"] 
    df["Net Rent"] = rentPlusVoid + df["Property Management and Letting Fees"]

def add_property_insurance(df):
    property_insurance_rate = processedData[Property_Location]["Average Property Insurance"] / 100
    amortilised_property = Property_Value_GBP / 12 
    insurance =  property_insurance_rate * amortilised_property
    insurance_inflation_adj = insurance * rpi_multiplyer(df.index.year)

    df["Property Insurance"] = - insurance_inflation_adj 

    df["Property Insurance"].round(0)

    df["Property Insurance"] = df["Property Insurance"].astype(int)
    
def add_maintenaince(df, Property_Value_GBP):
    
    amotilised_property_cost = Property_Value_GBP / 12
    property_adj_inflation = amotilised_property_cost * rpi_multiplyer(df.index.year)
    maintenace_rate = processedData[Property_Location]["Average Maintenance Spend"] / 100
    
    df["Maintenaince"] = - property_adj_inflation * maintenace_rate
    df["Maintenaince"] = df["Maintenaince"].round(0)
    df["Maintenaince"] = df["Maintenaince"].astype(int)

def add_net_income(df):
    df["net_income"] = df["Net Rent"] + df["Property Insurance"] + df["Maintenaince"]

# ====== Cash flow ===========================

rent =  1000
numPeriods = 120
startYear = 2025

# date = datetime.now()
startDate = datetime(year=startYear, month=1, day=1)

data = {
    "Date":   pd.date_range(startDate, periods=numPeriods, freq="ME"), 
    # "Net Income": [None for _ in range(0, numPeriods)],
}

df = pd.DataFrame(data=data).set_index("Date")

add_rent(df)

add_vacancy(df)

add_man_and_letting_fees(df)

add_ground_rent(df, Annual_Ground_Rent_and_Service_Charge_GBP)

add_Net_Rent(df)

add_property_insurance(df)
    
add_maintenaince(df, Property_Value_GBP)

add_net_income(df)




startDate = datetime(year=startYear, month=1, day=1)
print(df.head(5))
print(df.tail(5))

