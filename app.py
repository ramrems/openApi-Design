from flask import Flask, jsonify, request
from flasgger import Swagger, swag_from
import pandas as pd
import requests
from io import BytesIO

swagger_config = {
    'headers': [],
    'specs': [
        {
            'endpoint': 'apispec_1',
            'route': '/swagger.yml',
            'rule_filter': lambda rule: True,
            'model_filter': lambda tag: True,
        }
    ],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route': '/apidocs/'  # Sample url
}

app = Flask(__name__)
app.config['SWAGGER'] = swagger_config
swagger = Swagger(app, config=swagger_config)

# URL of the Excel file
excel_file_url = "https://github.com/ramrems/openApi-Design/raw/main/books.xlsx"

def load_data():
    try:
        # Read the Excel file directly from the URL
        excel_data = BytesIO(requests.get(excel_file_url).content)
        df = pd.read_excel(excel_data, engine='openpyxl')
        return df.to_dict('records')
    except Exception as e:
        print("An error occurred while reading the Excel file:", str(e))
        return []
@app.route('/')
def index():
    return jsonify({"message": "Welcome to the bookstore API!"})
    
# List all books
@app.route('/books', methods=['GET'])
@swag_from('swagger.yml')
def get_books():
    books = load_data()
    return jsonify(books)

# Add a new book
@app.route('/books', methods=['POST'])
@swag_from('swagger.yml')
def add_book():
    new_book = request.json
    books = load_data()
    new_book['id'] = len(books) + 1  # Assign a unique ID to the new book
    books.append(new_book)
    try:
        df = pd.DataFrame(books)
        df.to_excel(excel_file_url, index=False)  # Write the data to the Excel file
    except Exception as e:
        print("An error occurred while writing to the Excel file:", str(e))
    return jsonify(new_book), 201

# Retrieve a specific book
@app.route('/books/<int:id>', methods=['GET'])
@swag_from('swagger.yml')
def get_book(id):
    books = load_data()
    book = next((book for book in books if book['id'] == id), None)
    if book:
        return jsonify(book)
    return jsonify({'message': 'Book not found'}), 404

# Update a book
@app.route('/books/<int:id>', methods=['PUT'])
@swag_from('swagger.yml')
def update_book(id):
    updated_book = request.json
    books = load_data()
    # Find and update the updated book
    for i, book in enumerate(books):
        if book['id'] == id:
            books[i] = updated_book
            break
    else:
        return jsonify({'message': 'Book not found'}), 404

    # Re-create the DataFrame with the updated book list
    df = pd.DataFrame(books)
    
    # Write the DataFrame to the Excel file
    try:
        df.to_excel(excel_file_url, index=False)
    except Exception as e:
        print("An error occurred while writing to the Excel file:", str(e))

    return jsonify(updated_book)

# Delete a book
@app.route('/books/<int:id>', methods=['DELETE'])
@swag_from('swagger.yml')
def delete_book(id):
    # Load the data
    books = load_data()

    # Find and delete the book
    filtered_books = [book for book in books if book['id'] != id]

    # Write the filtered books to the Excel file
    df = pd.DataFrame(filtered_books)
    try:
        df.to_excel(excel_file_url, index=False)
    except Exception as e:
        print("An error occurred while writing to the Excel file:", str(e))

    return jsonify({'message': 'Book deleted'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
