import csv
import os
import string
import random
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Define the CSV file to store the URLs
CSV_FILE = 'urls.csv'

# Function to generate a random short URL key
def generate_short_id(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Function to load URLs from the CSV file
def load_urls():
    if not os.path.exists(CSV_FILE):
        return {}
    with open(CSV_FILE, mode='r') as file:
        reader = csv.reader(file)
        return {rows[0]: (rows[1], rows[2]) for rows in reader}

# Function to save a new URL mapping to the CSV file, including user IP
def save_url(short_id, original_url, user_ip):
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([short_id, original_url, user_ip])

# Function to get client IP address
def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        return request.remote_addr

# Custom URL Shortener Route
@app.route('/shorten', methods=['GET', 'POST'])
def shorten():
    if request.method == 'POST':
        data = request.get_json()
        original_url = data.get('url')
        
        # Validate URL input
        if not original_url:
            return jsonify({'success': False, 'message': 'The URL field is required!'}), 400

        # Generate a unique short URL ID
        urls = load_urls()
        short_id = generate_short_id()
        while short_id in urls:
            short_id = generate_short_id()
        
        # Get client IP address
        user_ip = get_client_ip()

        # Save the mapping in CSV with the client IP address
        save_url(short_id, original_url, user_ip)
        
        short_url = request.host_url + short_id
        return jsonify({'success': True, 'short_url': short_url}), 200

    return render_template('index.html')

# Route for redirecting shortened URLs
@app.route('/<short_id>')
def redirect_to_url(short_id):
    urls = load_urls()
    original_url = urls.get(short_id)
    print(urls)
    print(original_url)
    if original_url:
        return redirect(original_url[0])
    else:
        return jsonify({'success': False, 'message': 'URL not found!'}), 404

if __name__ == '__main__':
    app.run(debug=True)
