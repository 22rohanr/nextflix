import json
import os
import requests
from dotenv import load_dotenv


load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = os.getenv("BASE_URL")

def fetch_tmdb_results(media_type, filters):
    results = []

    url = f"{BASE_URL}/discover/{media_type}?api_key={TMDB_API_KEY}&{filters}page={1}"
    response = requests.get(url).json()
    results.extend(response.get("results"))
    pages = response.get("total_pages")

    for i in range(2, pages + 1):
        url = f"{BASE_URL}/discover/{media_type}?api_key={TMDB_API_KEY}&{filters}page={i}"
        response = requests.get(url).json()
        results.extend(response.get("results"))

    return results

def remove_duplicates(list1, list2):
    ids1 = {media.get("id") for media in list1}
    clean_list2 = [media for media in list2 if media.get("id") not in ids1]
    return list1 + clean_list2

def add_roles(media_type, data):
    for media in data:
        media_id = media.get("id")
    
        url = f"{BASE_URL}/{media_type}/{media_id}/credits?api_key={TMDB_API_KEY}"
        response = requests.get(url)
        credits = response.json()
        cast = credits.get("cast", [])
        crew = credits.get("crew", [])

        media["Cast"] = [person["name"] for person in cast 
                         if person.get("known_for_department") == "Acting"
                         and person.get("popularity", 0) > 2.0]

        media["Director"] = next((person["name"] for person in crew 
                                    if person.get("job", "").lower() == "director"), "Unknown")
    
        media["Composer"] = next((person["name"] for person in crew 
                                if person.get("job", "").lower() == "original music composer"), "Unknown")
        
    return data

def save_file(data, name):
    with open(name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    all_movies = fetch_tmdb_results("movie", "vote_average.gte=6.0&vote_count.gte=500&")
    jp_movies = fetch_tmdb_results("movie", "vote_average.gte=6.0&vote_count.gte=100&with_original_language=ja&")
    movies = remove_duplicates(all_movies, jp_movies)
    add_roles("movie", movies)
    save_file(movies, "backend/data/raw/movies.json")

    all_tv = fetch_tmdb_results("tv", "vote_average.gte=6.0&vote_count.gte=75&")
    jp_tv = fetch_tmdb_results("tv", "vote_average.gte=6.0&vote_count.gte=50&with_original_language=ja&")
    tv = remove_duplicates(all_tv, jp_tv)
    add_roles("tv", tv)
    save_file(tv, "backend/data/raw/tv.json")