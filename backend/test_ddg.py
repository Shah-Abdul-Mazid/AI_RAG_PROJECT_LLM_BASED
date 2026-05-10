from ddgs import DDGS
import json

def test_search():
    query = "Who is the Supreme Leader of the Islamic Republic of Iran ?"
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=3))
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    test_search()
