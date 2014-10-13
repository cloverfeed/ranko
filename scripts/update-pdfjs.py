"""
Download latest pdf.js into a relevant subdirectory of static/vendor.
"""

import bs4
import os
import requests
import tempfile
import zipfile


def latest_pdfjs_url():
    dl_url = 'http://mozilla.github.io/pdf.js/getting_started/'
    content = requests.get(dl_url).text
    bs = bs4.BeautifulSoup(content)
    links = [link for link in bs.find_all("a") if "Stable" in link.text]
    return links[0]['href']


def download_file(url, handle):
    response = requests.get(url, stream=True)
    assert response.ok, response
    for block in response.iter_content(1024):
        if not block:
            break
        handle.write(block)


def main():
    print "Getting latest pdfjs URL"
    url = latest_pdfjs_url()
    (tempfd, _) = tempfile.mkstemp()
    temp = os.fdopen(tempfd, "r+")
    print "Downloading latest pdfjs"
    download_file(url, temp)
    temp.seek(0)
    zip = zipfile.ZipFile(temp)
    base_dir = url.split('/')[-1][:-4]
    out_path = os.path.join('static/vendor', base_dir)
    print "Extracting relevant files"
    zip.extract('build/pdf.js', out_path)
    zip.extract('build/pdf.worker.js', out_path)


if __name__ == '__main__':
    main()
