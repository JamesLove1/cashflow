import pandas as pd
import time
from datetime import datetime
import calendar
import math

from processedData import processedData, calculate_sdlt, purchaser_costs, buy_to_let_morgage_calculator

class cashflow():

    def __init__(self,
                 Monthly_Gross_Rent_GBP,
                 Property_Location,                              # turn into an enum
                 Annual_Ground_Rent_and_Service_Charge_GBP,
                 Property_Value_GBP,
                 Property_Type,                                  # turn into an enum
                 Your_Place_of_Residency,                        # turn into an enum
                 What_Entity_is_Purchasing_the_Property,         # turn into an enum
                 Are_you_financing_the_Property_with_a_Mortgage  # turn into an enum
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

        self.add_ground_rent(self.df, Annual_Ground_Rent_and_Service_Charge_GBP, startYear)

        self.add_Net_Rent(self.df)

        self.add_property_insurance(self.df,startYear, Property_Location, Property_Value_GBP)

        self.add_maintenaince(self.df, Property_Value_GBP, startYear, Property_Location)

        self.add_net_income(self.df)   

        self.add_total_target_purchase_price(self.df, Property_Value_GBP)

        self.df["Purchaser's Costs"] = 0.0

        self.add_SDLT(self.df, Your_Place_of_Residency, Property_Value_GBP)

        self.purcheser_fees(self.df)

        self.all_in_Acquistion_Cost(self.df, Property_Value_GBP, Your_Place_of_Residency)

        self.portfolio_disposal(self.df, Property_Location, startYear)

        self.add_unlevered_net_income_flows(self.df)
        
        self.unlevered_net_capital_flows(self.df)
        
        self.unlevered_net_cash_flows(self.df)
        
        self.debt_drawdown(self.df, 
                           Are_you_financing_the_Property_with_a_Mortgage,
                           What_Entity_is_Purchasing_the_Property,
                           Property_Value_GBP,
                           Monthly_Gross_Rent_GBP
                           )
        
        self.loan_arrangement_fees(self.df,
                                   Are_you_financing_the_Property_with_a_Mortgage
                                   )
        
        self.loan_repayment_interest(self.df,
                                     Your_Place_of_Residency
                                     )
        
        self.loan_repayment_lump_sum(self.df)

        self.levered_net_income_flows(self.df)

        self.levered_net_capital_flows(self.df)

        self.levered_net_cash_flows(self.df)
        
    def levered_net_cash_flows(self, df):
        
        df["levered_net_cash_flows"] = 0.0
        
        sum = df["levered_net_capital_flows"] + df["levered_net_income_flows"]
        
        df["levered_net_cash_flows"] = sum
        
    def levered_net_capital_flows(self, df):
        
        df["levered_net_capital_flows"] = 0.0
        
        a = df["unlevered_net_capital_flows"]
        b = df["debt_drawdown"]
        c = df["loan_arrangement_fees"]
        d = df["loan_repayment_lump_sum"]
        
        df["levered_net_capital_flows"] = a + b + c + d 

    def levered_net_income_flows(self, df):
        
        df["levered_net_income_flows"] = 0.0

        sum = df["unlevered_net_income_flows"] + df["loan_repayment_interest"]
        df["levered_net_income_flows"] = sum



    def printDF(self):
       print(self.df.loc[:, "unlevered_net_cash_flows":].head(12))
       print(self.df.loc[:, "unlevered_net_cash_flows":].tail(12))        

    def loan_repayment_lump_sum(self, df):
        
        df["loan_repayment_lump_sum"] = 0.0
        
        cell = df.at[df.index[0], "debt_drawdown"]
        
        df.at[df.index[-1], "loan_repayment_lump_sum"] = -cell
        
        
    def loan_repayment_interest(self, 
                                df,
                                Your_Place_of_Residency
                                ):
        
        df["loan_repayment_interest"] = 0.0
        
        intrest_rate = 0
        
        if Your_Place_of_Residency == "UK Resident":
        
            intrest_rate = buy_to_let_morgage_calculator["5-Year Buy-to-Let (interest only) Mortgage rate (UK)"] / 100
        
        else:
            
            intrest_rate = buy_to_let_morgage_calculator["5-Year Buy-to-Let (interest only) Mortgage rate (Non-UK)"] / 100
            
            
        debt_drawdown = df.at[df.index[0], "debt_drawdown"] 
        
        df["loan_repayment_interest"] = - debt_drawdown/12 * intrest_rate
        
    def loan_arrangement_fees(self, 
                              df,
                              Are_you_financing_the_Property_with_a_Mortgage
                              ):
        
        df["loan_arrangement_fees"] = 0.0
        
        if Are_you_financing_the_Property_with_a_Mortgage == "Yes":
        
            arrangment_fee = buy_to_let_morgage_calculator["Loan Arrangement Fees"]
            df.at[df.index[0], "loan_arrangement_fees"] = -arrangment_fee
            
        else:  
        
            df.at[df.index[0], "Loan Arrangement Fees"] = 0
        
    def debt_drawdown(self, 
                      df, 
                      Are_you_financing_the_Property_with_a_Mortgage,
                      What_Entity_is_Purchasing_the_Property,
                      Property_Value_GBP,
                      Monthly_Gross_Rent_GBP
                      ):
        
        df["debt_drawdown"] = 0.0
        
        debt = self.morgage(
                Are_you_financing_the_Property_with_a_Mortgage,
                What_Entity_is_Purchasing_the_Property,
                Property_Value_GBP,
                Monthly_Gross_Rent_GBP
                )
        
        df.at[df.index[0], "debt_drawdown"] = debt
        
    def morgage(self,
                Are_you_financing_the_Property_with_a_Mortgage,
                What_Entity_is_Purchasing_the_Property,
                Property_Value_GBP,
                Monthly_Gross_Rent_GBP
                ):
        
        if Are_you_financing_the_Property_with_a_Mortgage == "Yes":
            
            if What_Entity_is_Purchasing_the_Property == "Company": 
                
                stressRate = buy_to_let_morgage_calculator["Stress Rate"]/100
                
                cutomLTV = (Monthly_Gross_Rent_GBP*12)/stressRate/1.25/Property_Value_GBP          
                ltv = min(cutomLTV,0.7)
                
                property_debit_tranch_value = Property_Value_GBP*ltv
                return property_debit_tranch_value
                
            else:

                stressRate = buy_to_let_morgage_calculator["Stress Rate"]/100
                
                cutomLTV = (Monthly_Gross_Rent_GBP*12)/stressRate/1.45/Property_Value_GBP
                cutomLTV = round(cutomLTV, 3)            
                ltv = min(cutomLTV,0.7)
                
                property_debit_tranch_value = Property_Value_GBP*ltv
                return property_debit_tranch_value
        
        return 0
            
    
    def unlevered_net_cash_flows(self, df):
        
        df["unlevered_net_cash_flows"] = 0.0
        
        sum = df["unlevered_net_capital_flows"]
        sum = sum + df["unlevered_net_income_flows"]
        df["unlevered_net_cash_flows"] = sum
    
    def unlevered_net_capital_flows(self, df):
        
        df["unlevered_net_capital_flows"] = 0.0
        sum = df["portfolio_disposal"] + df["All-in_Acquistion_Cost"]
        df["unlevered_net_capital_flows"] = sum       

    def add_unlevered_net_income_flows(self, df):
        
        df["unlevered_net_income_flows"] = float 
        df["unlevered_net_income_flows"] = df["net_income"]
        
    def ammount_of_1GBP_for_x_years_at_RPI(self, present_year, startYear):
        rpi = 0.0325
        return (1+rpi)**(present_year - startYear)

    def add_rent(self, df, startyear, Monthly_Gross_Rent_GBP):

        rpi_multiplyer = self.ammount_of_1GBP_for_x_years_at_RPI(df.index.year, startyear)

        df["Gross_Rent_(Full_Occupancy)"] = (Monthly_Gross_Rent_GBP * rpi_multiplyer).round(0)
        df["Gross_Rent_(Full_Occupancy)"] = df["Gross_Rent_(Full_Occupancy)"].astype(float)

    def add_man_and_letting_fees(self, df, startYear, Property_Location):

        fees =  processedData[Property_Location]["Average Property Management & Letting Fees"]
        fees = fees / 100
        
        rpi_multiplyer = self.ammount_of_1GBP_for_x_years_at_RPI(df.index.year, startYear)
        rpi_multiplyer.round(2)

        newColExFeesAdj =  df["Void_(Vacancy)"] + df["Gross_Rent_(Full_Occupancy)"]
        newColExFeesAdj *= fees
        newColExFeesAdj  = newColExFeesAdj.round(0)
        newColExFeesAdj *= rpi_multiplyer
        df["Property_Management_and_Letting_Fees"] = -newColExFeesAdj

        df["Property_Management_and_Letting_Fees"] = df["Property_Management_and_Letting_Fees"].astype(float)

    def add_vacancy(self, df, Property_Location):

        percentageVacancyRate = processedData[Property_Location]["Average Annual Vacancy"]

        df["Void_(Vacancy)"] = - round(df["Gross_Rent_(Full_Occupancy)"] * (percentageVacancyRate/100),0)
        df["Void_(Vacancy)"] = df["Void_(Vacancy)"].astype(float)

    def add_ground_rent(self, df, Annual_Ground_Rent_and_Service_Charge_GBP, startYear):

        df["Ground_Rent_Charges_(if_any)"] = 0.0
        
        if Annual_Ground_Rent_and_Service_Charge_GBP is None:
            return

        if Annual_Ground_Rent_and_Service_Charge_GBP == 0:
            return

        amortized_yearly_ground_rent = Annual_Ground_Rent_and_Service_Charge_GBP / 12 

        rpi_multiplyer = self.ammount_of_1GBP_for_x_years_at_RPI(df.index.year, startYear)
        res = amortized_yearly_ground_rent * rpi_multiplyer 

        df["Ground_Rent_Charges_(if_any)"] = res

    def add_Net_Rent(self, df):
        
        rentPlusVoid = df["Gross_Rent_(Full_Occupancy)"] + df["Void_(Vacancy)"] 
        
        df["Net_Rent"] = float
        df["Net_Rent"] = rentPlusVoid + df["Property_Management_and_Letting_Fees"]

    def add_property_insurance(self, df, startYear, Property_Location, Property_Value_GBP):
        property_insurance_rate = processedData[Property_Location]["Average Property Insurance"] / 100
        amortilised_property = Property_Value_GBP / 12 
        insurance =  property_insurance_rate * amortilised_property
        rpi_multiplyer = self.ammount_of_1GBP_for_x_years_at_RPI(df.index.year, startYear)
        insurance_inflation_adj = insurance * rpi_multiplyer

        df["Property_Insurance"] = - insurance_inflation_adj 

        df["Property_Insurance"].round(0)

        df["Property_Insurance"] = df["Property_Insurance"].astype(float)

    def add_maintenaince(self, df, Property_Value_GBP, startYear, Property_Location):

        amotilised_property_cost = Property_Value_GBP / 12
        rpi_multiplyer = self.ammount_of_1GBP_for_x_years_at_RPI(df.index.year, startYear)
        property_adj_inflation = amotilised_property_cost * rpi_multiplyer 
        maintenace_rate = processedData[Property_Location]["Average Maintenance Spend"] / 100

        df["Maintenaince"] = - property_adj_inflation * maintenace_rate
        df["Maintenaince"] = df["Maintenaince"].round(0)
        df["Maintenaince"] = df["Maintenaince"].astype(float)

    def add_net_income(self, df):
        df["net_income"] = 0.0
        df["net_income"] = df["Net_Rent"] + df["Property_Insurance"] + df["Maintenaince"]

    def add_total_target_purchase_price(self, df, Property_Value_GBP):

        df["total_target_purchase_price"] = 0.0

        df.at[df.index[0], "total_target_purchase_price"] = -Property_Value_GBP

    def add_SDLT(self, df, Your_Place_of_Residency, Property_Value_GBP):

        df["SDLT"] = 0.0

        tax = calculate_sdlt(Property_Value_GBP, Your_Place_of_Residency)

        df.at[df.index[0],"SDLT"] = -tax

    def purcheser_fees(self, df):

            fees = ["Legal_Fees", "Valuation", "Survey", "Other_(Misc)"]

            for fee in fees:

                df[fee] = 0.0

                if fee == fees[0]:
                    df.at[df.index[0], fee] = -purchaser_costs["Legal Fees"]

                elif fee == fees[-1]:
                    df.at[df.index[0], fee] = -purchaser_costs["Other (Misc)"]
                
                else:
                    df.at[df.index[0], fee] = -purchaser_costs[fee]

    def all_in_Acquistion_Cost(self, df, Property_Value_GBP, Your_Place_of_Residency):

        df["All-in_Acquistion_Cost"] = 0.0

        fees = ["Legal_Fees", "Valuation", "Survey", "Other_(Misc)"]

        cnt = 0

        for fee in fees:

            cnt += df.at[df.index[0], fee] 

        cnt -= calculate_sdlt(Property_Value_GBP, Your_Place_of_Residency)
        cnt += df.at[df.index[0], "total_target_purchase_price"]

        df.at[df.index[0], "All-in_Acquistion_Cost"] = cnt    

    def portfolio_disposal(self, df, Property_Location, startYear):

          df["portfolio_disposal"] = 0.0

          Total_Target_Purchase_Price = df.at[df.index[0], "total_target_purchase_price"]

          caitalGrowth = processedData[Property_Location]["Capital Growth"] / 100

          growthMutiplyer = (1+caitalGrowth)**(df.index[-1].year-startYear)

          salePrice = abs(Total_Target_Purchase_Price) * growthMutiplyer 

          df.at[df.index[-1], "portfolio_disposal"] = round(salePrice,0) 
          
    def printToExcel(self, df):
        df.T.to_excel("out.xlsx", engine="openpyxl")

   
cf = cashflow(Monthly_Gross_Rent_GBP = 2750,
          Property_Location = "Greater London",                  
          Annual_Ground_Rent_and_Service_Charge_GBP = 0,
          Property_Value_GBP = 650000,
          Property_Type = "Apartment",                           
          Your_Place_of_Residency = "UK Resident",               
          What_Entity_is_Purchasing_the_Property = "Company",    
          Are_you_financing_the_Property_with_a_Mortgage = "Yes" 
          )

cf.printDF()



