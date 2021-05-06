# #!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


# Start the browser and login with standard_user
def login (user, password):
    print ('Starting the browser...')
    # --uncomment when running in Azure DevOps.
    options = ChromeOptions()
    options.binary_location = "/snap/bin/chromium"
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-dev-shm-using")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    #options.add_argument("start-maximized")
    #options.add_argument("disable-infobars")
    #options.add_argument(r"user-data-dir=.\cookies\\test")
    chrome = webdriver.Chrome(options=options)
    #driver = webdriver.Chrome()
    print ('Browser started successfully. Navigating to the demo page to login.')
    chrome.get('https://www.saucedemo.com/')
    chrome.quit()

login('standard_user', 'secret_sauce')

