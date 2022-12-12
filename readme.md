# Ocean of PDF Scraper

It looked like [Ocean of PDF](https://oceanofpdf.com/) was going under becaues of the Ukraine war, so I decided to write a scraper to archive it.

## Usage

First install the requirements through pip, and then run `link_scraper.py` to scrape all the download links.
Run `downloader.py` after that to download the scraped links to a directory. If you require a GUI, run `gui_downloader.py`

```shell
python3 -m pip install requirements.txt
python3 link_scraper.py

python3 downloader.py
(or)
python3 gui_downloader.py
```
## LICENSE

Copyright (c) 2021 Krishna Sivakumar under [the MIT License](LICENSE).

