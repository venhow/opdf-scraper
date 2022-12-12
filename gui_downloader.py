import requests
from multiprocessing import Pool
from bs4 import BeautifulSoup
import sqlite3
import signal
import logging

try:
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()
except Exception as e:
    logging.exception(e)
    exit()


def fetch_destination():
    import tkinter as tk
    from tkinter import filedialog

    with conn:
        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.askdirectory()
        cursor.execute("update current_file set name = (?);", (file_path,))
        conn.commit()


def get_destination():
    try:
        return list(cursor.execute("select name from current_file;"))[0][0]
    except:
        return []


def get_filename(url):
    return url.split("/")[-1].split("?")[0]


def download_file(url):
    from os.path import join

    try:
        destination = get_destination()
        filename = join(destination, get_filename(url))
        with open(filename, 'wb') as file:
            content = requests.get(url, stream=True).content
            file.write(content)
    except Exception as e:
        logging.exception(e)


def download(url):
    try:
        main_page = BeautifulSoup(requests.get(url).content, "html.parser")
        post_url = "https://oceanofpdf.com/please-wait-for-few-moments-3/"

        form_tag = main_page.find_all("form")[2]
        id = form_tag.find("input")['value']
        filename = form_tag.find("input").find("input")['value']

        headers = {"User-Agent": "Defined"}
        payload = {"id": id, "filename": filename}
        session = requests.session()
        res = session.post(post_url, headers=headers, data=payload)

        download_page = BeautifulSoup(res.content, "html.parser")
        link = download_page.find_all("meta")[-1]['content'][6:]
        print(link)
        try:
            download_file(link)
            with conn:
                conn.execute(f"UPDATE links SET completed = 1 WHERE link = '{url}'")
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)


if __name__ == "__main__":

    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)

    fetch_destination()
    count = list(cursor.execute("select count(*) from links where completed = 0 ORDER BY id;"))[0][0]
    count_total = list(cursor.execute("select count(*) from links;"))[0][0]
    count_done = count_total - count
    cycle_count = 0
    while count > 0:

        links = [record[0] for record in list(cursor.execute("SELECT link FROM links WHERE completed = 0 ORDER BY id LIMIT 200;"))]
        cycle_count += 1
        print(f"cycle {cycle_count}: [{count_done} / {count_total}]")
        with Pool(30) as p:
            signal.signal(signal.SIGINT, original_sigint_handler)
            try:
                p.map(download, links)
            except KeyboardInterrupt:
                p.terminate()
                exit()

        count = list(cursor.execute("select count(*) from links where completed = 0;"))[0][0]
        count_done = count_total - count

