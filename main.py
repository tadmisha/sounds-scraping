import requests
from bs4 import BeautifulSoup as bs
from bs4 import Comment
from os import mkdir
from os.path import exists



def connect_lists(list_of_lists: list[list]) -> list:
    final_list = []
    for list in list_of_lists:
        final_list += list
    return final_list


def dict_to_zip(dict_: dict) -> zip:
    return zip(dict_.keys(), dict_.values())


def pages_amount_input() -> int:
    while True:
        try:
            pages_amount = int(input("How many pages do you want to scrape? "))
            if pages_amount > 0:
                return pages_amount
            else:
                print("Please enter a positive number")
        except ValueError:
            print("Please enter a number")


def folder_name_input() -> str: #check if name is appropriate
    invalid_symbols = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    while True:
        try:
            folder_name = input("What is the name of the folder? ")
            if folder_name == "":
                print("Please enter a folder name")
            else:
                for symbol in invalid_symbols:
                    if symbol in folder_name:
                        print("Invalid folder name")
                        break
                else:
                    return folder_name
        except ValueError:
            print("Please enter a folder name")
    


def download_from_url(name: str, url: str, path = ""):
    while path[-1] == '/':
        path = path[:-1]
    path += '/'
    content = requests.get(url).content
    with open(path+name, "wb") as file:
        file.write(content)


def get_html(url: str) -> str:
    r = requests.get(url)
    html = r.text
    print("Scraped web")
    return html


def get_soup(html: str) -> bs:
    soup = bs(html, 'html.parser')
    return soup


def get_page_sounds_urls(soup: bs) -> zip:
    elements = soup.find_all(class_="shead")
    urls = {element.text: element.find("a").get("href") for element in elements}
    print("Scraped urls")
    return dict_to_zip(urls)


def get_all_sounds_departments(url: str, pages_amount: int) -> zip:
    urls = {}
    for page in range(1, pages_amount+1):
        print("Scraping page №"+str(page))
        html = get_html(url+str(page))
        soup = get_soup(html)
        page_urls = get_page_sounds_urls(soup)
        urls |= page_urls
        print("\n")
        
    return dict_to_zip(urls)


def get_audios(sounds_url: str) -> zip:
    r = requests.get(sounds_url).text
    soup = bs(r, 'html.parser')
    title_divs = soup.find_all('div', class_=None, id=None)
    titles = [div.get_text(strip=True) for div in title_divs[2] \
        if not ((not div.get_text(strip=True)) or ("Скачать" in div.get_text(strip=True)) or ("Тип файла: " in div.get_text(strip=True)))] \
        + [div.get_text(strip=True) for div in title_divs[3] \
        if not ((not div.get_text(strip=True)) or ("Скачать" in div.get_text(strip=True)) or ("Тип файла: " in div.get_text(strip=True)))]
    urls = [comment.extract()[16:] for comment in soup.findAll(string=lambda text:isinstance(text, Comment) and "dle_audio_begin" in text)]

    return zip(titles, urls)


def download_audios(sounds_departments: list[list[str]], sounds_folder: str):
    if not exists(sounds_folder):
        mkdir(sounds_folder)

    for sounds_title, sounds_url in sounds_departments:
        mkdir(f"{sounds_folder}/{sounds_title}")
        print("Scraping "+sounds_title)
        audios = get_audios(sounds_url)
        for title, url in audios:
            print("\tDownloading "+title+"...")
            download_from_url(title+".mp3", url, f"{sounds_folder}/{sounds_title}")
        print("\n")



def main():
    url = "https://zvukipro.com/page/"
    sounds_folder = folder_name_input()
    pages_amount = pages_amount_input()
    print("Start working")
    sounds_departments = get_all_sounds_departments(url, pages_amount)
    download_audios(sounds_departments, sounds_folder)


if __name__ == "__main__":
    main()