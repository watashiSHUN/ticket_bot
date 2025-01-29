import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# webdriver works between selenium and chrome
# it translate commands from selenium into actions that Chrome can execute.
# TODO(shunxian): why use service? not needed
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

JAVASCRIPT_WAIT_TIME = 2  # seconds
PARKING_DATE = "February 8"  # Date to check parking availability


def check_parking_availability():
    url = "https://reservenski.parkstevenspass.com/select-parking"  # URL for Stevens Pass parking page

    driver = webdriver.Chrome()

    try:
        print(f"Opening URL: {url}")
        driver.get(url)
        # make the page full screen
        driver.maximize_window()
        time.sleep(JAVASCRIPT_WAIT_TIME)  # Wait for JavaScript to load the content

        # Scrape the page content
        page_content = driver.page_source

        with open("test.html", "w", encoding="utf-8") as file:
            file.write(page_content)
        print("Page content saved to test.html.")

        # NOTE: // Select the first element with the attribute 'data-id' and value '123': document.querySelector('[data-id="123"]');

        # NOTE: id/class they are all ATTRIBUTES, well defined ATTRIBUTES
        # logic in javascript:
        # let nodes = document.querySelectorAll('[aria-label="Saturday, February 1, 2025"]');
        # nodes[1].click();
        #
        # TODO(shunxian): use color to distinguish between available and unavailable
        # Example: Adjust selector to match parking info for February 1st
        # TODO(shunxian): we don't need day of the week.
        # DONE: //a[contains(@prop,'Foo')], https://stackoverflow.com/a/103417/1831108

        possible_date_divs = driver.find_elements(
            By.XPATH, f"//div[contains(@aria-label,'{PARKING_DATE}')]"
        )  # //*[contains(text(), 'February 1')]

        print(f"Found {len(possible_date_divs)} possible date divs.")

        # Create action chain object
        action = ActionChains(driver)

        if possible_date_divs:
            for date in possible_date_divs:
                print(f"Clicking on date div: {date}")
                # Click on the item
                action.click(on_element=date)
                # Perform the operation
                action.perform()

                print(f"Looking for carpool parking...")
                time.sleep(
                    JAVASCRIPT_WAIT_TIME
                )  # Wait for JavaScript to load the content

                # select carpool: `class="SelectRate_card__AT83w"`
                # or use text: "Carpool 4+ Arrival 7am - 10am, valid for all day parking"
                # Xpath: https://stackoverflow.com/questions/3813294/how-to-get-element-by-innertext
                # NOTE: xpath finds element in XML
                carpool_slot = driver.find_elements(
                    By.XPATH,
                    "//*[contains(text(), 'Carpool 4+ Arrival 7am - 10am, valid for all day parking')]",
                )

                if carpool_slot:
                    print("Find Carpool parking available!")
                    # assume there's only 1
                    # Click on the item
                    action.click(on_element=carpool_slot[0])
                    # Perform the operation
                    action.perform()

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        time.sleep(30)
        driver.quit()


if __name__ == "__main__":
    # TODO(shunxian): make a whileloop for busy pooling
    # TODO(shunxian): add login module
    # Uncomment the following lines to periodically check availability
    # while True:
    print("Checking parking availability...")
    check_parking_availability()
    # time.sleep(3600)  # Check every hour
