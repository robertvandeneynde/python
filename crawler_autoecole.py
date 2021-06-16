import requests
from bs4 import BeautifulSoup

r = requests.get('https://examen.autocontrole.be/Examen/')
soup = BeautifulSoup(r.text, 'html.parser')

def assert_one(x:list):
    assert len(x) == 1; return x[0]

node = assert_one(soup.find_all('input', attrs={'name': '__RequestVerificationToken'}))
r2 = requests.post(
    'https://examen.autocontrole.be/Examen/Home/CheckId',
    data={
        "ExpirationDate": "19/07/2026",
        node.get('name'): node.get('value'),
    },
    cookies=r.cookies
)
assert r2.status_code == 200
# with open('/home/robert/stuff.html', 'w') as f: f.write(r2.text)
soup2 = BeautifulSoup(r2.text, 'html.parser')
L = soup2.find_all('div', {'class': 'card-body'})
tt = 'Theoretisch examen Cat. B'
tt2 = 'Voorlopig hebben we geen beschikbare plaatsen meer. De planning zal worden geopend 2 weken voor de volgende beschikbare datum.'
divnode = next(l for l in L if tt in l.text)
if tt2 in divnode.text:
    print('nope')
else:
    print(divnode)
    print('YEP')
