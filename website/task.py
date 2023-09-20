import requests
from bs4 import *
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import json
import threading
import time

web_url = "https://www.amazon.in/dp/{}"


def main_image(images):
    dynamic_main = [_img.get('data-a-dynamic-image') for _img in images if _img.get('data-a-dynamic-image')]
    img_obj = json.loads(dynamic_main[0])
    return max(zip(img_obj.values(), img_obj.keys()))[1]
    # breakpoint()
    # for k, v in img_obj.items():
    #     if v == [679, 509]:
    #         return k
    #     elif v == [741, 556]:
    #         return k
    #     elif v == [879, 659]:
    #         return k
    #     elif v == [606, 455]:
    #         return k
    #     elif v == [550, 413]:
    #         return k
    #     elif v == [500, 375]:
    #         return k
    #     else:
    #         return k


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
    # img_link = ""
    if len(images)!=0:
        for i, image in enumerate(images):
            img_link = image
            # try:
            #     img_link = image['data-srcset']
            # except:
            #     try:
            #         img_link = image['data-src']
            #     except:
            #         try:
            #             img_link = image['data-fallback-src']
            #         except:
            #             try:
            #                 img_link = image['src']
            #             except:
            #                 try:
            #                     img_link = image
            #                 except:
            #                     pass

            try:
                if img_link:
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


def make_request(url, asin=None, path=None, filter_list=None):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    WebDriverWait(driver, 1)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.quit()
    if not asin and not path:
        return soup
    filter_list.append(main_image(soup.findAll('img')))
    return filter_list


def send_to_beautiful_soup(url, asin, path):
    soup = make_request(url)
    images, variants = soup.findAll('img'), soup.findAll('li')
    filter_list, var_asins = [], []
    filter_list.append(main_image(soup.findAll('img')))
    # var_asins = [asin.get('data-asin') for asin in variants if asin.get('data-asin')]
    for _asin in variants:
        # if _asin.get('data-csa-c-action') == "image-block-alt-image-hover" or _asin.get("data-csa-c-type") =="uxElement":
        if _asin.get('data-asin'):
            var_asins.append(_asin.get('data-asin'))
        elif _asin.get('data-csa-c-item-id'):
            var_asins.append(_asin.get('data-csa-c-item-id'))
        elif _asin.get('data-defaultasin'):
            var_asins.append(_asin.get('data-defaultasin'))
    # ["dimension-value-list-item-square-image",
    #  "inline-twister-swatch", "reduced-image-swatch-margin",
    #  "a-declarative", "desktop-configurator-dim-row-0"]
    tasks = []
    for _a in var_asins:
        url = web_url.format(_a)
        tasks.append(threading.Thread(target=make_request, args=(url, _a, path, filter_list)))
        tasks[-1].start()
        time.sleep(2)
    for t in tasks:
        t.join()
        time.sleep(1)
    # return filter_list
    return download_images(filter_list, asin, path)


def bulk_download(request, url, data):
    # asin_list = data['asin'].split(",")
    # for asin in asin_list:
    #     web_url = url.format(asin)
    #     send_to_beautiful_soup(web_url, asin, data['path'])
    # return True
    asin_list = data['asin'].split(",")
    tasks = []
    for asin in asin_list:
        web_url = url.format(asin)
        tasks.append(threading.Thread(target=send_to_beautiful_soup, args=(web_url, asin, data['path'])))
        tasks[-1].start()
        time.sleep(5)
    for t in tasks:
        t.join()
        time.sleep(1)
    return True
