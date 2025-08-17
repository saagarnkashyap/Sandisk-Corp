"""
Data Automation Script for Semiconductor Company Financial Data
This script demonstrates various automation approaches for gathering competitor data.
"""

import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import yfinance as yf
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialDataAutomator:
    """
    A class to automate the collection of financial data from various sources
    """
    
    def __init__(self):
        self.companies = {
            'WDC': 'Western Digital Corporation',
            'MU': 'Micron Technology Inc.',
            'TSM': 'Taiwan Semiconductor Manufacturing Company Limited',
            'INTC': 'Intel Corporation'
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_yahoo_finance_data(self, symbol, period='1y'):
        """
        Fetch financial data using Yahoo Finance API
        """
        try:
            logger.info(f"Fetching Yahoo Finance data for {symbol}")
            ticker = yf.Ticker(symbol)
            
            # Get quarterly financials
            quarterly_financials = ticker.quarterly_financials
            quarterly_balance_sheet = ticker.quarterly_balance_sheet
            
            # Extract key metrics
            data = []
            if not quarterly_financials.empty and not quarterly_balance_sheet.empty:
                for date in quarterly_financials.columns:
                    try:
                        revenue = quarterly_financials.loc['Total Revenue', date] if 'Total Revenue' in quarterly_financials.index else None
                        cogs = quarterly_financials.loc['Cost Of Revenue', date] if 'Cost Of Revenue' in quarterly_financials.index else None
                        gross_profit = quarterly_financials.loc['Gross Profit', date] if 'Gross Profit' in quarterly_financials.index else None
                        inventory = quarterly_balance_sheet.loc['Inventory', date] if 'Inventory' in quarterly_balance_sheet.index else None
                        cash = quarterly_balance_sheet.loc['Cash And Cash Equivalents', date] if 'Cash And Cash Equivalents' in quarterly_balance_sheet.index else None
                        
                        # Convert to millions
                        if revenue: revenue = revenue / 1e6
                        if cogs: cogs = cogs / 1e6
                        if gross_profit: gross_profit = gross_profit / 1e6
                        if inventory: inventory = inventory / 1e6
                        if cash: cash = cash / 1e6
                        
                        data.append({
                            'Company': symbol,
                            'Date': date,
                            'Revenue': revenue,
                            'Cost Of Goods Sold': cogs,
                            'Gross Profit': gross_profit,
                            'Inventory': inventory,
                            'Cash On Hand': cash,
                            'Inventory Turnover': cogs / inventory if (cogs and inventory and inventory != 0) else None
                        })
                    except Exception as e:
                        logger.warning(f"Error processing date {date} for {symbol}: {e}")
                        continue
            
            return pd.DataFrame(data)
            
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance data for {symbol}: {e}")
            return pd.DataFrame()
    
    def scrape_macrotrends_data(self, symbol):
        """
        Scrape financial data from Macrotrends (example implementation)
        Note: This is a simplified example. Real implementation would need to handle
        dynamic content, pagination, and anti-bot measures.
        """
        try:
            logger.info(f"Scraping Macrotrends data for {symbol}")
            
            # Example URLs (these would need to be actual Macrotrends URLs)
            revenue_url = f"https://www.macrotrends.net/stocks/charts/{symbol}/revenue"
            
            response = self.session.get(revenue_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # This is a placeholder - actual implementation would parse the HTML
                # to extract financial data tables
                logger.info(f"Successfully accessed Macrotrends for {symbol}")
                return {"status": "success", "message": "Data scraped successfully"}
            else:
                logger.warning(f"Failed to access Macrotrends for {symbol}: {response.status_code}")
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error scraping Macrotrends for {symbol}: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_sec_edgar_data(self, cik):
        """
        Fetch data from SEC EDGAR API
        """
        try:
            logger.info(f"Fetching SEC EDGAR data for CIK {cik}")
            
            # SEC EDGAR API endpoint
            url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
            
            headers = {
                'User-Agent': 'YourCompany your.email@company.com',
                'Accept-Encoding': 'gzip, deflate',
                'Host': 'data.sec.gov'
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched SEC data for CIK {cik}")
                return data
            else:
                logger.warning(f"Failed to fetch SEC data for CIK {cik}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching SEC data for CIK {cik}: {e}")
            return None
    
    def automated_data_collection(self):
        """
        Main automation function that collects data from multiple sources
        """
        logger.info("Starting automated data collection")
        
        all_data = []
        
        for symbol, company_name in self.companies.items():
            logger.info(f"Processing {company_name} ({symbol})")
            
            # Method 1: Yahoo Finance API
            yahoo_data = self.get_yahoo_finance_data(symbol)
            if not yahoo_data.empty:
                all_data.append(yahoo_data)
            
            # Method 2: Web scraping (Macrotrends example)
            scrape_result = self.scrape_macrotrends_data(symbol)
            logger.info(f"Macrotrends scraping result for {symbol}: {scrape_result}")
            
            # Add delay to be respectful to servers
            time.sleep(2)
        
        # Combine all data
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            
            # Save to CSV
            output_file = '/home/ubuntu/project/automated_financial_data.csv'
            combined_data.to_csv(output_file, index=False)
            logger.info(f"Saved automated data to {output_file}")
            
            return combined_data
        else:
            logger.warning("No data collected from automation")
            return pd.DataFrame()

def main():
    """
    Main function to demonstrate the automation approach
    """
    automator = FinancialDataAutomator()
    
    print("=== Financial Data Automation Demo ===")
    print("This script demonstrates various approaches for automating competitor data collection:")
    print("1. Yahoo Finance API - Free, reliable for basic financial data")
    print("2. Web Scraping - For sites like Macrotrends, requires careful implementation")
    print("3. SEC EDGAR API - Official government data, comprehensive but complex")
    print("4. Third-party APIs - Paid services like Alpha Vantage, Quandl, etc.")
    print()
    
    # Run automation
    result_data = automator.automated_data_collection()
    
    if not result_data.empty:
        print(f"Successfully collected data for {result_data['Company'].nunique()} companies")
        print(f"Total records: {len(result_data)}")
        print("\nSample data:")
        print(result_data.head().to_string())
    else:
        print("No data was collected. This may be due to API limitations or network issues.")
    
    print("\n=== Tech Stack Summary ===")
    print("Technologies used in this automation:")
    print("- Python: Core programming language")
    print("- pandas: Data manipulation and analysis")
    print("- requests: HTTP requests for APIs and web scraping")
    print("- BeautifulSoup: HTML parsing for web scraping")
    print("- yfinance: Yahoo Finance API wrapper")
    print("- logging: Error handling and monitoring")
    print("- json: Data serialization")
    print("- time: Rate limiting and delays")

if __name__ == "__main__":
    main()

