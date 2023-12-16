import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Game, Movie, TVShow, UserContent
from .models import TVShow, UserContent
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest


api_key_movie = "db9e6b5bb2e44f19d109c9ae67a1bce7"
base_url_movie = "https://api.themoviedb.org/3"

def search_movies(request):
    query = request.GET.get("name", "")

    if not query:
        return HttpResponse("")
    params = {
        "api_key": api_key_movie,
        "query": query,
        "page": 1,
        "page_size": 1,
    }
    response = requests.get(base_url_movie + "/search/movie", params=params)

    if response.status_code == 200:
        data = response.json()
        results = data["results"]
        # Check if the user is following each content (movie, show, or game)
        for result in results:
            content_id = result['id']
            category = 'movie'  # Adjust the category based on your logic for movies, shows, and games
            result['is_following'] = UserContent.objects.filter(
                user=request.user, category=category, content_id=content_id
            ).exists()

        return render(request, "content/search_results_movie.html", {"results": results})
    else:
        return HttpResponse("Error: " + str(response.status_code))
#############################################
@login_required
def search_tv(request):
    query = request.GET.get("name", "")

    if not query:
        return HttpResponse("")
    params = {
        "api_key": api_key_movie,
        "query": query,
        "page": 1,
        "page_size": 1,
    }
    response = requests.get(base_url_movie + "/search/tv", params=params)

    if response.status_code == 200:
        data = response.json()
        results = data["results"]
        for result in results:
            content_id = result['id']
            category = 'tvshow'  # Adjust the category based on your logic for movies, shows, and games
            result['is_following'] = UserContent.objects.filter(
                user=request.user, category=category, content_id=content_id
            ).exists()

        return render(request, "content/result_tvshow.html", {"results": results})
    else:
        return HttpResponse("Error: " + str(response.status_code))
#############################################
api_key_game = "ea0afd24e6f34b8f84a0802b8585d42d"
base_url_game = "https://api.rawg.io/api/games"

def search_games(request):
    query = request.GET.get("name", "")

    if not query:
        return HttpResponse("")

    url = f"{base_url_game}?search={query}&key={api_key_game}&page_size=3"
    response = requests.get(url)
    data = response.json()
    results = data.get("results", [])
    for result in results:
        content_id = result['id']
        category = 'game'  # Adjust the category based on your logic for movies, shows, and games
        result['is_following'] = UserContent.objects.filter(
            user=request.user, category=category, content_id=content_id
        ).exists()
    return render(request, "content/search_results_game.html", {"results": results})
#############################################
def search_form(request):
    tvshows = TVShow.objects.order_by("-release_date")[:10]
    movies = Movie.objects.order_by("-release_date")[:10]
    games = Game.objects.order_by("-release_date")[:10]
    # return render(request, "content/search_form.html", {"tvshows": tvshows_with_follow})
    return render(request, "content/content.html", {})
#############################################
@login_required
def add_content(request):
    category = request.GET.get('category')
    content_id = request.GET.get('id')

    if category == 'game':
        url = f"{base_url_game}/{content_id}?key={api_key_game}" 
        response = requests.get(url)
        result = response.json()

        game = Game.objects.filter(title=result["name"]).first()
        if not game:
            game = Game(
                id = result["id"],
                title=result["name"],
                genre=", ".join([g["name"] for g in result["genres"]]),
                platform=", ".join([p["platform"]["name"] for p in result["platforms"]]),
                release_date=result["released"],
                age_rating=result["esrb_rating"]["name"] if result["esrb_rating"] else "Unknown",
                cover=result["background_image"],
            )
            game.save()

        user_content = UserContent.objects.filter(user=request.user, category=category, content_id=content_id)
        if user_content.exists():
            user_content.delete()
        else:
            UserContent.objects.get_or_create(
                user=request.user,
                category=category,
                content_id=game.id
            )
        return render(request, "content/confirmation.html", {"content": game})

    elif category == 'movie':
        # Logic for movie category
        url = f"{base_url_movie}/movie/{content_id}?api_key={api_key_movie}"
        url_credits = f"{base_url_movie}/movie/{content_id}/credits?api_key={api_key_movie}"
        response = requests.get(url)
        result = response.json()

        response_credits = requests.get(url_credits) 
        result_credits = response_credits.json()

        movie = Movie.objects.filter(title=result["title"]).first()
        if not movie:
            movie = Movie(
                id = result["id"],
                title=result["title"],
                genre=", ".join([g["name"] for g in result["genres"]]),
                director=", ".join([d["name"] for d in result_credits["crew"] if d["job"] == "Director"]),
                release_date=result["release_date"],
                rating=result["vote_average"],
                cover=result["poster_path"],
                description=result["overview"],
            )
            movie.save()

        user_content = UserContent.objects.filter(user=request.user, category=category, content_id=content_id)
        if user_content.exists():
            user_content.delete()
        else:
            UserContent.objects.get_or_create(
                user=request.user,
                category=category,
                content_id=movie.id
            )
        return render(request, "content/confirmation.html", {"content": movie})

    elif category == 'tvshow':
        # Logic for TV show category
        url = f"{base_url_movie}/tv/{content_id}?api_key={api_key_movie}"
        response = requests.get(url)
        result = response.json()

        tvshow = TVShow.objects.filter(title=result["name"]).first()
        if not tvshow:
            tvshow = TVShow(
                id = result["id"],
                title=result["name"],
                genre=", ".join([g["name"] for g in result["genres"]]),
                release_date=result["first_air_date"],
                end_date=result["last_air_date"],
                seasons=result["number_of_seasons"],
                rating=result["vote_average"],
                cover=result["poster_path"],
                description=result["overview"],
            )
            tvshow.save()

        user_content = UserContent.objects.filter(user=request.user, category=category, content_id=content_id)
        if user_content.exists():
            user_content.delete()
        else:
            UserContent.objects.get_or_create(
                user=request.user,
                category=category,
                content_id=tvshow.id
            )
        return render(request, "content/confirmation.html", {"content": tvshow})

    else:
        # Handle invalid category
        return HttpResponseBadRequest("Invalid category")