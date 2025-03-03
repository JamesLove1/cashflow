import pandas as pd
import time
from datetime import datetime
import calendar

# ====== Input Data===========
Property_Location = "Grater London"                    # turn into an enum
Property_Type = "Apartment"                            # turn into an enum
Property_Value_GBP = 650000
Monthly_Gross_Rent_GBP = 2750
Annual_Ground_Rent_and_Service_Charge_GBP = 0
Your_Place_of_Residency = "UK Resident"                # turn into an enum
What_Entity_is_Purchasing_the_Property = "Company"     # turn into an enum
Are_you_financing_the_Property_with_a_Mortgage = "Yes" # turn into an enum

# ====== Key Financial Assumptions ============

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

# ===== Processed Data =====================



# ====== Cash flow ===========================

rent =  1000
numPeriods = 120

# date = datetime.now()
startDate = datetime(year=2025, month=1, day=1)

data = {
    "Date":   pd.date_range(startDate, periods=numPeriods, freq="ME"),
    "Gross Rent (Full Occupancy)": [ Monthly_Gross_Rent_GBP for _ in range(0, numPeriods)], 
    # "Void (Vacancy)": [None for _ in range(0, numPeriods)],
    # "Property Management & Letting Fees": [None for _ in range(0, numPeriods)],
    # "Ground Rent Charges (if any)": [None for _ in range(0, numPeriods)],
    # "Net Rent": [None for _ in range(0, numPeriods)],
    # "Property Insurance": [None for _ in range(0, numPeriods)],
    # "Maintenaince": [None for _ in range(0, numPeriods)],
    # "Net Income": [None for _ in range(0, numPeriods)],
}


df = pd.DataFrame(data=data).set_index("Date")

print(df.head(12))

