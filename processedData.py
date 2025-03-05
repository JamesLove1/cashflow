processedData = {
    "Greater London": {
        "Average Annual Vacancy": 6.17,
        "Average Property Management & Letting Fees": 15.00,
        "Average Property Insurance": 0.10,
        "Average Maintenance Spend": 1.00,
        "Average Rental Growth": 4.78,
        "Capital Growth": 6.90
    },
    "North East": {
        "Average Annual Vacancy": 6.38,
        "Average Property Management & Letting Fees": 15.00,
        "Average Property Insurance": 0.10,
        "Average Maintenance Spend": 1.00,
        "Average Rental Growth": 3.08,
        "Capital Growth": 3.80
    },
    "North West": {
        "Average Annual Vacancy": 7.15,
        "Average Property Management & Letting Fees": 15.00,
        "Average Property Insurance": 0.10,
        "Average Maintenance Spend": 1.00,
        "Average Rental Growth": 5.17,
        "Capital Growth": 4.40
    },
    "South East": {
        "Average Annual Vacancy": 6.30,
        "Average Property Management & Letting Fees": 15.00,
        "Average Property Insurance": 0.10,
        "Average Maintenance Spend": 1.00,
        "Average Rental Growth": 4.13,
        "Capital Growth": 5.60
    },
    "South West": {
        "Average Annual Vacancy": 7.06,
        "Average Property Management & Letting Fees": 15.00,
        "Average Property Insurance": 0.10,
        "Average Maintenance Spend": 1.00,
        "Average Rental Growth": 4.88,
        "Capital Growth": 5.20
    },
    "East Of England": {
        "Average Annual Vacancy": 6.27,
        "Average Property Management & Letting Fees": 15.00,
        "Average Property Insurance": 0.10,
        "Average Maintenance Spend": 1.00,
        "Average Rental Growth": 4.25,
        "Capital Growth": 5.40
    },
    "East Midlands": {
        "Average Annual Vacancy": 7.31,
        "Average Property Management & Letting Fees": 15.00,
        "Average Property Insurance": 0.10,
        "Average Maintenance Spend": 1.00,
        "Average Rental Growth": 4.74,
        "Capital Growth": 4.50
    },
    "West Midlands": {
        "Average Annual Vacancy": 6.02,
        "Average Property Management & Letting Fees": 15.00,
        "Average Property Insurance": 0.10,
        "Average Maintenance Spend": 1.00,
        "Average Rental Growth": 4.61,
        "Capital Growth": 4.80
    },
    "Yorkshire and Humberside": {
        "Average Annual Vacancy": 7.44,
        "Average Property Management & Letting Fees": 15.00,
        "Average Property Insurance": 0.10,
        "Average Maintenance Spend": 1.00,
        "Average Rental Growth": 4.25,
        "Capital Growth": 4.30
    },
    "Northern Ireland": {
        "Average Annual Vacancy": 7.49,
        "Average Property Management & Letting Fees": 15.00,
        "Average Property Insurance": 0.10,
        "Average Maintenance Spend": 1.00,
        "Average Rental Growth": 4.70,
        "Capital Growth": 3.60
    }
}

def calculate_sdlt(property_value, residentType):
    
    # SDLT Brackets for Non-UK Residents
    sdlt_non_uk = [
        {"from": 0, "to": 250000, "rate": 0.07, "amount": 17500},
        {"from": 250000, "to": 925000, "rate": 0.12, "amount": 48000},
        {"from": 925000, "to": 1500000, "rate": 0.17, "amount": None},
        {"from": 1500000, "to": 1_000_000_000, "rate": 0.19, "amount": None},
    ]

    # SDLT Brackets for UK Residents
    sdlt_uk = [
        {"from": 0, "to": 250000, "rate": 0.05, "amount": 12500},
        {"from": 250000, "to": 925000, "rate": 0.10, "amount": 40000},
        {"from": 925000, "to": 1500000, "rate": 0.15, "amount": None},
        {"from": 1500000, "to": 1_000_000_000, "rate": 0.17, "amount": None},
    ]

    if residentType == "UK Resident":
        sdlt_brackets = sdlt_uk
    else:
        sdlt_brackets = sdlt_non_uk
    
    tax = 0
    remaining_value = property_value

    for bracket in sdlt_brackets:
        if remaining_value <= 0:
            break

        lower, upper, rate, fixed_amount = bracket["from"], bracket["to"], bracket["rate"], bracket["amount"]

        # If bracket has a fixed amount, use it
        if fixed_amount is not None and property_value > lower:
            tax += fixed_amount
        else:
            taxable_amount = min(remaining_value, upper - lower)
            tax += taxable_amount * rate

        remaining_value -= (upper - lower)

    return tax

purchaser_costs = {
    "Legal Fees": 2000,
    "Valuation": 500,
    "Survey": 500,
    "Other (Misc)": 500
}

buy_to_let_morgage_calculator = {
    "Stress Rate": 8.50,
    "5-Year Buy-to-Let (interest only) Mortgage rate (Non-UK)":	6.50,
    "5-Year Buy-to-Let (interest only) Mortgage rate (UK)":	4.50,
    "Loan Arrangement Fees": 1000
}