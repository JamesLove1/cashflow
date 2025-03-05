
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
    
def test_unlevered_net_capital_flows():
    
    cell = cf.df.at[cf.df.index[0], "unlevered_net_capital_flows"]     
    assert cell == -706000 

    cell = cf.df.at[cf.df.index[-1], "unlevered_net_capital_flows"]     
    assert cell ==  1184985  
    
def test_unlevered_net_cash_flows():
    
    cell = cf.df.at[cf.df.index[0], "unlevered_net_cash_flows"].round()    
    assert cell == -704403  

    cell = cf.df.at[cf.df.index[-1], "unlevered_net_cash_flows"].round()
    assert cell == 1186944 
    
def test_debt_drawdown():
    
    cell = cf.df.at[cf.df.index[0], "debt_drawdown"].round()
    assert cell ==  310588 

def loan_arrangement_fees():
    
    cell = cf.df.at[cf.df.index[0], "Loan Arrangement Fees"]
    
    assert cell == 1000
    
def test_loan_repayment_interest():
    
    cell = cf.df.at[cf.df.index[0], "loan_repayment_interest"].round()
    
    assert cell == -1165.0
    
    cell = cf.df.at[cf.df.index[-1], "loan_repayment_interest"].round()
    
    assert cell == -1165.0

def loan_repayment_lump_sum(self, df):
    
    cell = df.at[df.index[0], "debt_drawdown"]
    
    lumpsum = df.at[df.index[-1], "loan_repayment_lump_sum"] = cell
    
    assert cell == lumpsum 
    
def test_unlevered_net_cash_flows():
    
    cell = cf.df.at[cf.df.index[0], "levered_net_income_flows"].round()    
    assert cell == 432  

    cell = cf.df.at[cf.df.index[-1], "levered_net_income_flows"].round()
    assert cell == 794
    
def test_unlevered_net_cash_flows():
    
    cell = cf.df.at[cf.df.index[0], "levered_net_capital_flows"].round()    
    assert cell == -396412.0   

    cell = cf.df.at[cf.df.index[-1], "levered_net_capital_flows"].round()
    assert cell ==  874397.0 
    
def levered_net_cash_flows():
    cell = cf.df.at[cf.df.index[0], "levered_net_cash_flows"].round()    
    assert cell == -395979.0   

    cell = cf.df.at[cf.df.index[-1], "levered_net_cash_flows"].round()
    assert cell ==  875190.0 

def test_five_Year_Unlevered_Total_Return_Pre_Tax():
    
    res = cf.five_Year_Unlevered_Total_Return_Pre_Tax()
    
    assert res == 0.0788
     
# TODO: I need to test this func much more
def test_five_Year_Unlevered_Money_Multiple_Pre_Tax():
    
    res = cf.five_Year_Unlevered_Money_Multiple_Pre_Tax(cf.df)
    
    res = round(res, 2)
    
    assert res == 1.98
    
def test_five_Year_levered_Total_Return_Pre_Tax():
    
    res = cf.five_Year_levered_Total_Return_Pre_Tax()
    
    assert res == 0.0965
    
# TODO: I need to test this func much more
def test_five_Year_levered_Money_Multiple_Pre_Tax():
    
    res = cf.five_Year_levered_Money_Multiple_Pre_Tax(cf.df)
    
    res = round(res, 2)
    
    assert res == 2.39