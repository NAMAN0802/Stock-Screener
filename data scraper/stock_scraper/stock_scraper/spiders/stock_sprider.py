import scrapy,re,os,time,random,ast
import pandas as pd
from scrapy_selenium import SeleniumRequest
from scrapy.selector import Selector
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class StockSpider(scrapy.Spider):
    name = 'stock_spider'
    # ticker = pd.read_csv("D:\python project\Ticker_List_NSE_India.csv")
    # tickers = ticker["SYMBOL"].to_list()  # Extend this list as needed
    # tickers = ["ANKITMETAL"]

    def __init__(self, tickers=None, base_url=None, full=True, **kwargs):
        super().__init__(**kwargs)

        self.tickers = ast.literal_eval(tickers) if isinstance(tickers, str) else tickers or []
        print(tickers)
        self.base_url = base_url or "https://www.screener.in/company/"
        self.full = full  # Boolean flag

    def start_requests(self):
        for ticker in self.tickers:
            if self.full:
                url = f"{self.base_url}{ticker}/consolidated/"
            else:
                url = f"{self.base_url}{ticker}/"

            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                meta={'ticker': ticker,
                      'dont_merge_cookies': True,
                      'handle_httpstatus_list': [200, 302]
                      },
                # wait_time=5,
                wait_time=0,  # disable static wait
                script="window.localStorage.clear(); window.sessionStorage.clear();",  # Clear storage
                dont_filter=True
            )

    def parse(self, response):
        driver = response.meta['driver']
        ticker = response.meta['ticker']
        current_url = driver.current_url.lower()
        if ticker.lower() not in current_url:
            # Force refresh if wrong page
            driver.get(response.url)
            time.sleep(5)
            current_url = driver.current_url.lower()
            if ticker.lower() not in current_url:
                self.logger.error(f"Failed to load correct page for {ticker}. Current URL: {current_url}")
                return

        try:
            # Ensure critical table has loaded (wait explicitly here)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//section[@id="shareholding"]//div[@id="quarterly-shp"]//table'))
            )

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//section[@id="profit-loss"]//table'))
            )

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//section[@id="cash-flow"]//table'))
            )

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//section[@id="balance-sheet"]//table'))
            )

        except TimeoutException:
            self.logger.warning(f"⚠️ Timed out waiting for key element on {ticker}")
            return

        # Scroll to bottom to trigger lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        html_content = driver.page_source
        
        sel = Selector(text=html_content)

        def parse_summary(xpath):
            records = []
            company_name = sel.xpath('//div[@class="card card-large"]//h1/text()').get()
            nse_link = sel.xpath('//a[contains(@href, "nseindia.com/get-quotes/equity?symbol=")]/@href').get()
            industries = sel.xpath('//p[@class="sub"]//a/text()').getall()
            industries = " > ".join(industries[:4]).strip()  # Join industries in a hierarchical format (e.g., "FMCG > Food Products > Seafood")
            records.append({'Metric': 'Company Name', 'Value': company_name})
            records.append({'Metric': 'NSE Link', 'Value': nse_link})
            records.append({'Metric': 'Industry', 'Value': industries})

            for item in sel.xpath(xpath):
                title = item.xpath(".//span[@class='name']//text()").get()
                value = re.sub(r'\s+', ' ', ''.join(item.xpath(".//span[contains(@class, 'value')]//text()").getall())).strip()
                if title and value:
                    records.append({'Metric': title.strip(), 'Value': value})
            return pd.DataFrame(records), industries

        def parse_regular_table(xpath):
            table = sel.xpath(xpath)
            headers = table.xpath(".//thead/tr/th//text()").getall()
            headers[1:] = [h.strip() for h in headers if h.strip()]
            headers[0] = 'Metric'

            rows = table.xpath(".//tbody/tr")
            records = []
            row_labels = []

            for row in rows:
                cells = row.xpath(".//td")
                row_data = []
                for cell in cells:
                    value = ''.join(cell.xpath(".//text()").getall()).strip()
                    row_data.append(value)
                if row_data:
                    row_labels.append(row_data[0])
                    records.append(row_data[1:])

            df = pd.DataFrame(records, columns=headers[1:], index=row_labels)
            return df

        def parse_peer_table(xpath):
            table = sel.xpath(xpath)
            headers = [
                re.sub(r'\s+', ' ', ' '.join(th.xpath(".//text()").getall())).strip()
                for th in table.xpath(".//tbody/tr[1]/th")
            ]
            headers = [h for h in headers if h]  # Remove empty entries
            rows = table.xpath(".//tbody/tr")[1:]
            records = []
            index_labels = []

            for row in rows:
                row_data = []
                for cell in row.xpath(".//td"):
                    value = ''.join(cell.xpath(".//text()").getall()).strip()
                    row_data.append(value)
                if row_data:
                    index_labels.append(row_data[0])      # First value = index
                    records.append(row_data[1:])

            footer=table.xpath(".//tfoot/tr")
            foot=[]
            for cell in footer.xpath(".//td"):
                value = ''.join(cell.xpath(".//text()").getall()).strip()
                foot.append(value)
            index_labels.append(foot[0])
            records.append(foot[1:])

            df = pd.DataFrame(records, columns=headers[1:], index=index_labels)
            df.index.name = headers[0] if headers else 'Company'
            return df

        sections = {
            'summary': {
                'xpath': '//div[@class="company-ratios"]//ul[@id="top-ratios"]//li',
                'parser': parse_summary
            },
            'peer_comparison': {
                'xpath': '//section[@id="peers"]//div[@id="peers-table-placeholder"]//table',
                'parser': parse_peer_table
            },
            'quarterly_results': {
                'xpath': '//section[@id="quarters"]//table',
                'parser': parse_regular_table
            },
            'profit_loss': {
                'xpath': '//section[@id="profit-loss"]//table',
                'parser': parse_regular_table
            },
            'balance_sheet': {
                'xpath': '//section[@id="balance-sheet"]//table',
                'parser': parse_regular_table
            },
            'cash_flow': {
                'xpath': '//section[@id="cash-flow"]//table',
                'parser': parse_regular_table
            },
            'ratios': {
                'xpath': '//section[@id="ratios"]//table',
                'parser': parse_regular_table
            },
            'shareholding': {
                'xpath': '//section[@id="shareholding"]//div[@id="quarterly-shp"]//table',
                'parser': parse_regular_table
            }
        }

        for section, config in sections.items():
            try:
                result = config['parser'](config['xpath'])
                if section == 'summary':
                    df, industries = result
                    folder_path = self.create_folder_structure(ticker, industries)
                else:
                    df = result
                
                if not df.empty:
                    file_path = os.path.join(folder_path, f"{section}.csv")
                    df.to_csv(file_path, encoding='utf-8')
                    self.log(f"[✓] {section} saved as {file_path}")
                else:
                    self.log(f"[✗] No data found in {section}")
            except Exception as e:
                self.log(f"[!] Error in {section}: {e}")

        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
        # Add random delay before next request
        delay = random.uniform(3, 6)
        time.sleep(delay)

    def create_folder_structure(self, ticker, industries):
        # Build folder structure dynamically using industries and ticker
        folder_path = os.path.join("fundamental_data")
        
        for industry in industries.split(" > "):  # Split industries by " > " and create subfolders
            folder_path = os.path.join(folder_path, industry.strip() if industry else "UnknownIndustry")
        
        folder_path = os.path.join(folder_path, ticker)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path
