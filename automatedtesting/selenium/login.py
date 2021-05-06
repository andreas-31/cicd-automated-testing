# #!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


# Start the browser and login with standard_user
def login (username, password):
    print('Starting the browser...')
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
    print('Browser started successfully. Navigating to URL:', url)
    driver.get(url)
    print("We are on the login page.")
    driver.save_screenshot('01_login_page.png')

    print('\n=== LOGIN ===')
    print(f'Trying to login as user {username}')
    driver.find_element_by_css_selector("input[id='user-name']").send_keys(username)
    driver.find_element_by_css_selector("input[id='password']").send_keys(password)
    print('> Clicking on the login button')
    driver.find_element_by_css_selector("input[id='login-button']").click()
    
    print('Checking that login was successful.')
    assert driver.find_element_by_id('logout_sidebar_link'), '> ERROR: Login to URL "{}" failed!'.format(url)
    print(f'> OK: Login to URL "{url}" with user name "{username}" successful!')

    print('\n=== ADD ITEMS ===')
    print("We are on the main page.")
    added_items = list()
    removed_items = list()
    print('Looking for items to add to cart')
    items = driver.find_elements_by_class_name('inventory_item')
    for count, item in enumerate(items, 1):
        item_name = item.find_element_by_class_name('inventory_item_name')
        added_items.append(item_name.text)
        print('Adding to cart item {}: "{}"'.format(count, item_name.text))
        item.find_element_by_css_selector("button[class='btn btn_primary btn_small btn_inventory']").click()
        
    driver.save_screenshot('02_main_page_items_added.png')

    print('\n=== CHECK SHOPPING CART ===')
    print('Opening shopping cart to check listed items')
    shopping_cart_link = driver.find_element_by_class_name('shopping_cart_container')
    shopping_cart_link.click()
    print("We are on the shopping cart page.")
    driver.save_screenshot('03_shopping_cart_page.png')
    
    print('Checking that previously added {} items are really in the shopping cart'.format(len(added_items)))
    print(', '.join(added_items))
    for count, my_item in enumerate(added_items, 1):
        print('Checking item {}: "{}"'.format(count, my_item))
        shopping_cart_items = driver.find_elements_by_class_name('inventory_item_name')
        assert my_item in [i.text for i in shopping_cart_items], \
            '> ERROR: item "{}" is NOT in the shopping cart!'.format(my_item)
        print('> OK: item "{}" is in the shopping cart!'.format(my_item))

    print('\n=== REMOVE ITEMS ===')
    print('Removing items from the shopping cart')
    for count, my_item in enumerate(added_items, 1):
        removed_items.append(my_item)
        print('Removing item {}: "{}"'.format(count, my_item))
        for cart_item in driver.find_elements_by_class_name('cart_item_label'):
            if cart_item.find_element_by_class_name('inventory_item_name').text == my_item:
                print('Click on remove button for item "{}"'.format(my_item))
                cart_item.find_element_by_css_selector("button[class='btn btn_secondary btn_small cart_button']").click()
                driver.save_screenshot(f'04_shopping_cart_page_item_{count}_removed.png')
        
        print('Checking that item "{}" has really been removed from shopping cart'.format(my_item))
        assert my_item not in [i.text for i in driver.find_elements_by_class_name('inventory_item_name')], \
            '> ERROR: item "{}" has NOT been removed from shopping cart!'.format(my_item)
        print('> OK: item "{}" has been removed from shopping cart!'.format(my_item))

    print('All UI tests with Selenium finshed successfully!')
    driver.stop_client()
    driver.close()
    driver.quit()

def main():
    login('standard_user', 'secret_sauce')

if __name__ == '__main__':
    main()

