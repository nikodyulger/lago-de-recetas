import pymupdf
from bs4 import BeautifulSoup


doc = pymupdf.open("1000-recetas-oro-arguinano.pdf")

# print(doc.page_count)
print(doc.get_toc())
# print(doc.metadata)

html = ""
for i in range(9,49):
    page = doc.load_page(i)
    html += page.get_text("html")

soup = BeautifulSoup(html, 'html.parser')

titles = soup.select("[style*='font-size:21.0pt']")[-1] # títulos
subtitles = soup.select("[style*='font-size:17.2pt']")[-2:]
ingredientes = soup.select("[style*='font-size:15.0pt']")
# print(html)
print([t.text for t in titles])
# print([i.text for i in ingredientes])
# print([s for s in subtitles])
content = []
for tag in subtitles[0].find_all_next():
    if tag.text == subtitles[1].text:
        break
    content.append(tag)
    
print(content)
# page = doc.load_page(46)
# print(page.get_text("html"))