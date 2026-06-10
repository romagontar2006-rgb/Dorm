from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from groq import Groq
from typing import Optional
import database as db
import os, shutil, uuid

app = FastAPI()
client = Groq(api_key="GROQ_API_KEY")

ADMIN_PASSWORD = "1111"
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

DORM_INFO = """
Jesteś cyfrowym administratorem akademików WSG w Bydgoszczy.
Akademiki:
1. ul. Czarna Droga 41 — 81 miejsc, 15 min pieszo do WSG
2. ul. Sienkiewicza 17 — 21 miejsc, 10 min pieszo do WSG
3. ul. Pomorska 80-86 — 4 miejsca, 20 min pieszo do WSG
4. ul. Zduny 13 — 23 miejsca, 10 min pieszo do WSG
5. ul. Wieśniacza 30 — 14 miejsc, 10 min samochodem do WSG
Ceny: pokój 1-osobowy 1150 PLN, pokój 2-osobowy 850 PLN, 3-osobowy 750 PLN. Kaucja: 850 PLN.
Rezerwacja: wysłać email na dormitory@byd.pl minimum 2 tygodnie przed przyjazdem.
Zakwaterowanie: Bydgoszcz, ulica Garbary 2, Budynek H, pok. 008, pon-pt 08:00-15:00.
Studenci WSG: najpierw Budynek C pok. 007, potem H 008.
в будинок С 007 йдуть тілький ті студенти які планують навчатися в WSG щоб підписати там договір з університетом і підтвердити що вони є студентами WSG. Студенти які не навчаються в WSG можуть одразу йти в будинок H 008 щоб підписати договір проживання.
Formułuj wszystko tak: na ulicy iw oficjalnych tekstach pisz wyłącznie po polsku (dosłownie). Możesz odpowiadać po ukraińsku, ale w publicznych/ oficjalnych sytuacjach tylko po polsku.
Email: dormitory@byd.pl
Заселення студентів WSG

Якщо студент навчається в WSG, процес виглядає так:
1. Студент спочатку повинен прийти до будівлі C, кімната 007.
2. Там студент підписує договір з університетом WSG, який підтверджує, що він навчається в цьому університеті.
3. Після цього студент може звернутися до адміністрації  будівля H кімната 008 працюємо з понеділка по п’ятницю з 8:00 до 15:00.
4. В адміністрації студент підписує договір проживання (umowa).
5. Після підписання договору студент отримує ключі від кімнати.
6. Адміністрація також надає інформацію:
• адреса гуртожитку
• як туди дістатися
• основні правила проживання

Після цього студент може заселятися.


🎓 Заселення студентів з інших університетів

Якщо студент не навчається у WSG, він також може проживати в гуртожитку, але процедура трохи інша.

Для заселення необхідно надати:
• паспорт
• PESEL

Після цього студент підписує договір проживання з адміністрацією та отримує ключі від кімнати.


💰 Депозит (Kaucja)

Перед заселенням студент повинен внести депозит.

Розмір депозиту:
850 PLN

Депозит використовується як гарантія дотримання правил проживання та покриття можливих пошкоджень майна.




REGULAMIN ZESPOŁU POKOI AKADEMICKICH WSG
Regulamin Zespołu Pokoi Akademickich WSG, zwanych dalej ZPA, określa ogólne zasady jego funkcjonowania, prawa i obowiązki mieszkańców.

1.  Do zamieszkania w pokoju akademickim uprawniona jest osoba, która zawarła umowę, dopełniła niezbędnych formalności związanych z zakwaterowaniem oraz wniosła należne opłaty.
2.  Przyjęcie i zwrot pokoju oraz jego wyposażenia  nastepuje protokolarnie.
3.  Za otrzymany  sprzęt i  wyposażenie pokoju mieszkaniec odpowiada materialnie.
4.  Za wszystkie uszkodzenia i braki w wyposażeniu pokoju jego mieszkańcy odpowiadają indywidualnie, a w przypadkach nieustalenia sprawcy -- łącznie, w równych częściach,
5.  Mieszkańcy zobowiązani są:

a.  do przestrzegania zapisów umowy najmu miejsca w pokojach akademickich WSG
b.  do przestrzegania przepisów BHP, przepisów przeciwpożarowych i ochrony mienia,
c.  do dokonywania opłat związanych z zamieszkaniem w ZPA do dnia 10 każdego miesiąca za miesiąc bieżący. Za zwłokę naliczane są  odsetki ustawowe.
d.  do przestrzegania Regulaminu ZPA oraz do podporządkowania się decyzjom Administracji WSG ,
e.  do przestrzegania ciszy nocnej w godz. od 22.00 do 6.00,
f.  do dbania o mienie ZPA, utrzymywania porządku i czystości w pokojach mieszkalnych i pomieszczeniach ogólnego użytku oraz do zgłaszania wszelkich zauważonych usterek technicznych do Administracji WSG, email:dormitory@byd.pl,
g.  do niezwłocznego powiadamiania Administracji WSG email;dormitory@byd.pl o wypadku lub chorobie zakaźnej współmieszkańca, zaistniałych na terenie ZPA,
h.  segregacji odpadów i śmieci wg instrukcji i wyrzucania ich do właściwych pojemników i ich wynoszenia do pojemników zbiorczych
i.  wyłączania światła i odbiorników elektrycznych, gdy nie są używane
j.  zakręcania zaworów grzejników ciepła/kaloryferów/,gdy okna są otwarte

6.  Mieszkańcom Zespołu Pokoi Akademickich WSG  zabrania się:


a.  używania w pokojach mieszkalnych kuchenek elektrycznych, gazowych i grzejników elektrycznych oraz innych źródeł ciepła nie stanowiących stałego wyposażenia pokoju,
b.  samowolnego zakładania, przerabiania, naprawiania i utrudniania korzystania innym użytkownikom z instalacji elektrycznych, gazowych, wodnych, telefonicznych, antenowych, komputerowych, itp.
c.  wymiany zamków ,wkładek patentowych w drzwiach pokojów i segmentów bez uzgodnienia z Administracją WSG, email:dormitory@byd.pl
d.  używania niezgodnie z przeznaczeniem pomieszczeń, wyposażenia  i sprzętu przeciwpożarowego,
e.  niszczenia  ścian i wyposażenia pokoi i części wspólnych 
f.  wrzucania do urządzeń sanitarnych przedmiotów, które mogłyby spowodować ich uszkodzenie lub wadliwe działanie,
g.  wyrzucania przez okna jakichkolwiek przedmiotów,
h.  trzymania w pokojach zwierząt,
i.  wnoszenie i posiadania broni palnej i pneumatycznej,
j.  palenia tytoniu na terenie ZPA z wyjątkiem miejsc do tego przeznaczonych i przystosowanych,
k.  wytwarzania, sprzedawania, podawania i spożywania napojów alkoholowych i narkotyków na terenie ZPA,
l.  udostępniania przyznanych miejsc osobom nieuprawnionym,
m.  prowadzenia na terenie ZPA działalności gospodarczej 
n.  składowania w pokojach mieszkalnych i pomieszczeniach ogólnodostępnych DS towarów i dóbr, których przeznaczenie i ilość mogą wskazywać na zamiary handlowe.
3.  Każde naruszenie Regulaminu ZPA dokonane pod wpływem alkoholu lub narkotyków karane jest ze szczególną surowością włącznie z pozbawieniem prawa do zamieszkania w ZPA w trybie natychmiastowym.
4.  Mieszkaniec odpowiada materialnie za szkody wyrządzone przez jego gości.
5.  Goście mieszkańców ZPA mają prawo wstępu na teren ZPA w godz. odwiedzin tzn. od 8.00 do 22.00.

-W przypadku zmiany miejsca zakwaterowania na prośbę Studenta po  wydaniu zgody przez Administrację, Student zobowiązany jest uiścić opłatę w wysokości 100 zł doliczonej do czynszu za pierwszy miesiąc w nowym miejscu zakwaterowania

"""

EMAIL_SYSTEM = """
Jesteś asystentem administratora akademików WSG w Bydgoszczy.
Twoje zadanie: analizować emaile od studentów i pisać profesjonalne odpowiedzi po polsku.
Informacje o akademikach:
- 5 akademików w Bydgoszczy
- Ceny: pokój 2-os. 850 PLN, 3-os. 750 PLN, kaucja 850 PLN
- Biuro: Budynek H 008, pon-pt 08:00-15:00
- Email: dormitory@byd.pl
- Rezerwacja: min. 2 tygodnie przed przyjazdem
Pisz emaile formalnie, uprzejmie, konkretnie. Podpisuj: "Z poważaniem, Administracja Akademików WSG"
"""

SYSTEM_PROMPTS = {
    "uk": f"Відповідай тільки українською. {DORM_INFO}",
    "en": f"Reply only in English. {DORM_INFO}",
    "pl": f"Odpowiadaj tylko po polsku. {DORM_INFO}",
}

def check_admin(password: str):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Błąd autoryzacji")

# ── МОДЕЛІ ──
class ChatMsg(BaseModel):
    text: str
    language: str = "pl"

class ReservationIn(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    is_wsg: bool
    gender: str
    dorm_id: int
    checkin: str
    checkout: str

class TicketIn(BaseModel):
    dorm_id: int
    room: Optional[str] = ""
    description: str
    photo_url: Optional[str] = ""

class ResidentIn(BaseModel):
    full_name: str
    dorm_id: int
    floor: str
    room: str
    checkin: str
    checkout: Optional[str] = ""
    gender: Optional[str] = "any"
    email: Optional[str] = ""
    phone: Optional[str] = ""
    telegram: Optional[str] = ""
    contract_date: Optional[str] = ""
    contract_end: Optional[str] = ""
    contract_num: Optional[str] = ""
    notes: Optional[str] = ""
    photo_url: Optional[str] = ""

class EmailAnalyze(BaseModel):
    email_text: str
    sender: Optional[str] = ""

# ── CHAT ──
@app.post("/api/chat")
async def chat(msg: ChatMsg):
    system = SYSTEM_PROMPTS.get(msg.language, SYSTEM_PROMPTS["pl"])
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": msg.text}]
    )
    return {"reply": r.choices[0].message.content}

# ── EMAIL AI ──
@app.post("/api/email-analyze")
async def email_analyze(data: EmailAnalyze, password: str = ""):
    check_admin(password)
    prompt = f"Email od studenta{' ('+data.sender+')' if data.sender else ''}:\n\n{data.email_text}\n\nNapisz profesjonalną odpowiedź na ten email."
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": EMAIL_SYSTEM}, {"role": "user", "content": prompt}]
    )
    reply = r.choices[0].message.content
    db.save_email_draft({"sender": data.sender, "original": data.email_text, "draft": reply})
    return {"draft": reply}

# ── ФОТО UPLOAD ──
@app.post("/api/upload-photo")
async def upload_photo(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "gif", "webp"]:
        raise HTTPException(status_code=400, detail="Nieprawidłowy format pliku")
    filename = f"{uuid.uuid4()}.{ext}"
    path = f"{UPLOAD_DIR}/{filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"url": f"/uploads/{filename}"}

# ── ГУРТОЖИТКИ ──
@app.get("/api/dorms")
async def get_dorms():
    return db.get_dorms()

@app.put("/api/dorms/{dorm_id}")
async def update_dorm(dorm_id: int, data: dict, password: str = ""):
    check_admin(password)
    db.update_dorm(dorm_id, data)
    return {"ok": True}

@app.get("/api/rooms-structure")
async def get_rooms():
    return db.get_rooms_structure()

# ── БРОНЮВАННЯ ──
@app.post("/api/reservations")
async def make_reservation(r: ReservationIn):
    rid = db.add_reservation(r.dict())
    return {"id": rid, "status": "pending"}

@app.get("/api/reservations")
async def list_reservations(password: str = ""):
    check_admin(password)
    return db.get_reservations()

@app.patch("/api/reservations/{res_id}")
async def patch_reservation(res_id: int, status: str, password: str = ""):
    check_admin(password)
    db.update_reservation_status(res_id, status)
    return {"ok": True}

# ── МЕШКАНЦІ ──
@app.post("/api/residents")
async def add_resident(r: ResidentIn, password: str = ""):
    check_admin(password)
    rid = db.add_resident(r.dict())
    return {"id": rid}

@app.get("/api/residents")
async def list_residents(password: str = ""):
    check_admin(password)
    return db.get_residents()

@app.patch("/api/residents/{res_id}")
async def patch_resident(res_id: int, data: dict, password: str = ""):
    check_admin(password)
    if data.get("status") == "evicted":
        residents = db.get_residents()
        for r in residents:
            if r["id"] == res_id:
                db.add_history({**r, "eviction_date": data.get("checkout", "")})
    db.update_resident(res_id, data)
    return {"ok": True}

@app.get("/api/history")
async def get_history(password: str = ""):
    check_admin(password)
    return db.get_history()

# ── ЗАЯВКИ ──
@app.post("/api/tickets")
async def create_ticket(t: TicketIn):
    tid = db.add_ticket(t.dict())
    return {"id": tid}

@app.get("/api/tickets")
async def list_tickets(password: str = ""):
    check_admin(password)
    return db.get_tickets()

@app.patch("/api/tickets/{ticket_id}")
async def patch_ticket(ticket_id: int, data: dict, password: str = ""):
    check_admin(password)
    db.update_ticket(ticket_id, data)
    return {"ok": True}

@app.get("/api/my-tickets")
async def my_tickets(email: str = ""):
    all_r = db.get_reservations()
    all_t = db.get_tickets()
    return {
        "tickets": all_t,
        "reservations": [r for r in all_r if r.get("email") == email]
    }

@app.get("/api/email-drafts")
async def get_email_drafts(password: str = ""):
    check_admin(password)
    return db.get_email_drafts()

class NoteIn(BaseModel):
    date: str
    time: Optional[str] = ""
    text: str
    done: bool = False
    color: str = "blue"
    type: str = "work"

@app.get("/api/notes")
async def get_notes(password: str = ""):
    check_admin(password)
    return db._load("notes")

@app.post("/api/notes")
async def add_note(note: NoteIn, password: str = ""):
    check_admin(password)
    notes = db._load("notes")
    note_dict = note.dict()
    note_dict["id"] = len(notes) + 1
    note_dict["created"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    notes.append(note_dict)
    db._save("notes", notes)
    return note_dict

@app.patch("/api/notes/{note_id}")
async def update_note(note_id: int, data: dict, password: str = ""):
    check_admin(password)
    notes = db._load("notes")
    for n in notes:
        if n["id"] == note_id:
            n.update(data)
    db._save("notes", notes)
    return {"ok": True}

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int, password: str = ""):
    check_admin(password)
    notes = db._load("notes")
    notes = [n for n in notes if n["id"] != note_id]
    db._save("notes", notes)
    return {"ok": True}
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/", StaticFiles(directory="static", html=True), name="static")