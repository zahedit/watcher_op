import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Game, Movie, TVShow, UserContent
from .models import TVShow, UserContent
from django.contrib.auth.decorators import login_required


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
    return render(request, "content/search_results.html", {"results": results})
#############################################
def search_form(request):
    tvshows = TVShow.objects.order_by("-start_date")[:10]
    movies = Movie.objects.order_by("-release_date")[:10]
    games = Game.objects.order_by("-release_date")[:10]
    # return render(request, "content/search_form.html", {"tvshows": tvshows_with_follow})
    return render(request, "content/content.html", {})
#############################################
@login_required
def add_content(request):
    tv_id = request.GET.get('id')
    url = f"{base_url_movie}/tv/{tv_id}?api_key={api_key_movie}"
    response = requests.get(url)
    result = response.json()

    # Check if the TV show already exists in the database
    tvShow = TVShow.objects.filter(title=result["name"]).first()
    category = 'tvshow'
    if not tvShow:
        # create a new movie object and save it to the database
        tvShow = TVShow(
            id = result["id"],
            title = result["name"],
            genre=", ".join([g["name"] for g in result["genres"]]),
            start_date = result["first_air_date"],
            end_date = result["last_air_date"],
            seasons = result["number_of_seasons"],
            rating = result["vote_average"],
            cover = result["poster_path"],
            description = result["overview"],
        )
        tvShow.save()
    tvshow_user_searched = TVShow.objects.get(title=result["name"])
    qs = UserContent.objects.filter(user=request.user, category=category, content_id=tv_id)
    if qs.exists():
        qs.delete()
    else:
        UserContent.objects.get_or_create (
            user=request.user,
            category='tvshow',  # Adjust the category based on your logic for movies, shows, and games
            content_id= tvshow_user_searched.id
        )
    return render(request, "content/confirmation.html", {"tv": tvShow})

from django.shortcuts import render, get_object_or_404
from .models import UserContent, TVShow, Movie, Game

@login_required
def dashboard(request):
    # Retrieve the latest 10 content items added by the user from all categories
    latest_content = UserContent.objects.filter(user=request.user).order_by('-id')[:10]

    content_with_details = []

    for content in latest_content:
        if content.category == 'tvshow':
            content_details = get_object_or_404(TVShow, id=content.content_id)
        elif content.category == 'movie':
            content_details = get_object_or_404(Movie, id=content.content_id)
        elif content.category == 'game':
            content_details = get_object_or_404(Game, id=content.content_id)

        content_with_details.append({
            'category': content.category,
            'content_id': content.content_id,
            'name': content_details.title,
            'cover': content_details.cover,
            'rating': content.rating,
            'review': content.review,
        })

    return render(request, "content/dashboard.html", {"content_with_details": content_with_details})
