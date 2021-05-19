#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
import csv
from datetime import datetime
import os.path

# Start the browser and login with standard_user
def login (username, password):
    csv_logfile = 'seleniumLogfile_{}.csv'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    # csv_rowlist is an array of arrays
    with open(csv_logfile, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['Time','Category','Message'])
        msg = 'Starting the browser...'
        print(msg)
        writer.writerow([now(), 'chrome', msg])
        options = ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-dev-shm-using")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)

        url = 'https://www.saucedemo.com/'
        msg = f'Browser started successfully. Navigating to URL: {url}'
        print(msg)
        writer.writerow([now(), 'chrome', msg])
        driver.get(url)
        msg = 'We are on the login page.'
        print(msg)
        writer.writerow([now(), 'chrome', msg])
        filename = '01_login_page.png'
        driver.save_screenshot(filename)
        check_file(filename, writer)

        msg = '=== LOGIN ==='
        print(f'\n{msg}')
        writer.writerow([now(), 'login', msg])
        msg = f'Trying to login as user {username}'
        print(msg)
        writer.writerow([now(), 'login', msg])
        driver.find_element_by_css_selector("input[id='user-name']").send_keys(username)
        driver.find_element_by_css_selector("input[id='password']").send_keys(password)
        msg = 'Clicking on the login button'
        print(f'> {msg}')
        writer.writerow([now(), 'login', msg])
        driver.find_element_by_css_selector("input[id='login-button']").click()

        msg = 'Checking that login was successful.'
        print(msg)
        writer.writerow([now(), 'login', msg])
        result = driver.find_element_by_id('logout_sidebar_link')
        msg = f'ERROR: Login to URL "{url}" failed!'
        if not result:
            writer.writerow([now(), 'login', msg])
        assert result, '> {msg}'
        msg = f'OK: Login to URL "{url}" with user name "{username}" successful!'
        print(f'> {msg}')
        writer.writerow([now(), 'login', msg])

        msg = '=== ADD ITEMS ==='
        print('\n{msg}')
        writer.writerow([now(), 'mainpage', msg])
        msg = 'We are on the main page.'
        print(msg)
        writer.writerow([now(), 'mainpage', msg])
        added_items = list()
        removed_items = list()
        msg = 'Looking for items to add to cart'
        print(msg)
        writer.writerow([now(), 'mainpage', msg])
        items = driver.find_elements_by_class_name('inventory_item')
        for count, item in enumerate(items, 1):
            item_name = item.find_element_by_class_name('inventory_item_name')
            added_items.append(item_name.text)
            msg = 'Adding to cart item {}: "{}"'.format(count, item_name.text)
            print(msg)
            writer.writerow([now(), 'mainpage', msg])
            item.find_element_by_css_selector("button[class='btn btn_primary btn_small btn_inventory']").click()
        
        filename = '02_main_page_items_added.png'
        driver.save_screenshot(filename)
        check_file(filename, writer)

        msg = '=== CHECK SHOPPING CART ==='
        print(f'\n{msg}')
        writer.writerow([now(), 'shoppingcart', msg])
        msg = 'Opening shopping cart to check listed items'
        print(msg)
        writer.writerow([now(), 'shoppingcart', msg])
        shopping_cart_link = driver.find_element_by_class_name('shopping_cart_container')
        shopping_cart_link.click()
        msg = 'We are on the shopping cart page.'
        print(msg)
        writer.writerow([now(), 'shoppingcart', msg])

        filename = '03_shopping_cart_page.png'
        driver.save_screenshot(filename)
        check_file(filename, writer)
    
        msg = 'Checking that previously added {} items are really in the shopping cart'.format(len(added_items))
        print(msg)
        writer.writerow([now(), 'shoppingcart', msg])
        msg = ', '.join(added_items)
        print(msg)
        writer.writerow([now(), 'shoppingcart', msg])
        for count, my_item in enumerate(added_items, 1):
            msg = f'Checking item {count}: "{my_item}"'
            print(msg)
            writer.writerow([now(), 'shoppingcart', msg])
            shopping_cart_items = driver.find_elements_by_class_name('inventory_item_name')
            result = my_item in [i.text for i in shopping_cart_items]
            msg = f'ERROR: item "{my_item}" is NOT in the shopping cart!'
            if not result:
                writer.writerow([now(), 'shoppingcart', msg])
            assert result, f'> {msg}'
            msg = f'OK: item "{my_item}" is in the shopping cart!'
            print(f'> {msg}')
            writer.writerow([now(), 'shoppingcart', msg])

        msg = '=== REMOVE ITEMS ==='
        print('\n{msg}')
        writer.writerow([now(), 'shoppingcart', msg])
        msg = 'Removing items from the shopping cart'
        print(msg)
        writer.writerow([now(), 'shoppingcart', msg])
        for count, my_item in enumerate(added_items, 1):
            removed_items.append(my_item)
            msg = f'Removing item {count}: "{my_item}"'
            print(msg)
            writer.writerow([now(), 'shoppingcart', msg])
            for cart_item in driver.find_elements_by_class_name('cart_item_label'):
                if cart_item.find_element_by_class_name('inventory_item_name').text == my_item:
                    msg = f'Click on remove button for item "{my_item}"'
                    print(msg)
                    writer.writerow([now(), 'shoppingcart', msg])
                    cart_item.find_element_by_css_selector("button[class='btn btn_secondary btn_small cart_button']").click()
                    
                    filename = f'04_shopping_cart_page_item_{count}_removed.png'
                    driver.save_screenshot(filename)
                    check_file(filename, writer)
        
            msg = f'Checking that item "{my_item}" has really been removed from shopping cart'
            print(msg)
            writer.writerow([now(), 'shoppingcart', msg])
            result = my_item not in [i.text for i in driver.find_elements_by_class_name('inventory_item_name')]
            msg = f'ERROR: item "{my_item}" has NOT been removed from shopping cart!'
            if not result:
                writer.writerow([now(), 'shoppingcart', msg])
            assert result, f'> {msg}'
            msg = f'OK: item "{my_item}" has been removed from shopping cart!'
            print(f'> {msg}')
            writer.writerow([now(), 'shoppingcart', msg])

        msg = 'All UI tests with Selenium finshed successfully!'
        print(msg)
        writer.writerow([now(), 'chrome', msg])
        driver.stop_client()
        driver.close()
        driver.quit()

# Return current timestamp in format YYYY-MM-DD HH:MM:SS
def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Check file exists and write status to logfile
def check_file(filename, writer):
    if os.path.isfile(filename):
        msg = f'Screenshot "{filename}" successfully created.'
    else:
        msg = f'Screenshot "{filename}" FAILED to create!'

    print(msg)
    writer.writerow([now(), 'screenshot', msg])

def main():
    login('standard_user', 'secret_sauce')

if __name__ == '__main__':
    main()

