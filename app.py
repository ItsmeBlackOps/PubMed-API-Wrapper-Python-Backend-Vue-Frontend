from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import xmltodict

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['POST'])
def search_publications():
    # PubMed API for searching publications
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    data = request.json
    print(data)
    query = data.get('query')
    pagination = data.get('pagination', {'start': 0, 'limit': 10})
    
    params = {
        'db': 'pubmed',
        'term': query,
        'retstart': pagination['start'],
        'retmax': pagination['limit'],
        'retmode': 'json'
    }
    response = requests.get(base_url, params=params)
    a = response.json()
    print(a['esearchresult']['idlist'])
    return jsonify(a['esearchresult']['idlist'])

@app.route('/details', methods=['GET'])
def get_details():
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    ids = request.args.getlist('ids')
    print(','.join(ids))
    params = {
        'db': 'pubmed',
        'id': ids,  # Ensure IDs are passed as a comma-separated string
        'retmode': 'xml',
        'rettype': 'abstract'
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = xmltodict.parse(response.content)
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Return a 500 internal server error on failure

    articles = data.get("PubmedArticleSet", {}).get("PubmedArticle", [])
    if not isinstance(articles, list):
        articles = [articles]  # Ensure articles is always a list
    
    extracted_info = []

    for article in articles:
        medline_citation = article.get("MedlineCitation", {})
        article_data = medline_citation.get("Article", {})

        pmid = medline_citation.get("PMID", {}).get("#text", "Data not available")
        title = article_data.get("ArticleTitle", "Data not available")
        abstract = article_data.get("Abstract", {}).get("AbstractText", "Data not available")
        abstract_text = " ".join([ab.get("#text", "") for ab in abstract]) if isinstance(abstract, list) else abstract

        authors = article_data.get("AuthorList", {}).get("Author", [])
        author_list = [f"{author.get('ForeName', '')} {author.get('LastName', '')}" for author in authors if author.get('ForeName')]
        author_list_text = ", ".join(author_list)

        journal = article_data.get("Journal", {}).get("Title", "Data not available")
        pub_year = article_data.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {}).get("Year", "Data not available")

        mesh_terms = medline_citation.get("MeshHeadingList", {}).get("MeshHeading", [])
        mesh_term_list = [mesh.get("DescriptorName", {}).get("#text", "") for mesh in mesh_terms]
        mesh_terms_text = ", ".join(mesh_term_list)

        extracted_info.append({
            "PMID": pmid,
            "Title": title,
            "Abstract": abstract_text,
            "Author List": author_list_text,
            "Journal": journal,
            "Publication Year": pub_year,
            "MeSH Terms": mesh_terms_text
        })

    print(extracted_info)
    return jsonify(extracted_info)  # Use jsonify to wrap the response

if __name__ == '__main__':
    app.run(debug=True)
