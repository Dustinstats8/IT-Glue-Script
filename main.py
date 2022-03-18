from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import requests
import time
import pprint

# IT Glue credentials
email = 'dustin.simmons@simplymac.com'
password = 'Trivium8'

api_key = '80cdd6b20c5fe7459dca7994408c1d5c.qGYUYXu6xLMI-lQD4KBo5gKqbt73CwEDsR3YbABy9tUqfO4Hm5hSEK21mYKqYkOJ'
org_id = 5022710

# Create browser object
options = webdriver.ChromeOptions()
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
# Set window size, otherwise --headless will break
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome('./chromedriver', options=options)
# driver = webdriver.Firefox(executable_path='./geckodriver')

# ActionChains object
action = ActionChains(driver)

global loop_range
# list for configurations that will be appended after API call
url_list = []
url_list2 = []


def config_api_call():
    # header with API key to enable API calls
    headers = {
        'x-api-key': 'ITG.80cdd6b20c5fe7459dca7994408c1d5c.qGYUYXu6xLMI-lQD4KBo5gKqbt73CwEDsR3YbABy9tUqfO4Hm5hSEK21mYKqYkOJ',
        'Content-Type': 'application/vnd.api+json',
        'Cache-Control': 'no-cache'
    }

    # PrettyPrint displays an easy to read JSON object (or just nested dictionary objects)
    pp = pprint.PrettyPrinter(indent=4)

    ###################################################################################################################
    # To add parameters to API call, edit the following URL                                                           #
    # example: 'page[size]=1000' sets the amount of configurations to be returned from the call                       #
    ###################################################################################################################
    # At the time of this comment, there are 1134 configurations. To get around the 1000 result limit in IT Glue API, #
    # split response into two variables that return 600 results each by adjusting the page size and page number       #
    ###################################################################################################################
    response = requests.get(
        'https://api.itglue.com/organizations/{0}/relationships/configurations?page[size]=600'
        .format(org_id), headers=headers
    )
    response2 = requests.get(
        'https://api.itglue.com/organizations/{0}/relationships/configurations?page[size]=600&page[number]=2'
        .format(org_id), headers=headers
    )

    pp.pprint(response2.json())

    # return response as python json object and find length
    json_object = response.json()
    json_object_len = len(json_object['data'])

    json_object2 = response2.json()
    json_object_len2 = len(json_object2['data'])

    ###################################################################################################################
    # The API call returns each configuration including ALL attributes. For this script, the only important attribute #
    # to grab is the URL which will be appended to the 'url_list' list. Each URL will then be opened in the automated #
    # Selenium browser window where they will be moved to the IT security group one by one due to IT Glue not having  #
    # the ability to perform bulk moves                                                                               #
    ###################################################################################################################
    # When appending to the list you see "['data'][counter]['attributes']['resource-url']" which is pathing out what  #
    # specific attribute I want appended which in this case is simply the URL of the configuration. The counter       #
    # variable is used to iterate through all the configurations pulled                                               #
    ###################################################################################################################

    # append each configuration from the json object to the previously created list
    counter = 0
    for i in range(json_object_len):
        url_list.append(json_object['data'][counter]['attributes']['resource-url'])
        counter += 1

    counter2 = 0
    for i in range(json_object_len2):
        url_list2.append(json_object2['data'][counter2]['attributes']['resource-url'])
        counter2 += 1

    response.close()
    response2.close()
    return url_list, url_list2


def locationTable():
    tic = time.perf_counter()
    driver.get("https://simply-mac.itglue.com/")
    driver.find_element_by_xpath(
        '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div/div[1]/div/div[1]/input'
    ).send_keys(email, Keys.RETURN)
    driver.find_element_by_xpath(
        '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input'
    ).send_keys(password, Keys.RETURN)
    driver.find_element_by_xpath('/html/body/div/div/div/section/div[2]/div/form/div[4]/input').click()
    driver.implicitly_wait(10)
    driver.find_element_by_xpath(
        '/html/body/div[1]/section/div/div/div/div[3]/div[2]/div/div[1]/div/div[2]/div/table/tbody/tr[3]/td[3]/a').click()
    driver.implicitly_wait(10)
    driver.find_element_by_xpath('/html/body/div[1]/section/div/div[1]/div/div[3]/nav/ul/li[9]/a/div/span').click()
    driver.implicitly_wait(10)

    # Get list of column web elements and get hrefs from each one
    all_tds = driver.find_elements_by_xpath(
        '//table[@class="react-table-inner"]//td[@class="column-name column-is-primary ellipsis"]'
        '//a')
    urls = []
    for i in all_tds:
        urls.append(i.get_attribute('href'))
    urls_len = len(urls)

    print('Table found.. Urls grabbed.. \nList length:', urls_len)

    true_check = 0
    false_check = 0

    driver.implicitly_wait(10)

    for x in range(urls_len):
        print(x + 1, '------------------------', x + 1, sep='')

        # iterate through list of hrefs and open each one in a new tab
        driver.execute_script('''window.open("{0}");'''.format(urls[x]))
        driver.switch_to.window(driver.window_handles[1])
        driver.get(urls[x])
        driver.implicitly_wait(10)
        driver.find_element_by_xpath('/html/body/div[1]/section/div/div[3]/div[1]/span[1]/a').click()
        driver.implicitly_wait(10)
        driver.find_element_by_id('location_accessible_option_specify').click()
        driver.implicitly_wait(10)

        # if block to check if location needs to be added to IT group
        checker = driver.find_element_by_xpath('//*[@id="location_resource_access_group_ids_48500"]').is_selected()
        if checker:
            print('|  Entering TRUE block.. |')
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            true_check += 1
            print('|  Leaving TRUE block..  |')
            print(x + 1, '------------------------', x + 1, '\n', sep='')
        else:
            print('|  Entering FALSE block.. |')
            driver.find_element_by_class_name('toggle-view-all').click()
            driver.implicitly_wait(10)
            driver.find_element_by_id('location_resource_access_group_ids_48500').click()
            driver.implicitly_wait(10)
            driver.find_element_by_xpath('//input[@class="btn btn-success btn-lg"]').click()
            driver.implicitly_wait(10)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            false_check += 1
            print('|  Leaving False block..  |')
            print(x + 1, '------------------------', x + 1, '\n', sep='')

    # Timer to track runtime and print run statistics
    toc = time.perf_counter()
    total_time = (toc - tic) / 60
    print('-------------------------------------------')
    print('Locations Adjustment Runtime:', round(total_time, 2), 'minutes')
    print('Updated', false_check, 'Locations')
    print(true_check, ' Locations were unaffected', sep='')
    print('-------------------------------------------')
    driver.quit()


def configurations():
    # Counter to report time it took for script to complete
    tic = time.perf_counter()

    # Navigating to website, logging in, selecting IT organization, and selecting configurations tab
    # Print statements simply confirm this
    driver.get("https://app.itglue.com/")
    driver.find_element_by_xpath('//*[@id="sessions"]/div/div/form/label[2]/div/input').send_keys(email)
    driver.find_element_by_xpath('//*[@id="sessions"]/div/div/form/div/label/div/input').send_keys(password)
    driver.find_element_by_xpath('//*[@id="sessions"]/div/div/form/button').click()
    driver.implicitly_wait(10)
    driver.find_element_by_xpath('//*[@id="organizations"]/a').click()
    print("Logged in and selected Organizations")
    driver.implicitly_wait(10)
    driver.find_element_by_xpath(
        '//*[@id="react-main"]/div/div[3]/div[2]/div/div[1]/div/div[2]/div/table/tbody/tr[1]/td[3]/a'
    ).click()
    print("Selected IT org")
    driver.implicitly_wait(10)
    driver.find_element_by_xpath('/html/body/div[1]/section/div/div[1]/div/div[3]/nav/ul/li[4]/a/span[1]').click()
    driver.implicitly_wait(10)
    print("Navigated to Configurations")

    time.sleep(3)

    # API call to pull configurations
    config_api_call()

    time.sleep(5)

    print('\nNumber of Configurations wave 1:', len(url_list))
    print('\nNumber of Configurations wave 2:', len(url_list2), '\n')

    # Counters to report number of True/False blocks after script completes
    true_check = 0
    false_check = 0

    ###################################################################################################################
    # The list pulled from the API call isn't alphabetized like the website, however, it does seem to be in the same  #
    # order everytime meaning that updating in waves should not be a problem.                                         #
    ###################################################################################################################

    for x in range(len(url_list)):
        print(x + 1, '------------------------', x + 1, sep='')

        # Open browser tab for each configuration URL in the list from the API call
        driver.execute_script('''window.open("{0}");'''.format(url_list[x]))

        # Switch focus from original tab to newly opened configuration URL
        driver.switch_to.window(driver.window_handles[1])
        driver.implicitly_wait(10)
        # I have no idea why sleeping for 2 seconds fixed this whole block but don't remove it
        time.sleep(3)

        ###############################################################################################################
        # IMPORTANT: Notice that find_element(s) is used here instead of find_element like everywhere else            #
        # This is because when find_elements is used and the element isn't found, an empty list is returned and       #
        # when find_element is used and the element isn't found, it throws an exception                               #
        ###############################################################################################################
        # Click 'edit' button if it's found
        if driver.find_elements_by_xpath(
                '/html/body/div[1]/section/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/a[1]'):
            driver.find_element_by_xpath(
                '/html/body/div[1]/section/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/a[1]').click()
            driver.implicitly_wait(60)

        time.sleep(2)

        # Click 'Specific Groups and/or Users can access this Configuration' radio button
        driver.execute_script('arguments[0].click();', WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((
                By.XPATH, '/html/body/div[1]/section/div/div[2]/form/div[2]/div/div[1]/div[2]/label'))))

        driver.implicitly_wait(10)

        # Click 'View Groups' dropdown menu
        driver.execute_script('arguments[0].click();', WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((
                By.XPATH, '/html/body/div[1]/section/div/div[2]/form/div[2]/div/div[2]/div/div/div[1]/div/div[2]'))))

        driver.implicitly_wait(10)
        time.sleep(1)

        # if block to check if location needs to be added to IT group
        driver.execute_script('arguments[0].click();', WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((
                By.XPATH, '/html/body/div[1]/section/div/div[2]/form/div[2]/div/div[1]/div[2]'))))

        driver.implicitly_wait(10)

        checker = driver.find_element_by_xpath(
            '/html/body/div[1]/section/div/div[2]/form/div[2]/div/div[2]/div/div/div[1]/div/div[3]/span[1]/label/input'
        )
        if checker.is_selected():
            print('|  Entering TRUE block.. |')
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            true_check += 1
            print('|  Leaving TRUE block..  |')
            print(x + 1, '------------------------', x + 1, '\n', sep='')
        else:
            print('|  Entering FALSE block.. |')
            driver.execute_script('arguments[0].click();', WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '/html/body/div[1]/section/div/div[2]/form/div[2]/div/div[2]/div/div/div[1]/div/div[3]/span[1]/label/input'))))
            driver.implicitly_wait(10)
            driver.execute_script('arguments[0].click();', WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//input[@class="btn btn-success btn-lg"]'))))
            driver.implicitly_wait(10)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            false_check += 1
            print('|  Leaving False block..  |')
            print(x + 1, '------------------------', x + 1, '\n', sep='')

    for x in range(len(url_list2)):
        print(x + 1, '------------------------', x + 1, sep='')

        # Open browser tab for each configuration URL in the list from the API call
        driver.execute_script('''window.open("{0}");'''.format(url_list2[x]))

        # Switch focus from original tab to newly opened configuration URL
        driver.switch_to.window(driver.window_handles[1])
        driver.implicitly_wait(10)
        # I have no idea why sleeping for 2 seconds fixed this whole block but don't remove it
        time.sleep(3)

        # Click 'edit' button
        driver.find_element_by_xpath(
            '/html/body/div[1]/section/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/a[1]').click()
        driver.implicitly_wait(60)

        time.sleep(2)

        # Click 'Specific Groups and/or Users can access this Configuration' radio button
        driver.execute_script('arguments[0].click();', WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((
                By.XPATH, '/html/body/div[1]/section/div/div[2]/form/div[2]/div/div[1]/div[2]/label'))))

        driver.implicitly_wait(10)

        # Click 'View Groups' dropdown menu
        driver.execute_script('arguments[0].click();', WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((
                By.XPATH, '/html/body/div[1]/section/div/div[2]/form/div[2]/div/div[2]/div/div/div[1]/div/div[2]'))))

        driver.implicitly_wait(10)
        time.sleep(1)

        # if block to check if location needs to be added to IT group
        driver.execute_script('arguments[0].click();', WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((
                By.XPATH, '/html/body/div[1]/section/div/div[2]/form/div[2]/div/div[1]/div[2]'))))

        driver.implicitly_wait(10)

        checker = driver.find_element_by_xpath(
            '/html/body/div[1]/section/div/div[2]/form/div[2]/div/div[2]/div/div/div[1]/div/div[3]/span[1]/label/input'
        ).is_selected()
        if checker:
            print('|  Entering TRUE block.. |')
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            true_check += 1
            print('|  Leaving TRUE block..  |')
            print(x + 1, '------------------------', x + 1, '\n', sep='')
        else:
            print('|  Entering FALSE block.. |')
            driver.execute_script('arguments[0].click();', WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '/html/body/div[1]/section/div/div[2]/form/div[3]/div/div[2]/div/div/div[1]/div/div[3]/span[1]/label/input'))))
            driver.implicitly_wait(10)
            driver.execute_script('arguments[0].click();', WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//input[@class="btn btn-success btn-lg"]'))))
            driver.implicitly_wait(10)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            false_check += 1
            print('|  Leaving False block..  |')
            print(x + 1, '------------------------', x + 1, '\n', sep='')


    # Timer to track runtime and print run statistics
    toc = time.perf_counter()
    total_time = (toc - tic) / 60
    print('-------------------------------------------')
    print('Configurations Runtime:', round(total_time, 2), 'minutes')
    print('Updated', false_check, 'configurations')
    print(true_check, ' Configurations were unaffected', sep='')
    print('-------------------------------------------')
    driver.quit()


def main():
    # locationTable()
    # time.sleep(3)
    configurations()


main()
