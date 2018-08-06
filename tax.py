"""
Program to calculate amount of taxes paid and take home income.
"""

import argparse
import sys

# Parse command line arguments
parser = argparse.ArgumentParser(description="Calculate taxes!")
parser.add_argument('--income', type=int, required=True, help="Total income")
parser.add_argument('--type', type=str, required=True, choices=["W2", "1099"], help="Type of filing status")
parser.add_argument('--retirement', type=int, help="Amount of 401k contribution")
parser.add_argument('--mortgage', type=int, help="Mortgage interest paid each year")
parser.add_argument('--propertytax', type=int, help="Property tax paid each year")
args = parser.parse_args()

# Global constants
SOCIAL_SECURITY_TAX_RATE = 0.062
SOCIAL_SECURITY_TAX_LIMIT = 128400
MEDICARE_TAX_RATE = 0.0145
SUI_SDI_TAX_RATE = 0.01
SUI_SDI_TAX_LIMIT = 114967
CALIFORNIA_STANDARD_DEDUCTION = 4236
FEDERAL_STANDARD_DEDUCTION = 12000
LOCAL_STATE_DEDUCTION_LIMIT = 10000

# Federa/State tax brackets in format of (up to this ammount, tax rate)
FEDERAL_TAX_BRACKETS = [(9525 ,0.1), (38700, 0.12), (82500, 0.22), (157500, 0.24), (200000, 0.32), (500000, 0.35), (sys.maxint, 0.037)]
CALIFORNIA_TAX_BRACKETS = [(8014, 0.01), (19000, 0.02), (29988, 0.04), (41628, 0.06), (52611, 0.08), (268749, 0.093), 
						   (322498, 0.103), (537497, 0.113), (999999, 0.123), (sys.maxint, 0.0133)]

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

if args.type == "1099":
	# 1099 tax filers are independent contractors and pay double the social security and medicare tax
	SOCIAL_SECURITY_TAX_RATE *= 2
	MEDICARE_TAX_RATE *= 2

# Calculate social security tax
# Social security tax is only applied on the first $128,400 of income for 2018
social_security_taxable_income = SOCIAL_SECURITY_TAX_LIMIT if args.income > SOCIAL_SECURITY_TAX_LIMIT else args.income
social_security_tax = round(social_security_taxable_income * SOCIAL_SECURITY_TAX_RATE, 2)

# Calculate medicare tax
# Medicare tax is applied on one's entire income
medicare_tax = round(args.income * MEDICARE_TAX_RATE, 2)

# Calculate SUI/SDI tax
# SUI/SDI tax is applied on the first $114,967 of total income
sui_sdi_taxable_income = SUI_SDI_TAX_LIMIT if args.income > SUI_SDI_TAX_LIMIT else args.income
sui_sdi_tax = round(sui_sdi_taxable_income * SUI_SDI_TAX_RATE, 2)

# Calculate California state tax
# California has a 4236 standard deduction
california_taxable_income = args.income - CALIFORNIA_STANDARD_DEDUCTION
# Deduct 401k contribution if applicable
california_taxable_income -= (args.retirement or 0)
if args.type == "1099":
	# If filing 1099, one may deduct the employer portion of social security and medicare tax, which is half of each
	california_taxable_income -= (social_security_tax / 2)
	california_taxable_income -= (medicare_tax / 2)
california_state_tax = calculate_tax(california_taxable_income, CALIFORNIA_TAX_BRACKETS)

# Calculate Federal IRS tax
# There is a 10k limit on california state tax + property tax deduction
local_state_deduction = min(LOCAL_STATE_DEDUCTION_LIMIT, california_state_tax + (args.propertytax or 0))
itemized_deduction = local_state_deduction + (args.mortgage or 0)
# Use the higher of itemized deduction or standard deduction
federal_tax_deduction = max(itemized_deduction, FEDERAL_STANDARD_DEDUCTION)
federal_taxable_income = args.income - federal_tax_deduction
# Deduct 401k contribution if applicable
federal_taxable_income -= (args.retirement or 0)
if args.type == "1099":
	# If filing 1099, one may deduct the employer portion of social security and medicare tax, which is half of each
	federal_taxable_income -= (social_security_tax / 2)
federal_state_tax = calculate_tax(federal_taxable_income, FEDERAL_TAX_BRACKETS)

# Print results
print "Total Income: ${}".format(args.income)
print "Social Security Tax: ${} ({}%)".format(social_security_tax, round(social_security_tax / args.income * 100, 2))
print "Medicare Tax: ${} ({}%)".format(medicare_tax,round(medicare_tax / args.income * 100, 2))
print "SUI/SDI Tax: ${} ({}%)".format(sui_sdi_tax, round(sui_sdi_tax / args.income * 100, 2))
print "California State Tax: ${} ({}%)".format(california_state_tax, round(california_state_tax / args.income * 100, 2))
print "Federal Income Tax: ${} ({}%)".format(federal_state_tax, round(federal_state_tax / args.income * 100, 2))
total_tax = social_security_tax + medicare_tax + sui_sdi_tax + california_state_tax + federal_state_tax
print "Total Tax: ${} ({}%)".format(total_tax, round(total_tax / args.income * 100, 2))

take_home = args.income - total_tax
take_home -= (args.retirement or 0)
final_print = "Total Net Income Is: ${}".format(take_home)
if args.retirement:
	final_print += " plus 401k amount ${}".format(args.retirement)
print final_print