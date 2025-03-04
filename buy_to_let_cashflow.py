import pandas as pd
import time
from datetime import datetime
import calendar
import math

from processedData import processedData, calculate_sdlt, purchaser_costs


class cashflow():

    def rpi_multiplyer(self, present_year, startYear):
        rpi = 0.0325
        return (1+rpi)**(present_year - startYear)

    def add_rent(self, df, startyear, Monthly_Gross_Rent_GBP):

        df["Gross Rent (Full Occupancy)"] = (Monthly_Gross_Rent_GBP * self.rpi_multiplyer(df.index.year,
                                             startyear)).round(0)
        df["Gross Rent (Full Occupancy)"] = df["Gross Rent (Full Occupancy)"].astype(int)

    def add_man_and_letting_fees(self, df, startYear, Property_Location):

        fees =  processedData[Property_Location]["Average Property Management & Letting Fees"]
        fees = fees / 100

        inflationAdjFees = fees * self.rpi_multiplyer(df.index.year, startYear)

        newColExFeesAdj =  df["Void (Vacancy)"] + df["Gross Rent (Full Occupancy)"]

        df["Property Management and Letting Fees"] = - newColExFeesAdj * inflationAdjFees
        df["Property Management and Letting Fees"] = df["Property Management and Letting Fees"].astype(int)

    def add_vacancy(self, df, Property_Location):

        percentageVacancyRate = processedData[Property_Location]["Average Annual Vacancy"]

        df["Void (Vacancy)"] = - round(df["Gross Rent (Full Occupancy)"] * (percentageVacancyRate/100),0)
        df["Void (Vacancy)"] = df["Void (Vacancy)"].astype(int)

    def add_ground_rent(self, df, Annual_Ground_Rent_and_Service_Charge_GBP):

        if Annual_Ground_Rent_and_Service_Charge_GBP is None:
            return

        if Annual_Ground_Rent_and_Service_Charge_GBP == 0:
            return

        amortized_yearly_ground_rent = Annual_Ground_Rent_and_Service_Charge_GBP / 12 

        res = amortized_yearly_ground_rent * self.rpi_multiplyer(df.index.year) 

        df["Ground Rent Charges (if any)"] = res

    def add_Net_Rent(self, df):
        rentPlusVoid = df["Gross Rent (Full Occupancy)"] + df["Void (Vacancy)"] 
        df["Net Rent"] = rentPlusVoid + df["Property Management and Letting Fees"]

    def add_property_insurance(self, df, startYear, Property_Location, Property_Value_GBP):
        property_insurance_rate = processedData[Property_Location]["Average Property Insurance"] / 100
        amortilised_property = Property_Value_GBP / 12 
        insurance =  property_insurance_rate * amortilised_property
        insurance_inflation_adj = insurance * self.rpi_multiplyer(df.index.year, startYear)

        df["Property Insurance"] = - insurance_inflation_adj 

        df["Property Insurance"].round(0)

        df["Property Insurance"] = df["Property Insurance"].astype(int)

    def add_maintenaince(self, df, Property_Value_GBP, startYear, Property_Location):

        amotilised_property_cost = Property_Value_GBP / 12
        property_adj_inflation = amotilised_property_cost * self.rpi_multiplyer(df.index.year, startYear)
        maintenace_rate = processedData[Property_Location]["Average Maintenance Spend"] / 100

        df["Maintenaince"] = - property_adj_inflation * maintenace_rate
        df["Maintenaince"] = df["Maintenaince"].round(0)
        df["Maintenaince"] = df["Maintenaince"].astype(int)

    def add_net_income(self, df):
        df["net_income"] = df["Net Rent"] + df["Property Insurance"] + df["Maintenaince"]

    def add_total_target_purchase_price(self, df, Property_Value_GBP):

        df["total_target_purchase_price"] = None  # Initialize column if missing

        df.at[df.index[0], "total_target_purchase_price"] = -Property_Value_GBP

    def add_SDLT(self, df, Your_Place_of_Residency, Property_Value_GBP):

        df["SDLT"] = None

        tax = calculate_sdlt(Property_Value_GBP, Your_Place_of_Residency)

        df.at[df.index[0],"SDLT"] = -tax

    def purcheser_fees(self, df):

            fees = ["Legal Fees", "Valuation", "Survey", "Other (Misc)"]

            for fee in fees:

                df[fee] = None

                df.at[df.index[0], fee] = -purchaser_costs[fee]

    def all_in_Acquistion_Cost(self, df, Property_Value_GBP, Your_Place_of_Residency):

        df["All-in Acquistion Cost"] = None

        fees = ["Legal Fees", "Valuation", "Survey", "Other (Misc)"]

        cnt = 0

        for fee in fees:

            cnt += df.at[df.index[0], fee] 

        cnt -= calculate_sdlt(Property_Value_GBP, Your_Place_of_Residency)
        cnt += df.at[df.index[0], "total_target_purchase_price"]

        df.at[df.index[0], "All-in Acquistion Cost"] = cnt    

    def portfolio_disposal(self, df, Property_Location, startYear):

          df["portfolio_disposal"] = None

          Total_Target_Purchase_Price = df.at[df.index[0], "total_target_purchase_price"]

          caitalGrowth = processedData[Property_Location]["Capital Growth"] / 100

          growthMutiplyer = (1+caitalGrowth)**(df.index[-1].year-startYear)

          salePrice = abs(Total_Target_Purchase_Price) * growthMutiplyer 

          df.at[df.index[-1], "portfolio_disposal"] = round(salePrice,0) 

    def printToExcel(self, df):
        df.T.to_excel("out.xlsx", engine="openpyxl")

    def __init__(self,
                  Monthly_Gross_Rent_GBP,
                  Property_Location = "Greater London",                   # turn into an enum
                  Annual_Ground_Rent_and_Service_Charge_GBP = 0,
                  Property_Value_GBP = 650000,
                  Property_Type = "Apartment",                            # turn into an enum
                  Your_Place_of_Residency = "UK Resident",                # turn into an enum
                  What_Entity_is_Purchasing_the_Property = "Company",     # turn into an enum
                  Are_you_financing_the_Property_with_a_Mortgage = "Yes"  # turn into an enum
                  ):

        numPeriods = 120
        startYear = 2025
        startDate = datetime(year=startYear, month=1, day=1)

        data = {
            "Date":   pd.date_range(startDate, periods=numPeriods, freq="ME"), 
        }

        self.df = pd.DataFrame(data=data).set_index("Date")

        self.add_rent(self.df, startYear, Monthly_Gross_Rent_GBP)

        self.add_vacancy(self.df, Property_Location)

        self.add_man_and_letting_fees(self.df, startYear, Property_Location)

        self.add_ground_rent(self.df, Annual_Ground_Rent_and_Service_Charge_GBP)

        self.add_Net_Rent(self.df)

        self.add_property_insurance(self.df,startYear, Property_Location, Property_Value_GBP)

        self.add_maintenaince(self.df, Property_Value_GBP, startYear, Property_Location)

        self.add_net_income(self.df)   

        self.add_total_target_purchase_price(self.df, Property_Value_GBP)

        self.df["Purchaser's Costs"] = None

        self.add_SDLT(self.df, Your_Place_of_Residency, Property_Value_GBP)

        self.purcheser_fees(self.df)

        self.all_in_Acquistion_Cost(self.df, Property_Value_GBP, Your_Place_of_Residency)

        self.portfolio_disposal(self.df, Property_Location, startYear)

    def printDF(self):
        print(self.df.loc[:, "Valuation": ].head(5))
        print(self.df.loc[:, "Valuation": ].tail(5))        


cashflow(Monthly_Gross_Rent_GBP = 2750,
          Property_Location = "Greater London",                  # turn into an enum
          Annual_Ground_Rent_and_Service_Charge_GBP = 0,
          Property_Value_GBP = 650000,
          Property_Type = "Apartment",                           # turn into an enum
          Your_Place_of_Residency = "UK Resident",               # turn into an enum
          What_Entity_is_Purchasing_the_Property = "Company",    # turn into an enum
          Are_you_financing_the_Property_with_a_Mortgage = "Yes" # turn into an enum
          ).printDF()



