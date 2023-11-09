#!/usr/bin/python3

# DO NOT RUN ANY OF THIS CODE UNLESS YOU UNDERSTAND WHAT IT DOES
# I TAKE NO RESPONSIBILITY FOR ANYTHING, USE ON YOUR OWN RISK

# Copyright Dimitrios Vlastaras 2023

import click
import os
import csv
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

@click.group()
def stripetool():
    """Convert Stripe payout .csv files to .pdf files that can be used for accounting."""
    pass

@click.command()
@click.option('--input', prompt="Input .csv file", help='Input .csv file from Stripe payout reports.')
@click.option('--output', default="", prompt="Output .pdf file", help='Output .pdf file that can be used for accounting. Leave empty for the same name as the input file.')
def convert(input, output):
    """Takes a Stripe .csv file and creates a .pdf file."""

    input = os.path.abspath(input)
    
    if not os.path.exists(input):
        print("[-] " + input + " doesn't exist.")
        exit(1)

    if output == "":
        output = ".".join(input.split(".")[0:-1])

    if output.split(".")[-1] != "pdf":
         output = output + ".pdf"

    output = os.path.abspath(output)

    if os.path.exists(output):
        print("[-] " + output + " already exists.")
        exit(1)

    csv_file = open(input, mode ='r')
    entries = csv.DictReader(csv_file)

    make_pdf(entries, output)
    print("[+] PDF saved: " + output)

def make_pdf(entries, output):
    doc = SimpleDocTemplate(output, pagesize=A4)
    elements = []
    
    data = [['Type', 'Date', 'Paid Amount', 'Amount', 'Fees', 'Net', 'Customer Email']]

    sum_paid_amount = 0
    sum_amount = 0
    sum_fees = 0
    sum_net = 0

    original_currency = "EUR"
    currency = "SEK"

    for entry in entries:

        original_currency = entry['Currency'].upper()
        currency = entry['Converted Currency'].upper()

        type = entry['Type']
        date = entry['Created']
        original_amount = entry['Amount'].replace(",",".") + " " + original_currency
        amount = entry['Converted Amount'].replace(",",".") + " " + currency
        fees = entry['Fees'].replace(",",".") + " " + currency
        net = entry['Net'].replace(",",".") + " " + currency
        customer = entry['Customer Email']

        sum_paid_amount = sum_paid_amount + float(entry['Amount'].replace(",","."))
        sum_amount = sum_amount + float(entry['Converted Amount'].replace(",","."))
        sum_fees = sum_fees + float(entry['Fees'].replace(",","."))
        sum_net = sum_net + float(entry['Net'].replace(",","."))

        pdf_row = [type, date, original_amount, amount, fees, net, customer]
        data.append(pdf_row)


    sum_row = ['Sum', '', "{:.2f}".format(sum_paid_amount) + " " + original_currency, "{:.2f}".format(sum_amount) + " " + currency, "{:.2f}".format(sum_fees) + " " + currency, "{:.2f}".format(sum_net) + " " + currency, '']
    data.append(sum_row)

    table = Table(data)
    table.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'RIGHT'),
('TEXTCOLOR',(0,0),(-1,0),colors.black),
('TEXTCOLOR',(0,-1),(-1,-1),colors.black),
('TEXTCOLOR',(0,1),(-1,-2),colors.gray),
('ALIGN',(0,0),(-1,0),'CENTER'),
('ALIGN',(0,0),(0,-1),'CENTER'),
('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
('BOX', (0,0), (-1,-1), 1, colors.black),
]))
    elements.append(table)
    doc.build(elements)

stripetool.add_command(convert)

if __name__ == '__main__':
    stripetool()
