
import buy_to_let_cashflow
import pytest

cf = None

@pytest.fixture(autouse=True)
def setup():

    global cf 
    cf = buy_to_let_cashflow.cashflow(
        Monthly_Gross_Rent_GBP = 2750,
        Property_Location = "Greater London",                  
        Annual_Ground_Rent_and_Service_Charge_GBP = 0,
        Property_Value_GBP = 650000,
        Property_Type = "Apartment",                           
        Your_Place_of_Residency = "UK Resident",               
        What_Entity_is_Purchasing_the_Property = "Company",    
        Are_you_financing_the_Property_with_a_Mortgage = "Yes" 
        )
       
def test_unlevered_net_income_flows():
    
    net_income = cf.df["net_income"]
    unlevered_net_income_flows = cf.df["unlevered_net_income_flows"]
    
    assert net_income.equals(unlevered_net_income_flows)
    
    


