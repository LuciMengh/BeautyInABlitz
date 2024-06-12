
from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# GET-Anfrage durchführen
def setService(service):
    services = {
        'Damenhaarschnitt': 'damenhaarschnitt',
        'Herrenhaarschnitt': 'herrenhaarschnitt',
        'Manikuere': 'manikuere',
        'Pedikuere': 'pedikure',
        'IPL dauerhafte Haarentfernung': 'ipl-dauerhafte-haarentfernung',
        'Gesichtsbehandlungen': 'gesichtsbehandlungen',
        'Entspannungsmassage': 'entspannungsmassage',
        'Thaimassage': 'thaimassage'
    }

    return services.get(service, 'damenhaarschnitt')

def setPreferedLocation(location):
    locations = {
        'Charlottenburg': '-charlottenburg',
        'Kreuzberg': '-kreuzberg',
        'Mitte': '-mitte',
        'Spandau': '-spandau',
        'Neukölln': '-neukoelln',
        'Tegel': '-tegel',
        'Reineckendorf': '-reineckendorf',
        'Lichtenrade': '-lichtenrade',
        'Lichtenberg': '-lichtenberg'
    }
    
    return locations.get(location, '-charlottenburg')

    
def setUrl(service, location):
    base_url = 'https://www.treatwell.de/orte/behandlung-'
    selected_service = setService(service)
    selected_location = setPreferedLocation(location)

    full_url = f'{base_url}{selected_service}/angebot-typ-lokal/in-berlin{selected_location}-de/?view=list'

    return full_url

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        service = request.form.get('service', 'damenhaarschnitt')
        location = request.form.get('location', '-charlottenburg')

        url = setUrl(service, location)
        response = requests.get(url)

        # BeautifulSoup-Objekt erstellen
        soup = BeautifulSoup(response.content, 'html.parser')

        # Alle Elemente, die mit dem Laden verbunden sind suchen
        shops = soup.find_all(class_='BrowseResult-module--container--a0806d')

        # Liste zum Speichern der Informationen zu jedem Salon
        info_shop = []

        # Über jedes Element iterieren und Informationen extrahieren
        for shop in shops:
            # Laden-URL
            shop_url = shop.find('a')['href']

            # Namen des Salons
            shop_name = shop.find('h2', class_='Text-module_mdHeader__2D1lu').text.strip()
            
            # Bewertung des Salons und Komma entfernen
            rating = shop.find('span', class_='Text-module_bodyHeavy__1LMI1 Rating-module_label__1wOHw').text.strip().replace(',', '.')

            # Standort
            location = shop.find('div', class_='BrowseResultSummary-module--location--70d009').text.strip()
            location = location.replace("Auf Karte anzeigen", "").strip()

            # Nach Elemente mit Ladenbilder suchen
            carousel_div = shop.find('div', class_='BrowseResultSummary-module--imageContainer--5605d3')

            # Wenn es Bilder gibt
            if carousel_div:
                # Erstes Bild suchen
                first_image = carousel_div.find('img')       
                # Wenn es ein Bild gibt
                if first_image:
                # URL in src Etikette suchen
                    if 'src' in first_image.attrs:
                        image_url = first_image['src']
        

            # Preis
            price_wrapper = shop.find('div', class_='PriceView-module--priceWrapper--3cfb53 PriceView-module--stacked--b205c9')
            price_elements = price_wrapper.find_all('span', class_='Text-module_bodyHeavy__1LMI1')
            if len(price_elements) == 2:
                # Wenn es zwei Preisangaben gibt, zeigen wir nur den aktuellen Preis. Manche Läden zeigen den alten und neuen Preis
                #current_price = price_elements[0].text.strip()
                previous_price = price_elements[1].text.strip()
                preis = f"{previous_price}"
            else:
                # Wenn es nur eine Preisangabe gibt
                preis = price_elements[0].text.strip()
            
            # Die Informationen zum Salon in der Liste speichern
            info_shop.append({
                'shop_name': shop_name,
                'rating': rating,
                'location': location,
                'price': preis,
                'picture': image_url,
                'shop_url': shop_url

            })

        # Liste der Salons nach Bewertung absteigen sortieren
        info_shop.sort(key=lambda x: float(x['rating']), reverse=True)
        top_shops = info_shop[:3]
        return render_template('results.html', shops=top_shops)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

# Die ersten drei Salons mit der höchsten Bewertung anzeigen
# for i, shop in enumerate(info_shop[:3], 1):
#     print(f"Shop {i}:")
#     print(f"Name: {shop['shop_name']}")
#     print(f"Bewertung: {shop['rating']}")
#     print(f"Standort: {shop['location']}")
#     print(f"Preis ab: {shop['price']}")
#     print(shop['picture'])
#     print(f"Laden ansehen: {shop['shop_url']}")
#     print()