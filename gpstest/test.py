import requests
from flask import Flask
app = Flask(__name__)

address = "strandvägen 5"
postalCode = "104 40"

print(f"test {address}")


@app.route('/some-url')
def get_data():
    data = requests.get(
        'https://nominatim.openstreetmap.org/search.php?street=strandv%C3%A4gen+5&postalcode=134+64&format=jsonv2').content
    return data


print(get_data())
