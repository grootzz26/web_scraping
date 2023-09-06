import requests
from bs4 import *
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def bulk_url_format(data, url):
    asin_list = data['asin'].split(",")
    url_list, path_list = [], []
    for asin in asin_list:
        u = url.format(asin)
        url_list.append(u)

    return url_list, path_list


def download_images(images, asin, path):
    count = 0
    print(f"Total {len(images)} images found in asin {asin}")
    if len(images)!=0:
        for i, image in enumerate(images):
            try:
                img_link = image['data-srcset']
            except:
                try:
                    img_link = image['data-src']
                except:
                    try:
                        img_link = image['data-fallback-src']
                    except:
                        try:
                            img_link = image['src']
                        except:
                            pass

            try:
                r = requests.get(img_link).content
                try:
                    r = str(r, 'utf-8')
                except UnicodeDecodeError:

                    if i == 0:
                        with open(f"{path}/{asin}/main.jpg", "wb+") as f:
                            f.write(r)
                    else:
                        with open(f"{path}/{asin}/images{i+1}.jpg", "wb+") as f:
                            f.write(r)

                    count += 1
            except:
                pass
        if count == len(images):
            print("All Images Downloaded!")

            # if all images not download
        else:
            print(f"Total {count} Images Downloaded Out of {len(images)}")
        return True
    else:
        print("No images found")
        return False


def send_to_beautiful_soup(url, asin, path):
    # options = webdriver.FirefoxOptions()
    # firefox_options = options.add_argument('--headless')
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source)
    driver.quit()
    images = soup.findAll('img')
    filter_list = []
    for img in images:
        if len(filter_list) == 0:
            if not img.get('class') and not img.get('alt') and 'jpg' in img.get("src"):
                filter_list.append(img)
        if len(filter_list) >= 1 and img.get('class') and img.get('class') == ["swatch-image", "inline-twister-manual-load"]:
            if img.get('src'):
                filter_list.append(img)

    return download_images(filter_list, asin, path)


def bulk_download(request, url, data):
    asin_list = data['asin'].split(",")
    for asin in asin_list:
        web_url = url.format(asin)
        show_result = send_to_beautiful_soup(web_url, asin, data['path'])
    return True
