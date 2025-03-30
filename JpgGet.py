from selenium.webdriver.common.by import By
import time
from selenium_demo import OpenBrowser
import base64
import re
import os
from tqdm import tqdm



def DownloadOneImage(driver, image_url, save_path="downloaded_image.jpg", max_retries=5):
    """Download from website"""
    for attempt in range(max_retries):
        try:
            print(f"Try to download: {image_url}(No.{attempt + 1})")
            driver.get(image_url)
            time.sleep(2)  
            
            img_element = driver.find_element(By.TAG_NAME, "img")
            img_src = img_element.get_attribute("src")

            if img_src.startswith("data:image"):
                base64_string = img_src.split(',')[1]
                img_data = base64.b64decode(base64_string)
            else:
                img_data = driver.execute_script("""
                    return fetch(arguments[0], { credentials: 'include' })
                        .then(response => {
                            if (!response.ok) throw new Error('Fetch failed: ' + response.status);
                            return response.blob();
                        })
                        .then(blob => new Promise((resolve) => {
                            const reader = new FileReader();
                            reader.onloadend = () => resolve(reader.result);
                            reader.readAsDataURL(blob);
                        }))
                        .then(dataUrl => dataUrl.split(',')[1])
                        .catch(error => { throw error; });
                """, img_src)
                img_data = base64.b64decode(img_data)

            with open(save_path, "wb") as f:
                f.write(img_data)
            return True
        
        except Exception as e:
            print(f"Error when download: {image_url}\n{e}")
            if attempt < max_retries - 1:
                time.sleep(2)  
                continue
            exit()

def DownloadImage(driver, urls, save_path):
    """Read txt to extract url, download and save at certain path"""
    index = 0
    for url in urls:
        # Extract urls
        url_dict = {}
        current_key = None
        
        with open(url, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                page_match = re.match(r"Page (\d+), No\.(\d+):", line)
                if page_match:
                    page, no = page_match.groups()
                    current_key = (int(page), int(no))
                    url_dict[current_key] = []
                elif line.startswith("//") and current_key is not None:
                    url = "https:" + line
                    url_dict[current_key].append(url)
        
        # Makedir 
        PathCloth = os.path.join(save_path, "clothes")
        PathModel = os.path.join(save_path, "models")
        os.makedirs(PathCloth, exist_ok=True)
        os.makedirs(PathModel, exist_ok=True)
        
        # Download
        for (page, no), urls in tqdm(url_dict.items()):
            path1 = os.path.join(PathCloth, "{:06d}.jpg".format(index))
            path2 = os.path.join(PathModel, "{:06d}.jpg".format(index))
            DownloadOneImage(driver, urls[1], path2) 
            DownloadOneImage(driver, urls[0], path1) 
            index += 1
            

if __name__ == '__main__':
    browser = OpenBrowser(9222)
    urls = [
        "D:\Code\crawler\links\Images-lingerie.txt",
        "D:\Code\crawler\links\Images-shorts.txt",
        "D:\Code\crawler\links\Images-skirts.txt",
        "D:\Code\crawler\links\Images-sports.txt",
        "D:\Code\crawler\links\Images-swimwear.txt",
        "D:\Code\crawler\links\Images-tops.txt",
    ]
    save_path = "D:\Model_Data\Datasets\\video_dressup"
    DownloadImage(browser, urls, save_path)
