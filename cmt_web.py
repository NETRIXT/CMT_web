from flask import Flask, render_template, request, send_file
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO

app = Flask(__name__)

def requires_authentication(response):
    # Check if the response indicates that authentication is required
    return response.status_code == 401 and 'WWW-Authenticate' in response.headers

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    username = request.form.get('username')  # Get the username from the form
    password = request.form.get('password')  # Get the password from the form

    # Send an initial request to check if authentication is required
    initial_response = requests.get(url, auth=HTTPBasicAuth(username, password))  # Use the username and password for authentication


    # Check if authentication is required
    requires_auth = requires_authentication(initial_response)
    print(f"Requires Auth: {requires_auth}")


    if requires_auth:
        # Provide a print statement to indicate that authentication is required
        print("Authentication is required.")
        # If authentication fails, render an error message
        if initial_response.status_code == 401:
            error = "If authentication fails, please check your username and password."
            return render_template('auth_form.html', requires_auth=requires_auth, url=url, error=error)


    # If no authentication is required, proceed with scraping
    soup = BeautifulSoup(initial_response.text, 'html.parser')
    header_tags = ['header', 'nav', 'aside', 'footer']

    for tag_name in header_tags:
        for header in soup.find_all(tag_name):
            header.extract()

    visible_text = list(soup.stripped_strings)
    df = pd.DataFrame({'Content': visible_text})

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    output.seek(0)

    # Provide print statements to indicate the success of the scraping
    print("Scraping successful. Creating Excel file.")

    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='visible_data.xlsx')

if __name__ == '__main__':
    app.run(debug=True)
