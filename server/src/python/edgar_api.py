import os
import requests
import pandas as pd
from datetime import datetime, timedelta

#https://github.com/GGRusty/Edgar_Video_content

headers ={"User-Agent": "decompose@stockstrip.com"}   

def extract_number(period):
    number = ''.join(filter(str.isdigit, period))
    return int(number) if number else None

def cik_to_ticker(ticker, headers=headers):
    ticker = ticker.upper().replace(".","-")
    url = "https://www.sec.gov/files/company_tickers.json"
    ticker_json = requests.get(url, headers=headers).json()
    for company in ticker_json.values():
        if company["ticker"] == ticker:
            cik = str(company["cik_str"]).zfill(10)
            return cik

    raise ValueError(f"Ticker {ticker} not found in SEC database")

def data_parser_submission(ticker, headers=headers, only_filings_df=False):
    cik = cik_to_ticker(ticker, headers)
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    company_json = requests.get(url, headers=headers).json()
    if only_filings_df:
        return pd.DataFrame(company_json['filings']['recent'])
    return company_json


#Check for enough inofrmation to have do revenue growth or dividend or earnings growth
def get_facts(ticker, headers=headers):
    cik = cik_to_ticker(ticker, headers)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    company_facts = requests.get(url, headers=headers).json()
    print("Got Facts")
    return company_facts

def get_filtered_filings(ticker, ten_k=True, just_accession_numbers=False, headers=headers):
    company_filings_df = data_parser_submission(ticker, only_filings_df=True, headers=headers)
    print(company_filings_df[company_filings_df['form'] == '10-K'])
    if ten_k:
        df = company_filings_df[company_filings_df['form'] == '10-K']
    else :
        df = company_filings_df[company_filings_df['form'] == '10-Q']
    if len(df) <= 0:
        df = company_filings_df[company_filings_df['form'] == '20-F']

    if just_accession_numbers:
        print("Accession numbers")
        return df.set_index("reportDate")["accessionNumber"]
    else:
        return df

#on circumstances of issue use this method to fine the issue
def facts_DF(ticker, headers=headers):
    print("Facts beg")
    facts = get_facts(ticker, headers)
    us_gaap_data = facts["facts"]["us-gaap"]
    df_data = []
    for fact, details in us_gaap_data.items():
        for unit in details["units"]:
            for item in details["units"][unit]:
                row = item.copy()
                row["fact"] = fact
                df_data.append(row)

    df = pd.DataFrame(df_data)
    df["end"] = pd.to_datetime(df["end"])
    df["start"] = pd.to_datetime(df["start"])
    df = df.drop_duplicates(subset=["fact", "end", "val"])
    df.set_index("end", inplace=True)
    labels_dict = {fact: details["label"] for fact, details in us_gaap_data.items()}
    print("Facts end")
    return df, labels_dict

def annual_facts(ticker, headers=headers):
    accession_nums = get_filtered_filings(
        ticker, ten_k=True, just_accession_numbers=True
    )
    df, label_dict = facts_DF(ticker, headers)
    ten_k = df[df["accn"].isin(accession_nums)]
    ten_k = ten_k[ten_k.index.isin(accession_nums.index)]
    pivot = ten_k.pivot_table(values="val", columns="fact", index="end")
    pivot.rename(columns=label_dict, inplace=True)
    return pivot.T

def quarterly_facts(ticker, headers=headers):
    print("Beg Quarterly")
    accession_nums = get_filtered_filings(
        ticker, ten_k=False, just_accession_numbers=True, headers=headers
    )
    df, label_dict = facts_DF(ticker, headers)
    ten_q = df[df["accn"].isin(accession_nums)]
    ten_q = ten_q[ten_q.index.isin(accession_nums.index)].reset_index(drop=False)
    ten_q = ten_q.drop_duplicates(subset=["fact", "end"], keep="last")
    pivot = ten_q.pivot_table(values="val", columns="fact", index="end")
    pivot.rename(columns=label_dict, inplace=True)
    print("End Quarterly")
    return pivot.T

def save_dataframe_to_csv(dataframe, folder_name, ticker, statement_name, frequency):
    print("Saved")
    path = os.path.join("./src/python", folder_name)
    directory_path = os.path.join(path, ticker)

    os.makedirs(directory_path, exist_ok=True)
    file_path = os.path.join(directory_path, f"{statement_name}_{frequency}.csv")
    dataframe.to_csv(file_path)
    return None

def delete_csv(folder_name, ticker, statement_name, frequency):
    print("Deleted")
    path = os.path.join("./src/python", folder_name)
    directory_path = os.path.join(path, ticker)
    os.makedirs(directory_path, exist_ok=True)
    file_path = os.path.join(directory_path, f"{statement_name}_{frequency}.csv")
    if os.path.exists(file_path): 
        os.remove(file_path)
    
    while True:
        try:
            os.rmdir(directory_path)
            directory_path = os.path.dirname(directory_path)  # Move up one directory
        except OSError:
            # Stop if the directory is not empty or cannot be removed
            break

    return None

#EPS growth indicates that the company is becoming more profitable, 
# which can lead to increased shareholder value.
#  Net income growth shows that the company is not only 
# increasing its top-line revenue, but also effectively 
# managing its costs and increasing its bottom-line profit.
    # data = get_facts(stock)
    # fact =data['facts']['us-gaap'].keys() 
    # revenues = fact['Revenues']['units']['usd']


# try:
#     # Fetch and save annual facts for BABA
#     # df = annual_facts("BABA", headers=headers)
#     # save_dataframe_to_csv(df, "csv", "BABA", "10-K", "1-year")
#     # facts = get_facts("BABA")
#     # usgaapkey = facts["facts"]["us-gaap"].keys()
#     # print(facts["facts"]["us-gaap"]["MarketableSecuritiesCurrent"]['units']['USD'])
#     # facts, label_dict = facts_DF("BABA")
#     # accession_nums = get_filtered_filings(
#     #     "BABA", ten_k=True, just_accession_numbers=True
#     # )
#     # print(accession_nums)
#     # print( annual_facts("BABA", headers=headers))

# except ValueError as e:
#     print(f"Error: {e}")
# except Exception as e:
#     print(f"Unexpected error: {e}")


# df = annual_facts("AAPL", headers=headers)
# print(df[df.index == "Accounts Payable, Current"])

# print(annual_APPL[annual_APPL[1].isin('Accounts Payable, Current')])