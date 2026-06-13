import os
from datetime import datetime
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def _load(name):
    result = supabase.table("app_data").select("data").eq("name", name).execute()
    if result.data:
        return result.data[0]["data"]
    return []


def _save(name, data):
    print("SAVE CALLED:", name)

    supabase.table("app_data").upsert({
        "name": name,
        "data": data,
        "updated_at": datetime.now().isoformat()
    }, on_conflict="name").execute()


def _load_dict(name):
    result = supabase.table("app_data").select("data").eq("name", name).execute()
    if result.data:
        return result.data[0]["data"]
    return {}


def _save_dict(name, data):
    supabase.table("app_data").upsert({
        "name": name,
        "data": data,
        "updated_at": datetime.now().isoformat()
    }).execute()

# ────────────────────────────────────────────
# СТРУКТУРА КІМНАТ
# ────────────────────────────────────────────
ROOMS_STRUCTURE = {
    1: {  # Czarna Droga 41
        "1": {
            "1A": {"capacity": 2, "gender": "any"},
            "1B": {"capacity": 1, "gender": "any"},
            "1C": {"capacity": 2, "gender": "any"},
            "1D": {"capacity": 2, "gender": "any"},
            "1E": {"capacity": 2, "gender": "any"},
        },
        "2": {
            "2A": {"capacity": 1, "gender": "any"},
            "2B": {"capacity": 2, "gender": "any"},
            "2C": {"capacity": 1, "gender": "any"},
            "2D": {"capacity": 2, "gender": "any"},
            "2E": {"capacity": 2, "gender": "any"},
        },
        "3": {
            "3A": {"capacity": 1, "gender": "any"},
            "3B": {"capacity": 2, "gender": "any"},
            "3C": {"capacity": 2, "gender": "any"},
            "3D": {"capacity": 2, "gender": "any"},
            "3E": {"capacity": 2, "gender": "any"},
            "3F": {"capacity": 2, "gender": "any"},
        },
        "4": {
            "4A": {"capacity": 1, "gender": "any"},
            "4B": {"capacity": 2, "gender": "any"},
            "4C": {"capacity": 2, "gender": "any"},
            "4D": {"capacity": 2, "gender": "any"},
            "4E": {"capacity": 2, "gender": "any"},
            "4F": {"capacity": 2, "gender": "any"},
        },
        "5": {
            "5A": {"capacity": 1, "gender": "any"},
            "5B": {"capacity": 2, "gender": "any"},
            "5C": {"capacity": 2, "gender": "any"},
            "5D": {"capacity": 2, "gender": "any"},
            "5E": {"capacity": 1, "gender": "any"},
            "5F": {"capacity": 2, "gender": "any"},
        },
        "6": {
            "6A": {"capacity": 1, "gender": "any"},
            "6B": {"capacity": 2, "gender": "any"},
            "6C": {"capacity": 2, "gender": "any"},
            "6D": {"capacity": 2, "gender": "any"},
            "6E": {"capacity": 2, "gender": "any"},
            "6F": {"capacity": 2, "gender": "any"},
        },
        "7": {
            "7A": {"capacity": 2, "gender": "any"},
            "7B": {"capacity": 2, "gender": "any"},
            "7C": {"capacity": 2, "gender": "any"},
            "7D": {"capacity": 2, "gender": "any"},
            "7E": {"capacity": 2, "gender": "any"},
        },
        "8": {
            "8A": {"capacity": 1, "gender": "any"},
            "8B": {"capacity": 2, "gender": "any"},
            "8C": {"capacity": 2, "gender": "any"},
            "8D": {"capacity": 2, "gender": "any"},
            "8E": {"capacity": 2, "gender": "any"},
            "8F": {"capacity": 2, "gender": "any"},
        },
    },
    2: {  # Sienkiewicza 17
        "M2": {
            "6M2/A1": {"capacity": 2, "gender": "male"},
            "6M2/A2": {"capacity": 3, "gender": "male"},
            "6M2/A3": {"capacity": 3, "gender": "male"},
        },
        "M3": {
            "6M3/A1": {"capacity": 3, "gender": "female"},
            "6M3/A2": {"capacity": 2, "gender": "female"},
            "6M3/A3": {"capacity": 3, "gender": "female"},
            "6M3/A4": {"capacity": 2, "gender": "female"},
            "6M3/A5": {"capacity": 3, "gender": "female"},
        },
    },
    3: {  # Pomorska 80-86
        "2": {
            "2A": {"capacity": 2, "gender": "any"},
            "2B": {"capacity": 1, "gender": "any"},
            "2C": {"capacity": 1, "gender": "any"},
        },
    },
    4: {  # Zduny 13
        "5": {
            "A": {"capacity": 3, "gender": "any"},
            "B": {"capacity": 3, "gender": "any"},
            "C": {"capacity": 2, "gender": "any"},
            "D": {"capacity": 3, "gender": "any"},
            "E": {"capacity": 2, "gender": "any"},
            "F": {"capacity": 2, "gender": "any"},
            "G": {"capacity": 2, "gender": "any"},
            "H": {"capacity": 2, "gender": "any"},
            "I": {"capacity": 2, "gender": "any"},
            "J": {"capacity": 2, "gender": "any"},
        },
    },
}

def get_rooms_structure():
    return ROOMS_STRUCTURE

# ────────────────────────────────────────────
# ГУРТОЖИТКИ
# ────────────────────────────────────────────
DORMS_DEFAULT = [
    {"id": 1, "name": "ul. Czarna Droga 41", "rooms": 8, "total_places": 82, "free_places": 82, "price_double": 850, "price_triple": 750, "distance": "15 min pieszo do WSG", "description": "Największy akademik. 8 pięter, 82 miejsca.", "photo": "https://placehold.co/400x200/1a3c5e/white?text=Czarna+Droga+41"},
    {"id": 2, "name": "ul. Sienkiewicza 17", "rooms": 2, "total_places": 21, "free_places": 21, "price_double": 850, "price_triple": 750, "distance": "10 min pieszo do WSG", "description": "M2 — tylko chłopcy. M3 — tylko dziewczyny.", "photo": "https://placehold.co/400x200/1a3c5e/white?text=Sienkiewicza+17"},
    {"id": 3, "name": "ul. Pomorska 80-86", "rooms": 1, "total_places": 4, "free_places": 4, "price_double": 850, "price_triple": 750, "distance": "20 min pieszo do WSG", "description": "Małe mieszkanie studenckie.", "photo": "https://placehold.co/400x200/1a3c5e/white?text=Pomorska+80-86"},
    {"id": 4, "name": "ul. Zduny 13", "rooms": 1, "total_places": 23, "free_places": 23, "price_double": 850, "price_triple": 750, "distance": "10 min pieszo do WSG", "description": "Komfortowy akademik, piętro 5.", "photo": "https://placehold.co/400x200/1a3c5e/white?text=Zduny+13"},
    {"id": 5, "name": "ul. Wieśniacza 30", "rooms": 4, "total_places": 14, "free_places": 14, "price_double": 850, "price_triple": 750, "distance": "10 min samochodem do WSG", "description": "Spokojny akademik poza centrum.", "photo": "https://placehold.co/400x200/1a3c5e/white?text=Wieśniacza+30"},
]

def get_dorms():
    d = _load("dorms")
    return d if d else DORMS_DEFAULT

def save_dorms(dorms):
    _save("dorms", dorms)

def update_dorm(dorm_id, fields):
    dorms = get_dorms()
    for d in dorms:
        if d["id"] == dorm_id:
            d.update(fields)
    save_dorms(dorms)

def update_free_places(dorm_id):
    """Автоматично рахує вільні місця"""
    structure = ROOMS_STRUCTURE.get(dorm_id, {})
    residents = get_residents()
    active = [r for r in residents if r.get("dorm_id") == dorm_id and r.get("status") == "active"]
    occupied = len(active)
    total = sum(
        room["capacity"]
        for floor in structure.values()
        for room in floor.values()
    )
    dorms = get_dorms()
    for d in dorms:
        if d["id"] == dorm_id:
            d["free_places"] = max(0, total - occupied)
            d["total_places"] = total
    save_dorms(dorms)

# ────────────────────────────────────────────
# БРОНЮВАННЯ
# ────────────────────────────────────────────
def get_reservations():
    return _load("reservations")

def add_reservation(data):
    items = get_reservations()
    data["id"] = len(items) + 1
    data["status"] = data.get("status", "pending")
    data["created"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    items.append(data)
    _save("reservations", items)
    return data["id"]

def update_reservation_status(res_id, status):
    items = get_reservations()
    for r in items:
        if int(r["id"]) == int(res_id):
            r["status"] = status
    _save("reservations", items)

def delete_reservation(res_id):
    items = get_reservations()
    items = [r for r in items if int(r["id"]) != int(res_id)]
    _save("reservations", items)    

# ────────────────────────────────────────────
# МЕШКАНЦІ
# ────────────────────────────────────────────
def get_residents():
    return _load("residents")

def add_resident(data):
    items = get_residents()
    data["id"] = len(items) + 1
    data["status"] = "active"
    data["created"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    items.append(data)
    _save("residents", items)
    update_free_places(data.get("dorm_id"))
    return data["id"]

def update_resident(res_id, fields):
    items = get_residents()
    dorm_id = None
    for r in items:
        if r["id"] == res_id:
            r.update(fields)
            dorm_id = r.get("dorm_id")
    _save("residents", items)
    if dorm_id:
        update_free_places(dorm_id)

def get_history():
    return _load("history")

def add_history(data):
    items = get_history()
    data["id"] = len(items) + 1
    items.append(data)
    _save("history", items)

# ────────────────────────────────────────────
# ЗАЯВКИ
# ────────────────────────────────────────────
def get_tickets():
    return _load("tickets")

def add_ticket(data):
    items = get_tickets()
    data["id"] = len(items) + 1
    data["status"] = "received"
    data["created"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    data["admin_comment"] = ""
    items.append(data)
    _save("tickets", items)
    return data["id"]

def update_ticket(ticket_id, fields):
    items = get_tickets()
    for t in items:
        if t["id"] == ticket_id:
            t.update(fields)
    _save("tickets", items)

# ────────────────────────────────────────────
# EMAIL DRAFTS
# ────────────────────────────────────────────
def get_email_drafts():
    return _load("email_drafts")

def save_email_draft(data):
    items = get_email_drafts()
    data["id"] = len(items) + 1
    data["created"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    items.append(data)
    _save("email_drafts", items)
    return data["id"]