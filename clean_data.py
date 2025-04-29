import json

MOVIE_GENRES = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
    99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
    27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance",
    878: "Science Fiction", 10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
}

TV_GENRES = {
    10759: "Action, Adventure", 16: "Animation", 35: "Comedy", 80: "Crime", 99: "Documentary",
    18: "Drama", 10751: "Family", 10762: "Kids", 9648: "Mystery", 10763: "News",
    10764: "Reality", 10765: "Sci-Fi, Fantasy", 10766: "Soap", 10767: "Talk",
    10768: "War, Politics", 37: "Western", 10749: "Romance", 36: "History", 22: "Musical"
}

LANG_MAP = {
    "en": "English", "ja": "Japanese", "es": "Spanish", "fr": "French", "ko": "Korean",
    "zh": "Chinese", "de": "German", "it": "Italian", "pt": "Portuguese", "hi": "Hindi",
    "ru": "Russian", "tr": "Turkish", "cn": "Cantonese", "he": "Hebrew"
}

def generate_data_point(media_type, media):
    overview = media.get("overview", "").strip()
    if not overview or len(overview) < 10:
        return None

    is_movie = media_type == "movie"
    title = media.get("title") if is_movie else media.get("name")
    date = media.get("release_date") if is_movie else media.get("first_air_date")
    year = date[:4] if date else "Unknown"

    lang = LANG_MAP.get(media.get("original_language"), "Unknown")
    genre_map = MOVIE_GENRES if is_movie else TV_GENRES
    genres = [genre_map.get(gid, f"Genre({gid})") for gid in media.get("genre_ids", [])]
    genres_flat = [g.strip() for genre in genres for g in genre.split(",")]

    rating_val = round(media.get("vote_average", 0), 1)
    vote_count_val = media.get("vote_count", 0)

    is_anime = (lang.lower() == "japanese" and "Animation" in genres_flat)
    type_noun = "movie" if is_movie else "tv"

    cast_list = media.get("Cast", [])
    if cast_list:
        cast_list = cast_list[:5]
        cast_str = ", ".join(cast_list)
    else:
        cast_str = None

    director = media.get("Director")
    composer = media.get("Composer")
    director = director if director and director != "Unknown" else None
    composer = composer if composer and composer != "Unknown" else None

    summary_parts = [f"{title} ({year}) is a {lang.lower()}-language {', '.join(genres_flat).lower()} {type_noun}."]
    if cast_str:
        summary_parts.append(f"It stars {cast_str}.")
    if director:
        summary_parts.append(f"Directed by {director}.")
    if composer:
        summary_parts.append(f"Music composed by {composer}.")
    summary_parts.append(f"This {type_noun} centers around: {overview}")

    embedding_text = " ".join(summary_parts)

    metadata = {
        "title": title,
        "type": type_noun,
        "language": lang,
        "genres": genres_flat,
        "rating": rating_val,
        "vote_count": vote_count_val,
        "anime": is_anime,
        "year": int(year) if year.isdigit() else None,
        "summary": overview,
    }
    if cast_list:
        metadata["cast"] = cast_list
    if director:
        metadata["director"] = director
    if composer:
        metadata["composer"] = composer

    return {
        "id": str(media["id"]),
        "metadata": metadata,
        "text": embedding_text,
        "values": []
    }


def convert_file(media_type, name):
    with open(name, "r", encoding="utf-8") as f:
        media_list = json.load(f)

    results = []
    for media in media_list:
        s = generate_data_point(media_type, media)
        if s:
            results.append(s)

    return results

def save_file(media_type, raw_name, new_name):
    converted_data = convert_file(media_type, raw_name)
    with open(new_name, "w", encoding="utf-8") as f:
        json.dump(converted_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    save_file("movie", "data/movies.json", "data/movies_cleaned.json")
    save_file("tv", "data/tv.json", "data/tv_cleaned.json")