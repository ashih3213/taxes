"""
Program to calculate amount of taxes paid and take home income.
"""

import argparse
import sys

# Parse command line arguments
parser = argparse.ArgumentParser(description="Calculate taxes!")
parser.add_argument('--income', type=int, required=True, help="Total income")
parser.add_argument('--retirement', type=int, default=0, help="Amount of 401k contribution")
parser.add_argument('--mortgage', type=int, default=0, help="Mortgage interest paid each year")
parser.add_argument('--propertytax', type=int, default=0, help="Property tax paid each year")
args = parser.parse_args()

# Global constants
SOCIAL_SECURITY_TAX_RATE = 0.062
SOCIAL_SECURITY_TAX_LIMIT = 137700
MEDICARE_TAX_RATE = 0.0145
SUI_SDI_TAX_RATE = 0.01
SUI_SDI_TAX_LIMIT = 122909
CALIFORNIA_STANDARD_DEDUCTION = 4537
FEDERAL_STANDARD_DEDUCTION = 12200
LOCAL_STATE_DEDUCTION_LIMIT = 10000
DONATION_DEDUCTION = 250

# Federa/State tax brackets in format of (up to this ammount, tax rate)
FEDERAL_TAX_BRACKETS = [(9700 ,0.1), (39475, 0.12), (84200, 0.22), (160725, 0.24), (204100, 0.32), (510300, 0.35), (sys.maxsize, 0.37)]
CALIFORNIA_TAX_BRACKETS = [(8809, 0.01), (20883, 0.02), (32960, 0.04), (45753, 0.06), (57824, 0.08), (295373, 0.093), 
						   (354445, 0.103), (590742, 0.113), (1000000, 0.123), (sys.maxsize, 0.133)]

def calculate_tax(taxable_income, brackets):
	"""
	Calculate how much tax should be paid for a specific type of bracket.

	Args:
		taxable_income (int): Taxable income.
		brackets: (list): List of tuples containing tax bracket thresholds and percentages
	"""
	tax_amount = 0
	if taxable_income <= 0:
		return tax_amount
	done = False
	for index, (threshold, tax_rate) in enumerate(brackets):
		if taxable_income < threshold:
			# This is the last threshold, exit after this iteration
			threshold = taxable_income
			done = True
		if index > 0:
			tax_amount += (threshold - brackets[index - 1][0]) * tax_rate
		else:
			tax_amount += threshold * tax_rate
		if done:
			return round(tax_amount, 2)

# Calculate social security tax
social_security_taxable_income = SOCIAL_SECURITY_TAX_LIMIT if args.income > SOCIAL_SECURITY_TAX_LIMIT else args.income
social_security_tax = round(social_security_taxable_income * SOCIAL_SECURITY_TAX_RATE, 2)

# Calculate medicare tax
# Medicare tax is applied on one's entire income
medicare_tax = args.income * MEDICARE_TAX_RATE
# Additional medicare tax over 200k
if args.income > 200000:
	medicare_tax += (args.income - 200000) * 0.009
medicare_tax = round(medicare_tax, 2)

# Calculate SUI/SDI tax
sui_sdi_taxable_income = SUI_SDI_TAX_LIMIT if args.income > SUI_SDI_TAX_LIMIT else args.income
sui_sdi_tax = round(sui_sdi_taxable_income * SUI_SDI_TAX_RATE, 2)

# Calculate California state tax
california_deduction = max(CALIFORNIA_STANDARD_DEDUCTION, min(LOCAL_STATE_DEDUCTION_LIMIT, args.propertytax) + args.mortgage)
california_taxable_income = args.income - CALIFORNIA_STANDARD_DEDUCTION - args.retirement
california_state_tax = calculate_tax(california_taxable_income, CALIFORNIA_TAX_BRACKETS)

# Calculate Federal IRS tax
local_state_deduction = min(LOCAL_STATE_DEDUCTION_LIMIT, california_state_tax + args.propertytax)
itemized_deduction = local_state_deduction + args.mortgage + DONATION_DEDUCTION
# Use the higher of itemized deduction or standard deduction
federal_tax_deduction = max(itemized_deduction, FEDERAL_STANDARD_DEDUCTION)
federal_taxable_income = args.income - federal_tax_deduction - args.retirement
federal_state_tax = calculate_tax(federal_taxable_income, FEDERAL_TAX_BRACKETS)

# Print results
print("Total Income: ${}".format(args.income))
print("Social Security Tax: ${} ({}%)".format(social_security_tax, round(social_security_tax / args.income * 100, 2)))
print("Medicare Tax: ${} ({}%)".format(medicare_tax, round(medicare_tax / args.income * 100, 2)))
print("SUI/SDI Tax: ${} ({}%)".format(sui_sdi_tax, round(sui_sdi_tax / args.income * 100, 2)))
print("California State Tax: ${} ({}%)".format(california_state_tax, round(california_state_tax / args.income * 100, 2)))
print("Federal Income Tax: ${} ({}%)".format(federal_state_tax, round(federal_state_tax / args.income * 100, 2)))
total_tax = social_security_tax + medicare_tax + sui_sdi_tax + california_state_tax + federal_state_tax
print("Total Tax: ${} ({}%)".format(total_tax, round(total_tax / args.income * 100, 2)))

take_home = args.income - total_tax
print("Total Net Income is: ${}".format(take_home))