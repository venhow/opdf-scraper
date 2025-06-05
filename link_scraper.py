from requests import get
from bs4 import BeautifulSoup
from multiprocessing import Pool
import sqlite3

headers = {'Accept-Encoding': 'identity', 'User-Agent': 'Defined'}
conn = sqlite3.connect("links.db", check_same_thread = False)
cursor = conn.cursor()
cursor.execute("create table if not exists links (url text)")

def scrape(page):
    url = f"https://oceanofpdf.com/recently-added/page/{page}"
    print(page)
    try:
        html = BeautifulSoup(get(url, headers=headers).text, "html.parser")
        for article in html.find_all("article"):
            href = article.find("a")['href']
            try:
                cursor.execute(f"INSERT INTO links(link) VALUES ('{href}');")
                cursor.execute(f"UPDATE pages SET scraped = 1 WHERE page = (?);", (page,))
                conn.commit()
            except sqlite3.IntegrityError:
                pass
    except Exception as e:
        print(e)

if __name__ == "__main__":
    count = list(cursor.execute("select count(*) from pages where scraped = 0;"))[0][0]
    cycle = 0

    while count > 0:
        cycle += 1
        print(f"cycle {cycle}")
        pages = [record[0] for record in list(cursor.execute("SELECT page FROM pages WHERE scraped = 0 LIMIT 1000;"))]
        with Pool(8) as p:
            p.map(scrape, pages)

        count = list(cursor.execute("select count(*) from pages where scraped = 0;"))[0][0]

    conn.close()
