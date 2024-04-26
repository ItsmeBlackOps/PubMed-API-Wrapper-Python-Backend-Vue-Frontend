from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Third-party API endpoint URLs
ID_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed"
DETAILS_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed"

@app.route('/search', methods=['POST'])
def search_publications():
    """
    Search publications based on a given query.

    Request Body:
    {
        "query": "Your search query",
        "retstart": Optional. Pagination start index. Default is 0.
        "retmax": Optional. Maximum number of results per page. Default is 10.
    }

    Returns:
    {
        "ids": ["id1", "id2", ...]
    }
    """
    try:
        query = request.json.get('query')
        retstart = request.json.get('retstart', 0)
        retmax = request.json.get('retmax', 10)

        params = {
            'term': query,
            'retstart': retstart,
            'retmax': retmax,
            'retmode': 'json'
        }

        response = requests.get(ID_ENDPOINT, params=params)
        data = response.json()
        ids = data['esearchresult']['idlist']

        return jsonify({'ids': ids}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/details', methods=['GET'])
def get_publication_details():
    """
    Get details of publications based on provided IDs.

    Request Args:
    ids: Comma-separated list of publication IDs.
    fields: Optional. Comma-separated list of fields to return.

    Returns:
    {
        "publications": [
            {"PMID": "", "Title": "", "Abstract": "", "AuthorList": "", "Journal": "", "PublicationYear": "", "MeSHTerms": []},
            ...
        ]
    }
    """
    try:
        ids = request.args.get('ids').split(',')
        fields = request.args.get('fields', '').split(',')

        params = {
            'id': ','.join(ids),
            'retmode': 'xml'
        }

        response = requests.get(DETAILS_ENDPOINT, params=params)
        # Process XML response and extract required fields
        # Your implementation to parse XML and extract required fields

        # Example response
        publications = [
            {'PMID': '123456', 'Title': 'Sample Title', 'Abstract': 'Sample Abstract', 'AuthorList': 'Sample Authors', 'Journal': 'Sample Journal', 'PublicationYear': '2023', 'MeSHTerms': ['Term1', 'Term2']},
            {'PMID': '789012', 'Title': 'Another Title', 'Abstract': 'Another Abstract', 'AuthorList': 'Another Authors', 'Journal': 'Another Journal', 'PublicationYear': '2022', 'MeSHTerms': ['Term3', 'Term4']}
        ]

        return jsonify({'publications': publications}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
