import random

from django.http import Http404
from django.shortcuts import redirect, render

BASE_PLACES = [
    {
        "name": "Троєщина",
        "district": "Деснянський район",
        "note": "Нішеве місце для незабутньої прогулянки. Атмосферою не насолодишся, зате травму отримаєщ.",
        "rating": 2,
        "is_custom": False,
    },
    {
        "name": "Гора Щекавиця",
        "district": "Поділ",
        "note": 'Один із найяскравіших прикладів українського "ядерного гумору" та національного фаталізму. Прекрасні краєвиди і історична місцина.',
        "rating": 5,
        "is_custom": False,
    },
]


def get_all_places(request):
    custom_places = request.session.get("custom_places", [])
    all_places = []
    for index, place in enumerate(BASE_PLACES + custom_places):
        all_places.append({**place, "id": index})
    return all_places


def pick_random_place(places):
    
    if not places:
        return None
    weights = [place.get("rating", 1) for place in places]
    return random.choices(places, weights=weights, k=1)[0]


def places_list(request):
    if "custom_places" not in request.session:
        request.session["custom_places"] = []

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "clear":
            request.session["custom_places"] = []
            request.session.modified = True
        else:
            name = request.POST.get("place_name", "").strip()
            district = request.POST.get("place_district", "").strip()
            note = request.POST.get("place_note", "").strip()
            try:
                rating = int(request.POST.get("place_rating", ""))
            except ValueError:
                rating = 0

            if name and 1 <= rating <= 5:
                new_place = {
                    "name": name,
                    "district": district if district else None,
                    "note": note,
                    "rating": rating,
                    "is_custom": True,
                }
                custom_places = request.session["custom_places"]
                custom_places.append(new_place)
                request.session["custom_places"] = custom_places
                request.session.modified = True

        return redirect("places_list")

    filter_mode = request.GET.get("filter", "all")
    all_places = get_all_places(request)
    base_count = len(BASE_PLACES)

    if filter_mode == "base":
        places_to_show = all_places[:base_count]
    elif filter_mode == "mine":
        places_to_show = all_places[base_count:]
    else:
        places_to_show = all_places

    picked_place = None
    if request.GET.get("pick"):
        picked_place = pick_random_place(all_places)

    context = {
        "places": places_to_show,
        "custom_places": request.session["custom_places"],
        "filter_mode": filter_mode,
        "picked_place": picked_place,
    }
    return render(request, "places/places_list.html", context)


def place_detail(request, place_id):
    all_places = get_all_places(request)
    if place_id >= len(all_places):
        raise Http404("Такого місця немає")
    return render(request, "places/place_detail.html", {"place": all_places[place_id]})
