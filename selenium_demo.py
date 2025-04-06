from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
import random

class Test():
    def __init__(self):
        """Test the code."""
        print("There exist link-test and web-test!")
        print("You can choose one of them by calling 'LinkTest()' or 'WebTest()'!")
        
    def LinkTest(self, browser):
        """Test the way of link"""
        def LinkFinder(browser, store=True):
            """Find all links in the website and store them into txt."""
            # Search for class
            containers = browser.find_elements(By.CLASS_NAME, "ProductList0__productItemContainer")
            # Extract link
            links = []
            for index, container in enumerate(containers):
                link = container.find_element(By.TAG_NAME, "a").get_attribute("href")
                links.append(link)
            # Store link
            if store:
                with open("D:/Code/crawler/links.txt", "w", encoding="utf-8") as file:
                    for link in links:
                        file.write(link + "\n")  
            # print(f"We have stored links into txt! Totally extract {len(links)}!")
            return links
        
        def LinkRedirect(browser, links):
            """Redirect the link."""
            for index, link in enumerate(links):
                if index >= 5:
                    break
                while True:
                    browser.get(link)
                    if browser.title != "Access Denied":
                        break
                    print("Website deny access! Refresh and retry!")
                    browser.refresh()
                    time.sleep(5)  
                time.sleep(3)
        
        
        links = LinkFinder(browser)
        LinkRedirect(browser, links)
    
    def WebTest(self, browser):
        print("Begin to test our code! Firstly visit Baidu!")
        browser.get("https://www.baidu.com/")
        print(browser.title)
        browser.find_element(By.NAME,'wd').send_keys("12343")
        browser.find_element(By.ID, 'su').click()
        time.sleep(5)
        
        print("Next visit a-porter!")
        browser.get("https://www.net-a-porter.com/en-us/")
        print(browser.title)
        time.sleep(5)
        
        print("Now you have pass all tests!")

class utils():
    def __init__(self):
        pass
    
    def _scroll_down_one_eighth(self, browser):
        """Scroll down the page by one eighth of the window height."""
        window_height = browser.execute_script("return window.innerHeight")
        scroll_distance = window_height // 8
        browser.execute_script(f"window.scrollBy(0, {scroll_distance});")

    def _find_next_key(self, browser):
        """Find the next key."""
        key = browser.find_elements(By.CLASS_NAME, "Pagination7__nextCopy")
        disableKey = browser.find_elements(By.CLASS_NAME, "Pagination7__nextCopy--disabled")
        if disableKey != []:
            return -1
        
        while key == []:
            self._scroll_down_one_eighth(browser)
            key = browser.find_elements(By.CLASS_NAME, "Pagination7__nextCopy")
            disableKey = browser.find_elements(By.CLASS_NAME, "Pagination7__nextCopy--disabled")
            if disableKey != []:
                return -1
            time.sleep(random.uniform(0.1, 0.3))
        return key[0]

    def _error_handle(self, browser):
        """Handle the error."""
        error = browser.find_element(By.CLASS_NAME, "ErrorPage6__link")
        time = 0
        while error != []:
            if time >= 5:
                print("Exit!")
                exit()
            print("Error found! Try to refresh the page!")
            browser.refresh()
            WebDriverWait(browser, 120)
            error = browser.find_element(By.CLASS_NAME, "ErrorPage6__link")
            time += 1

def OpenBrowser(port=9222):
    """Open a browser and return the browser object."""
    # Open edge
    def open_edge(port:int=9222):
        cmd_line=f'start msedge --remote-debugging-port={port}'
        cmd_line+=" --user-data-dir=D:\\Code\\crawler\\User2 "
        os.system(cmd_line)
    open_edge(port=port)
    return ControlBrowser(port)

def ControlBrowser(port):
    """Control the browser by port."""
    # Control edge
    edge_options=Options()
    edge_options.add_experimental_option('debuggerAddress',f'127.0.0.1:{port}')

    browser=webdriver.Edge(options=edge_options)
    return browser
    
def ExtractPagePath(browser, group, name):
    """Extrract the path of the clothing and model in one page."""
    containers = browser.find_elements(By.CLASS_NAME, "ProductList0__productItemContainer")
    # print(f"Find out {len(containers)} kinds of clothes!")
    
    for index, container in enumerate(containers):
        # sroll down util find the picture
        pictures = container.find_elements(By.TAG_NAME, "picture")
        while pictures == []:
            utils()._scroll_down_one_eighth(browser)
            pictures = container.find_elements(By.TAG_NAME, "picture")
            time.sleep(random.uniform(0.1, 0.3))
        
        # Extract path
        if len(pictures) < 2:
            print(f"No.{group+index}, no source found!")
            continue
        PathClothing = pictures[0].find_element(By.TAG_NAME, "source").get_attribute("srcset").split(",")[-1].split(" ")[1]
        PathModel = pictures[1].find_elements(By.TAG_NAME, "source")[-1].get_attribute("srcset").split(",")[-1].split(" ")[1]
        
        # Store path
        with open(f"D:\Code\crawler\links\Images-{name}.txt", "a", encoding="utf-8") as file:
            file.write(f"Page {group}, No.{index}:\n")
            file.write(PathClothing + "\n")
            file.write(PathModel + "\n")
        print(f"Page {group}, No.{index}")
        time.sleep(0.5)
        
    return len(containers)
        
def ExtractPath(browser, name="lingerie"):
    """Extract the path of the clothing and model."""
    group = 0
    while True:
        print("Page group:", group)
        # Extract the path of the clothing and model
        ExtractPagePath(browser, group, name=name)
        NextKey = utils()._find_next_key(browser)
        if NextKey == -1:
            break
        # Click the next key
        ActionChains(browser).move_to_element(NextKey).click(NextKey).perform()
        WebDriverWait(browser, 120)
        time.sleep(10)
        group += 1


if __name__=='__main__':
    browser = OpenBrowser(port=9222)
    Test().WebTest(browser)
    
    # Visit website
    # website = "https://www.net-a-porter.com/en-us/shop/clothing/lingerie"
    # while True:
    #     browser.get(website)
    #     if browser.title != "Access Denied":
    #         break
    #     print("Website deny access! Refresh and retry!")
    #     browser.refresh()
    #     time.sleep(random.uniform(0.5, 2))    

    # ExtractPath(browser, name='lingerie')


    time.sleep(10)
    browser.close()


