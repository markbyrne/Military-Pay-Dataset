#!/usr/bin/env python
""":"""

__author__ = "Mark Byrne"
__version__ = "1.0"
__email__ = "MarkByrne.pro+milpayscraper@gmail.com"
__date__ = "20220918"

from datetime import datetime
from bs4 import BeautifulSoup as bs
import requests
import os

url = "https://www.military.com/benefits/military-pay/charts/historical-military-pay-rates.html"

ad_dir = "files/active_duty"
ad_files_list = os.listdir(ad_dir)
datasets_dir = "../datasets"


def get_AD_pay_charts():
    print("Downloading Pay Charts")
    response = requests.get(url)
    soup = bs(response.text, 'html.parser')
    content = soup.find('div', {'id': 'bodyContent'})
    if content is None:
        raise Exception("Unable to find Body Content.")

    pdf_table = None
    for table in content.find_all('table'):
        print(table)
        print(table.th.string)
        if table.th.string == "1949-1979":
            pdf_table = table
            print("PDF Table Found")
            break

    if pdf_table is None:
        raise Exception("Unable to find PDF Table.")

    for link in pdf_table.find_all('a'):
        if link.string:
            date = None
            try:
                date = datetime.strptime(link.string.strip(), "%b. %d, %Y")
            except ValueError:
                try:
                    date = datetime.strptime(link.string.strip(), "%b %d, %Y")
                except ValueError:
                    date = datetime.strptime(link.string.strip(), "%b .%d, %Y")
            year = datetime.strftime(date, "%Y")
            month = datetime.strftime(date, "%m")
            day = datetime.strftime(date, "%d")
            file_url = link['href']

            if f"AD-{year}-{month}-{day}.pdf" not in ad_files_list:
                print(f"Downloading -> AD-{year}-{month}-{day}.pdf from {file_url}...")
                download_pdf(file_url, f"{ad_dir}/AD-{year}-{month}-{day}.pdf")
                print(f"Complete.\n")


def download_pdf(url, file_name):
    # Send GET request
    pdf_response = requests.get(url)
    # Save the PDF
    if pdf_response.status_code == 200:
        with open(file_name, "wb") as f:
            f.write(pdf_response.content)
            f.close()
    else:
        print(pdf_response.status_code)


def scrape_pdf(file_name):
    import tabula as tb
    import pandas as pd
    import numpy as np

    data = tb.read_pdf(file_name, pages='1', pandas_options={'header': None})
    data_df = pd.DataFrame(data=data[0])

    print(data_df)
    if data_df.iloc[0, 0] == "O-10":
        data_df.set_axis(["Rank","2 or less","Over 2","Over 3","Over 4","Over 6","Over 8","Over 10","Over 12","Over 14","Over 16","Over 18","Over 20","Over 22","Over 24","Over 26","Over 28","Over 30","Over 32","Over 34","Over 36","Over 38","Over 40"], axis=1, inplace=True)
    else:
        data_df.rename(columns=data_df.iloc[0], inplace=True)
        data_df.drop(data_df.index[0], inplace=True)
        data_df.rename(columns={data_df.columns[0]: "Rank"}, inplace=True)

    data_df = data_df[data_df['Rank'].notna()]
    data_df.set_index("Rank", inplace=True)

    data_df.replace(0.00, np.nan, inplace=True)
    data_df.replace('0.00', np.nan, inplace=True)
    data_df.replace("(\d+\.\d+) (\d+\.\d+)", "\\1, \\2", inplace=True, regex=True)

    data_df[:] = data_df[:].replace("[$]", "", regex=True)

    print(data_df.head())
    data_df.to_csv(f'{datasets_dir}/annual_pay_scales/{os.path.basename(file_name)[:-4]}.csv', index=True)


# get_AD_pay_charts()
# for file in ad_files_list:
#     scrape_pdf(f"{ad_dir}/{file}")

