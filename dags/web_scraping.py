import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

def extract(page):
    
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}

    url = f'https://www.malaysiastock.biz/Listed-Companies.aspx?type=A&value={page}'

    r = requests.get(url,headers)

    soup = BeautifulSoup(r.content, 'html.parser')

    return soup


def transform(soup):

    #divs = soup.find_all('div', id = 'companyInfo')
    #table = soup.find_all('table', {'id':'MainContent_tStock'})

    table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="MainContent_tStock") 
    #rows = table.findAll(lambda tag: tag.name=='tr')

    return table

def rowgetDataText(tr, coltag='td'): # td (data) or th (header) 

    return [td.get_text(strip=True) for td in tr.find_all(coltag)]

def tableDataText(table):    
    #Parses a html segment started with tag <table> followed 
    #by multiple <tr> (table rows) and inner <td> (table data) tags. 
    #It returns a list of rows with inner columns. 
    #Accepts only one <th> (table header/data) in the first row.

    rows = []

    trs = table.find_all('tr')

    headerow = rowgetDataText(trs[0], 'th')

    if headerow: # if there is a header row include first
        rows.append(headerow)
        trs = trs[1:]
        
    for tr in trs: # for every table row
        
        rows.append(rowgetDataText(tr, 'td') ) # data row

    return rows

def tableDataImg(table):

    shariah_list = []

    trs = table.find_all('tr')

    for tr in trs: # for every table row
        cols = tr.find_all('td')
        #print('this is cols', cols)
        for col in cols:
            #print('this is col', col)
            img_list = col.find_all('img')
            #print('this is a_list', img_list)
            for img in img_list:
                #print('this is a', a)
                #link = a.get("src")
                link = img['src']
                shariah_list.append(link)
                #print(shariah_list)
                #print(len(shariah_list))


    return shariah_list

def tableDataMarketName(soup):

    market_list = []

    divs = soup.find_all('div', {'id': 'companyInfo'})

    for item in divs:
        cols = item.find_all('td')
        for col in cols:
            try:
                market_name = col.find('span', class_ = 'marketBtn Orange marketType_ListedCompanies').text.strip()
                #print('this is market name', market_name)
                market_list.append(market_name)
            except:
                try:
                    market_name = col.find('span', class_ = 'marketBtn Pink marketType_ListedCompanies').text.strip()
                    #print('this is market name', market_name)
                    market_list.append(market_name)
                except:
                    try:
                        market_name = col.find('span', class_ = 'marketBtn Blue marketType_ListedCompanies').text.strip()
                        #print('this is market name', market_name)
                        market_list.append(market_name)
                    except:
                        try:
                            market_name = col.find('span', class_ = 'marketBtn Green marketType_ListedCompanies').text.strip()
                            #print('this is market name', market_name)
                            market_list.append(market_name)
                        except:
                            'Something wrong'

    return market_list

def main():

    list_of_df = []
    list_of_shariah = []
    list_of_market = []

    pages = ['0','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

    for item in pages:
        extracted_page = extract(item)
        extracted_table = transform(extracted_page)
        transformed_table = tableDataText(extracted_table)
        #testing below
        
        shariah_list = tableDataImg(extracted_table)
        market_list = tableDataMarketName(extracted_page)

        shariah_df = pd.DataFrame(shariah_list)
        dftable = pd.DataFrame(transformed_table[1:], columns = transformed_table[0])
        market_df = pd.DataFrame(market_list)

        #extract stock code
        dftable['Stock Code'] = dftable['Company'].str.extract('(\([^)]*\))')
        dftable['Stock Code'] = dftable['Stock Code'].str.strip('(')
        dftable['Stock Code'] = dftable['Stock Code'].str.strip(')')
        dftable['Stock Code'] = dftable['Stock Code'].str.strip()

        #extract company full name
        dftable['Company Full Name'] = dftable['Company'].str.split(')').str[1]

        #extract company short name
        dftable['Stock Short Name'] = dftable['Company'].str.split().str[0]
        dftable['Stock Short Name'] = dftable['Stock Short Name'].str.strip()

        list_of_df.append(dftable)
        list_of_shariah.append(shariah_df)
        list_of_market.append(market_df)

    dftable_final = pd.concat(list_of_df)
    dfshariah_final = pd.concat(list_of_shariah)
    dfmarket_final = pd.concat(list_of_market)

    print('this is df market final', dfmarket_final.head(10))

    #Adding column header
    dfshariah_final.columns = ['Shariah_links']
    dfmarket_final.columns = ['Market_Name']

    dfshariah_final['Shariah_final'] = np.where(dfshariah_final['Shariah_links'] == 'https://www.malaysiastock.biz/App_Themes/images/Yes.png', 'Yes', 'No')

    print('this is shariah list', dfshariah_final.shape)
    print('this is shariah head', dfshariah_final.head(10))
    print('unique value of shariah is:', dftable_final.Shariah.unique())
    print('This is market head \n', dfmarket_final.head(10))
    print(dftable_final.shape)
    print(dftable_final.head(10))
    
    df_temp = pd.concat([dftable_final, dfshariah_final], axis = 1)

    print('df temp head is: \n', df_temp.head(10))
    print('df temp shape is: \n', df_temp.shape)

    df_temp = df_temp.reset_index(drop=True)
    dfmarket_final = dfmarket_final.reset_index(drop=True)

    df_final = pd.concat([df_temp, dfmarket_final], axis = 1)

    print('df_final head is: \n', df_final.head(10))
    print('df_final shape is: \n', df_final.shape)

    df_final = df_final[['Company Full Name','Stock Short Name','Stock Code','Market_Name','Shariah_final','Sector','Market Cap', 'Last Price','PE', 'DY', 'ROE']]
    df_final = df_final.rename(columns = {'Shariah_final':'Shariah','PE':'Price–earnings ratio','DY':'Dividend yield','ROE':'Return on equity','Market_Name':'Market Name'})

    df_final['Company_Key'] = np.random.randint(1000,10000, len(df_final))
    df_final['Stock_Key'] = np.random.randint(1500,10000, len(df_final))

    print('df_final head is: \n', df_final.head(10))
    print('df_final shape is: \n', df_final.shape)

    df_fct_table = df_final[['Market Cap','Last Price','Price–earnings ratio','Dividend yield','Return on equity','Company_Key','Stock_Key']]
    df_fct_table = df_fct_table.rename(columns = {'Market Cap':'Market_Cap','Last Price':'Last_Price','Price–earnings ratio':'Price–earnings_ratio','Dividend yield':'Dividend_yield','Return on equity':'Return_on_equity'})


    df_company_dim_table = df_final[['Company Full Name','Shariah','Sector','Company_Key']]
    df_company_dim_table = df_company_dim_table.rename(columns = {'Company Full Name':'Company_Full_Name'})


    df_stock_dim_table = df_final[['Stock Short Name','Stock Code','Market Name','Stock_Key']]
    df_stock_dim_table = df_stock_dim_table.rename(columns = {'Stock Short Name': 'Stock_Short_Name', 'Stock Code':'Stock_Code','Market Name':'Market_Name'})

    print(df_fct_table.columns)
    print(df_company_dim_table.columns)
    print(df_stock_dim_table.columns)

    df_fct_table.to_csv('df_fct_table.csv', index = None)
    df_company_dim_table.to_csv('df_company_dim_table.csv', index = None)
    df_stock_dim_table.to_csv('df_stock_dim_table.csv', index = None)
    
    return