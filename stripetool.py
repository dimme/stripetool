#!/usr/bin/python3

# DO NOT RUN ANY OF THIS CODE UNLESS YOU UNDERSTAND WHAT IT DOES
# I TAKE NO RESPONSIBILITY FOR ANYTHING, USE ON YOUR OWN RISK

# Copyright Dimitrios Vlastaras 2026

import sys
import os
import csv
from collections import Counter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

def make_pdf(entries, output):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "stripe_logo.svg")

    doc = SimpleDocTemplate(output, pagesize=A4)
    elements = []

    drawing = svg2rlg(logo_path)
    scale = 80 / drawing.width
    drawing.width = 80
    drawing.height = drawing.height * scale
    drawing.scale(scale, scale)
    elements.append(drawing)
    elements.append(Spacer(1, 12))

    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    data = [['Type', 'Date', 'Paid Amount', 'Amount', 'Fees', 'Net', '25% VAT', 'Customer']]

    sum_paid_amount = 0
    sum_amount = 0
    sum_fees = 0
    sum_net = 0

    original_currency = "EUR"
    currency = "SEK"

    months = []
    years = []

    for entry in entries:

        original_currency = entry['Currency'].upper()
        currency = entry['Converted Currency'].upper()

        type = entry['Type']
        date = entry['Created']
        date_parts = date.split("-")
        months.append(date_parts[1])
        years.append(date_parts[0])

        paid_amount_value = float(entry['Amount'].replace(",","."))
        gross_value = float(entry['Converted Amount'].replace(",","."))
        fees_value = float(entry['Fees'].replace(",","."))
        net_value = float(entry['Net'].replace(",","."))
        vat_value = round(net_value - net_value / 1.25, 2)

        customer = entry.get('Customer Name') or entry.get('Details') or ''

        sum_paid_amount += paid_amount_value
        sum_amount += gross_value
        sum_fees += fees_value
        sum_net += net_value

        fmt = lambda v, c: "{:.2f}".format(v) + " " + c
        pdf_row = [type, date,
                   fmt(paid_amount_value, original_currency),
                   fmt(gross_value, currency),
                   fmt(fees_value, currency),
                   fmt(net_value, currency),
                   fmt(vat_value, currency),
                   customer]
        data.append(pdf_row)


    fmt = lambda v, c: "{:.2f}".format(v) + " " + c
    sum_row = ['Sum', '',
               fmt(sum_paid_amount, original_currency),
               fmt(sum_amount, currency),
               fmt(sum_fees, currency),
               fmt(sum_net, currency),
               fmt(round(sum_net - sum_net / 1.25, 2), currency),
               '']
    data.append(sum_row)

    most_common_month = int(Counter(months).most_common(1)[0][0])
    most_common_year = Counter(years).most_common(1)[0][0]
    month_name = month_names[most_common_month - 1]

    styles = getSampleStyleSheet()
    header = Paragraph("Stripe Payout Report for " + month_name + " " + most_common_year, styles['Title'])
    elements.append(header)
    elements.append(Spacer(1, 12))

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

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 stripetool.py <input_csv> [output_pdf]")
        exit(1)

    input_file = os.path.abspath(sys.argv[1])

    if not os.path.exists(input_file):
        print("[-] " + input_file + " doesn't exist.")
        exit(1)

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        output_file = ".".join(input_file.split(".")[0:-1])

    if output_file.split(".")[-1] != "pdf":
        output_file = output_file + ".pdf"

    output_file = os.path.abspath(output_file)

    if os.path.exists(output_file):
        print("[-] " + output_file + " already exists.")
        exit(1)

    with open(input_file, mode='r') as csv_file:
        entries = csv.DictReader(csv_file)
        make_pdf(entries, output_file)

    print("[+] PDF saved: " + output_file)
