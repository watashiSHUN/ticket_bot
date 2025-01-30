import os
import time

import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

load_dotenv()
# webdriver works between selenium and chrome
# it translate commands from selenium into actions that Chrome can execute.
# TODO(shunxian): why use service? not needed
from selenium.webdriver.chrome.service import Service

# NOTE: not used
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

JAVASCRIPT_WAIT_TIME = 2  # seconds
PARKING_DATE = "February 1"  # Date to check parking availability


def login(driver):
    # Go to the login page
    driver.get("https://reservenski.parkstevenspass.com/login")
    time.sleep(JAVASCRIPT_WAIT_TIME)  # Wait for JavaScript to load the content

    # Find the username field
    username = driver.find_element(By.ID, "emailAddress")
    # Enter the username
    username.send_keys(os.getenv("STEVENS_PASS_USERNAME"))

    # Find the password field
    password = driver.find_element(By.ID, "password")
    # Enter the password
    password.send_keys(os.getenv("STEVENS_PASS_PASSWORD"))

    # Find the login button
    login_button = driver.find_element(By.XPATH, "//button[text()='Login']")

    # Click the login button
    login_button.click()

    # Wait for the page to load
    time.sleep(JAVASCRIPT_WAIT_TIME)


def check_parking_availability(driver):
    url = "https://reservenski.parkstevenspass.com/select-parking"  # URL for Stevens Pass parking page

    try:
        print(f"Opening URL: {url}")
        driver.get(url)
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

        if possible_date_divs:
            for date in possible_date_divs:
                print(f"Clicking on date div: {date}")
                try:
                    date.click()
                except Exception as e:
                    print(f"Error clicking on date div: {e}")
                    continue  # try next click

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
                    try:
                        carpool_slot[0].click()
                        # redirect to honk, click on park for free
                        time.sleep(JAVASCRIPT_WAIT_TIME * 3)
                        reserve = driver.find_element(
                            By.XPATH, "//*[contains(text(), 'Park For Free')]"
                        )
                        reserve.click()
                        time.sleep(JAVASCRIPT_WAIT_TIME)
                        confirm = driver.find_element(
                            By.XPATH, "//*[contains(text(), 'Confirm')]"
                        )
                        confirm.click()
                    except Exception as e:
                        print(f"Error clicking on carpool slot: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        time.sleep(10)
        driver.quit()


if __name__ == "__main__":
    while True:
        # Create a new instance of the Chrome driver
        driver = webdriver.Chrome()
        # make the page full screen
        driver.maximize_window()

        # TODO(shunxian): make a whileloop for busy pooling
        # TODO(shunxian): add login module
        # Uncomment the following lines to periodically check availability
        login(
            driver
        )  # TODO(shunxian): Store cookie instead of store username/password (although, if its only on my laptop, maybe it's ok)
        check_parking_availability(driver)
        time.sleep(1800)  # Check every hour
