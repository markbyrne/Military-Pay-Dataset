#!/usr/bin/env python
""":"""

__author__ = "Mark Byrne"
__version__ = "1.0"
__email__ = "MarkByrne.pro+milpayscraper@gmail.com"
__date__ = "20220918"

from bs4 import BeautifulSoup as bs
import requests
import os
import tabula as tb
import pandas as pd


url = "https://www.military.com/benefits/military-pay/charts"

ad_dir = "files/active_duty"
ad_files_list = os.listdir(ad_dir)
datasets_dir = "../datasets"


def get_AD_pay_charts():
    response = requests.get(url)
    soup = bs(response.text, 'html.parser')
    content = soup.find('div', {'class': 'page__content'})

    for link in content.find_all('a'):
        if link.string and "Active Duty Pay Charts" in link.string:
            year = link.string[0:4]
            file_url = link['href']

            if f"AD-{year}.pdf" not in ad_files_list:
                print(f"Downloading -> AD-{year}.pdf from {file_url}...")
                download_pdf(file_url, f"{ad_dir}/AD-{year}.pdf")
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
    data = tb.read_pdf(file_name, pages='1', pandas_options={'header': None})
    data_df = pd.DataFrame(data=data[0])

    print(data_df)
    if data_df.iloc[0,0] == "O-10":
        data_df.set_axis(["Rank","2 or less","Over 2","Over 3","Over 4","Over 6","Over 8","Over 10","Over 12","Over 14","Over 16","Over 18","Over 20","Over 22","Over 24","Over 26","Over 28","Over 30","Over 32","Over 34","Over 36","Over 38","Over 40"], axis=1, inplace=True)
    else:
        data_df.rename(columns=data_df.iloc[0], inplace=True)
        data_df.drop(data_df.index[0], inplace=True)
        data_df.rename(columns={data_df.columns[0]: "Rank"}, inplace=True)

    data_df = data_df[data_df['Rank'].notna()]
    data_df.set_index("Rank", inplace=True)

    print(data_df.head())
    data_df.to_csv(f'{datasets_dir}/annual_pay_scales/{os.path.basename(file_name)[:-4]}.csv', index=True)


#get_AD_pay_charts()
# for file in ad_files_list:
#     scrape_pdf(f"{ad_dir}/{file}")
scrape_pdf(f"files/active_duty/AD-2018.pdf")
