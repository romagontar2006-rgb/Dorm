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
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ADMIN_PASSWORD = "1111"
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

DORM_INFO = """
Jesteś profesjonalnym asystentem administracji akademików WSG Akademiki.

Twoim zadaniem jest pomaganie administracji w komunikacji z mieszkańcami akademików.

Zawsze:

* odpowiadaj uprzejmie, profesjonalnie i rzeczowo;
* używaj formalnego języka odpowiedniego dla administracji akademika;
* wykrywaj język wiadomości i odpowiadaj w tym samym języku;
* obsługuj język polski, ukraiński, angielski i rosyjski;
* twórz gotowe odpowiedzi e-mail, które można wysłać bez dodatkowej edycji;
* zachowuj neutralny i pomocny ton;
* podawaj jasne instrukcje dla mieszkańca, jeśli są potrzebne.

W przypadku pytań dotyczących:

* zakwaterowania,
* umów,
* płatności,
* przedłużenia pobytu,
* zgłoszeń technicznych,
* zasad akademika,

udzielaj odpowiedzi zgodnych z praktyką administracji akademików.

Jeżeli nie posiadasz wystarczających informacji, nie wymyślaj odpowiedzi. Napisz uprzejmie, że sprawa wymaga weryfikacji przez administrację.



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


Poniżej przesyłam wzór umowy zakwaterowania obowiązującej w naszych akademikach.

Zapoznaj się dokładnie z jej treścią i potraktuj ją jako materiał referencyjny do przyszłych odpowiedzi.

Nie cytuj automatycznie umowy i nie odwołuj się do konkretnych paragrafów, chyba że jest to konieczne do udzielenia poprawnej odpowiedzi.

Na co dzień odpowiadaj naturalnie, profesjonalnie i zwięźle, tak jak pracownik administracji akademika.

Wykorzystuj wiedzę wynikającą z umowy jako kontekst i źródło zasad obowiązujących mieszkańców, ale nie przytaczaj jej dosłownie bez potrzeby.

Jeżeli pytanie wymaga odniesienia do konkretnego punktu umowy, możesz wskazać odpowiedni zapis lub paragraf.

Teraz przeanalizuj poniższą umowę:

UMOWA NAJMU MIEJSCA W POKOJACH STUDENCKICH WSG
LEASE AGREEMENT FOR A PLACE IN WSG STUDENT SUITES

zawarta w Bydgoszczy, w dniu ........... pomiędzy 
concluded in Bydgoszcz on ........... between : 
Wyższą Szkołą Gospodarki w Bydgoszczy, ul. Garbary 2, 85-229 Bydgoszczy reprezentowanym przez Dyrektora Administracyjnego Tomasza Frejgandta zwanym w dalszej części umowy Wynajmującym 
WSG University in Bydgoszcz, at 2 Garbary street, 85-229 Bydgoszcz represented by the Administrative Director Tomasz Frejgandt hereinafter referred to as the Lessor
a / and ........... ...........
Legitymującą/cym się dokumentem tożsamości / having identity document nr ...........
Data urodzenia / Date of birth: ...........
PRZEDMIOT UMOWY
PL §1
1.	Przedmiotem niniejszej umowy jest korzystanie przez Najemcę z miejsca w pokoju 1-osobowym / 
2-osobowym / 3-osobowym* nr ........... w Pokojach studenckich przy ulicy ........... w Bydgoszczy.
2.	Niniejszą umowę zawiera się na czas określony od  ........... do  ...........
3.	Prawa i obowiązki Najemcy są określone w Regulaminie Pokoi  Podpisując niniejszą umowę Najemca oświadcza, że zapoznał się z ww. regulaminem i zobowiązuje się do jego przestrzegania oraz ponoszenia wszelkich konsekwencji wynikających z jego nieprzestrzegania.
SUBJECT OF THE CONTRACT
EN §1
4.	The subject of this agreement is the Lessee's use of a place in a single room/double room/ triple room* no. ...........  in Student suites at  ........... ........... Street in Bydgoszcz.
5.	This Agreement is concluded for a fixed period from  ........... to  ...........
6.	The rights and obligations of the Tenant are set out in the Student Residence Rules and Regulations. By signing this agreement the Lessee declares that he/she is familiar with the aforementioned Rules and Regulations and undertakes to observe them and bear all consequences resulting from their non-observance.
UPRAWNIENIA I OBOWIĄZKI NAJEMCY
PL §2
7.	Najemca zobowiązuje się do używania lokalu-pokoju akademickiego określonego w §1 umowy zgodnie z jego przeznaczeniem oraz umową, z poszanowaniem obowiązującego w budynku porządku domowego, Regulaminu Pokoi Studenckich, a także z poszanowaniem praw mieszkańców sąsiednich lokali.
8.	Bez zgody Wynajmującego, Najemca nie może zmienić przeznaczenia przedmiotu najmu, w szczególności dokonywać przebudowy pomieszczeń, innych przeróbek i adaptacji (np. zmiana koloru ścian, wieszanie plakatów, obrazów itp.)
9.	Najemca nie jest uprawniony do oddania przedmiotu najmu w podnajem ani do bezpłatnego używania osobom trzecim bez zgody Wynajmującego pod groźbą natychmiastowego rozwiązania umowy na mocy §5 ust.4, w przypadku stwierdzenia takiego faktu. Ponadto zachowanie może skutkować zatrzymaniem opłaty  jednorazowej (kaucji) przez Wynajmującego określonej w §4 pkt 4 umowy.
10.	Najemca w czasie trwania umowy najmu zobowiązany jest do  bezwzględnego przestrzegania przepisów przeciwpożarowych, oraz innych zaleceń i regulaminów ustanowionych przez Wynajmującego. W pokojach akademickich jak i w całym budynku obowiązuje całkowity zakaz palenia tytoniu i używania otwartego ognia. W przypadku stwierdzenia naruszenia tego zapisu Wynajmujący jest uprawniony do natychmiastowego rozwiązania niniejszej umowy na mocy §5 ust.4. Ponadto zachowanie może skutkować zatrzymaniem opłaty  jednorazowej (kaucji) przez Wynajmującego określonej w §4 pkt 4 umowy.
11.	Najemca w czasie trwania umowy najmu zobowiązany jest do bieżącego sprzątania pokoju w celu zachowania w czystości wynajmowanego lokalu oraz do poszanowania znajdującego się w nim wyposażenia a także do dbałości o czystość i stan techniczny wyposażenia w pomieszczeniach wspólnych.
12.	Najemca wyraża zgodę na ewentualne zamiany pokoju/miejsca w lokalu w trakcie trwania umowy najmu wynikające z potrzeb Wynajmującego.
13.	Najemca wyraża zgodę na wejście do pokoju pracowników Wynajmującego pod jego nieobecność w przypadku zagrożenia dla budynku lub mienia Wynajmującego. Z takiego zdarzenia Wynajmujący sporządzi stosowną notatkę.
14.	Najemca wyraża zgodę na interwencję pracowników firmy ochroniarskiej Wynajmującego bezpośrednio w lokalu Najemcy, w przypadku naruszania zapisów Regulaminu Pokoi Studenckich przez Najemcę lub przebywające w lokalu inne osoby. 
15.	Najemca ponosi pełną odpowiedzialność materialną za przekazane mienie stanowiące sprzęt oraz wyposażenie pokoju akademickiego.
16.	Najemca odpowiada za szkodę spowodowaną w powierzonym mieniu wg następujących zasad:
–	za szkodę w wyposażeniu indywidualnym pokoju akademickiego (wg protokołu zdawczo-odbiorczego) – osobiście do pełnej wysokości,
–	za szkodę w wyposażeniu pokoju – w częściach ułamkowych wg ilości osób zakwaterowanych w pokoju,
–	 za szkodę w otoczeniu Budynku Pokoi Studenckich  – osobiście w pełnej wysokości,
17.	Za zniszczenie sprzętu i urządzeń stanowiących wyposażenie budynku, piętra, części wspólnych (toalety, pralnie, korytarze, schody itp.) odpowiada sprawca szkody. W przypadku nie wykrycia sprawcy Wynajmujący zastrzega sobie prawo do dochodzenia szkody w częściach ułamkowych od mieszkańców budynku, piętra.
18.	Za zniszczenie mienia w Pokojach Studenckich noszące znamiona wandalizmu sprawca karany będzie natychmiastowym rozwiązaniem niniejszej umowy na mocy §5 ust.4 i wydaleniem z Pokoi Studenckich, jednocześnie zobowiązany jest do pokrycia kosztów napraw zdewastowanego sprzętu, części budynku itp. Ponadto zachowanie może skutkować zatrzymaniem opłaty  jednorazowej (kaucji) przez Wynajmującego określonej w §4 pkt 4 umowy.
19.	Studenci zainteresowani zamieszkaniem w Pokojach Studenckich w kolejnym okresie składają deklarację przedłużenia pobytu najpóźniej na dwa tygodnie przed jego rozpoczęciem.
–	deklaracje należy złożyć wysyłając wiadomość na adres: dormitory@byd.pl.
–	dane niezbędne do dokonania rezerwacji to: imię i nazwisko, płeć, data urodzenia, numer paszportu (w przypadku obcokrajowców), planowany okres pobytu, adres mailowy, polski numer telefonu kontaktowego. 
–	o przyznaniu miejsca decyduje kolejność zgłoszeń, jednak pierwszeństwo w uzyskaniu miejsc przypada dla studentów rozpoczynających studia w danym roku akademickim ,studentom Erasmusa oraz osobom, które z góry uiściły minimum 2 miesięczną opłatę za pobyt.
TENANT'S RIGHTS AND OBLIGATIONS
EN §2
20.	The Lessee undertakes to use the residential premises- academic room specified in §1 of this agreement in accordance with its intended use and the agreement, with respect for the domestic order in force in the building, the Regulations of the Student Residence, as well as with respect for the rights of residents of neighbouring premises.
21.	Without the consent of the Landlord, the Tenant may not change the intended use of the subject of the lease, in particular make alterations to the premises, other modifications and adaptations(example; changing the color of the walls, hanging any kind of picture on the walls etc).
22.	The Lessee shall not be authorised to sublet the subject of the lease or to make it available for free use to third parties without the Lessor's consent under the penalty of immediate termination of the agreement pursuant to §5 sect. 4 in the event of such a fact. In addition, such behavior results in the retention of a one-time fee (deposit) by the Lessor specified in §4 point 4 of the contract.
23.	The Tenant shall comply strictly with the fire safety regulations and other instructions and regulations established by the Landlord during the lease term. Smoking and the use of fire in academic rooms and in the entire building is strictly prohibited. In the event of any violation of this provision, the Lessor shall be entitled to immediately terminate this agreement pursuant to §5 sect. 4. In addition, such behavior results in the retention of the one-off fee (deposit) by the Lessor specified in §4 point 4.
24.	The Tenant shall, during the period of the tenancy, clean and maintain the cleanliness of the leased premises and respect the equipment contained therein as well as the cleanliness and state of repair of the equipment in the common areas.
25.	The Tenant agrees to any possible change of room/place in the premises during the term of the tenancy resulting from the needs of the Lessor.
26.	The Lessee consents to the Lessor's staff entering the room in his absence in the event of a threat to the building or the Lessor's property. The Lessor shall make an appropriate note of such an event.
27.	The Tenant agrees to the intervention of the Landlord's security company personnel directly in the Tenant's premises in the event of violation of the Student House Regulations by the Tenant or other persons residing in the premises. 
28.	The Tenant takes full material responsibility for the equipment and furnishings entrusted to him.
29.	The tenant is responsible for damage caused to the entrusted property according to the following rules:
–	for damage to personal equipment of the academic room (according to the handover and acceptance protocol) up to the full amount,
–	for damage to room equipment - in fractions according to the number of persons accommodated in the room,
–	for damage to the surroundings of the Student's suite - personally in the full amount,
30.	The perpetrator of the damage is held responsible for damage to equipment and devices that are part of the furnishing of the building, floor and common areas (toilets, laundry rooms, corridors, stairs, etc.), but if the perpetrator is not found, the Landlord reserves the right to claim the damage in fractional parts from the residents of the floor.
31.	For damage to the property of the Student's suite which bears the signs of vandalism, the offender will be punished with immediate termination of this agreement pursuant to §5.4 and expulsion from the Student's suite; at the same time he/she is obliged to cover the costs of repairs of the devastated equipment, parts of the building, etc. In addition, such behavior results in the retention of the one-time fee (deposit) by the Lessor specified in §4 point 4 of the contract.. Students interested in living in the Student House in the next period submit a declaration
32.	Students interested in living in the Student Residence in the following period shall submit a declaration of extension of their stay at the latest two weeks before its commencement.
–	declarations should be made by sending a message to: dormitory@byd.pl.
–	The data necessary for the reservation are: name and surname, gender, date of birth, passport number (in case of foreigners), planned period of stay, e-mail address, Polish contact phone number. 
–	The place is allocated on a first-come, first-served basis, however, priority is given to students commencing their studies in a given academic year Erasmus Students and to those who have paid a minimum of two months' stay in advance.
UPRAWNIENIA I OBOWIĄZKI WYNAJMUJĄCEGO
PL §3
33.	Wynajmujący zobowiązuje się wydać Najemcy przedmiot najmu określony w §1 umowy w stanie przydatnym do umówionego użytku i utrzymywać go w takim stanie przez cały czas trwania niniejszej umowy.
34.	Wynajmujący zobowiązuje się do wykonania bieżących drobnych napraw przedmiotu najmu na koszt Najemcy o ile są one wynikiem zdarzeń, za które odpowiedzialność ponosi Najemca. Należności z tytułu bieżących, napraw pobierane są z opłaty jednorazowej, o której mowa w § 4 punkt 4. Jeżeli wartość napraw przekracza wysokość opłaty jednorazowej (kaucji) Wynajmujący ma prawo do dochodzenia różnicy z polisy opisanej w § 4 ust.5 lub bezpośrednio od Najemcy.
RIGHTS AND OBLIGATIONS OF THE LESSOR
EN §3
35.	The Lessor undertakes to return the subject of the lease specified in §1 of this contract to the Lessee in a condition suitable for the agreed use and to maintain it in such condition throughout the term of this contract.
36.	The Lessor shall make current minor repairs of the subject of the lease at the expense of the Lessee, provided that they are the result of events for which the Lessee is responsible. Amounts due for current repairs shall be collected from the one-off fee referred to in § 4 section 4. If the value of repairs exceeds the amount of the one-off fee (deposit) The Lessor has the right to claim the difference from the policy described in § 4 section 5  or directly from the Lessee.
CZYNSZ I INNE OBCIĄŻENIA
PL §4
37.	Najemca zobowiązuje się płacić miesięczny czynsz o którym mowa w §1 ust. 1 w wysokości 1 150 PLN /  950 PLN / 900 PLN / 850 PLN miesięcznie (słownie: tysiąc sto pięćdziesiąt PLN / dziewięćset pięćdziesiąt PLN / dziewięćset PLN / osiemset pięćdzisiąt PLN). Osoby kwaterujące się po 15 dniu miesiąca wnoszą odpłatność w wysokości 50% miesięcznej stawki. Zakwaterowanie przed 15 dniem miesiąca wiąże się z koniecznością uregulowania odpłatności za cały miesiąc. Osoby wykwaterowujące się do 15-go dnia miesiąca wnoszą odpłatność w wysokości 50% miesięcznej stawki. Wykwaterowanie po 15-tym dniu miesiąca wiąże się z koniecznością uregulowania odpłatności za cały miesiąc.
38.	Czynsz miesięczny zawiera opłaty za wodę, ścieki, wywóz śmieci, energię elektryczną, ogrzewanie, Internet, sprzątanie części wspólnych
39.	Najemca zobowiązuje się do uiszczania na rzecz Wynajmującego opłaty, o której mowa w §4 ust. 1 w terminie do 10 dnia miesiąca na indywidualne konto bankowe 16109000048853300400234547, które znajduje się również na koncie studenta w systemie new.isaps.pl. Za datę wpłaty uważa się dzień wpływu należności na rachunek bankowy. Potwierdzenie dokonanej wpłaty należy dostarczyć mailowo na adres e-mail: bof@byd.pl. Obowiązującą wysokość opłat oraz zasady odpłatności reguluje odpowiednie dla danego Roku Akademickiego Zarządzenie Rektora WSG.
40.	W celu zabezpieczenia pokrycia ewentualnych kosztów zniszczeń spowodowanych przez Najemcę, a także pozostałych zobowiązań Najemcy wobec Wynajmującego w tym opłat czynszowych lub pokrycia nieuiszczonych opłat wynikających z zawartej z Wynajmującym umowy o warunkach kształcenia i zasadach odpłatności za studia ,Wynajmujący pobiera opłatę jednorazową (depozyt) w wysokości czynszu tj.: 1 150 PLN /  950 PLN / 900 PLN / 850 PLN *.
–	z wpłaty depozytu zwolnieni są studenci przybywający w ramach programów mobilności studenckiej (Erasmus, Kazachstan) lub innych umów pomiędzy WSG a partnerami.
41.	W celu zabezpieczenia pokrycia ewentualnych kosztów uszkodzeń mienia, wypadków w czasie pobytu w domu akademickim, kosztów leczenia powstałych w wyniku wypadków losowych, Najemca zobowiązuje się do zawarcia indywidualnej polisy OC (odpowiedzialność cywilna) za pośrednictwem Samorządu Studenckiego Wyższej Szkoły Gospodarki -www.samorzad. byd.pl; zakładka: Ubezpieczenia w terminie 7 dni od daty podpisania niniejszej umowy
42.	Najemca reguluje opłatę jednorazową, o której mowa w §4 ust. 5 najpóźniej do 7 dni od dnia podpisania umowy na konto bankowe 16109000048853300400234547, które znajduje się również na koncie studenta new.ISAPS. W przypadku wykorzystania pełnej kwoty depozytu wymienionego w §4 ust. 5 na pokrycie kosztów tam określonych, Wynajmujący ma prawo pobrać od Najemcy kolejny depozyt w takiej samej kwocie lub/i zabezpieczyć się z polisy OC.
43.	Depozyt jest zwracany Najemcy w całości albo pomniejszony o koszty określone w §4 ust. 5, w przypadku ich poniesienia, po zakończeniu umowy najmu i opuszczeniu z zajmowanego lokalu.
44.	W przypadku nie opuszczenia lokalu przez Najemcę w dniu wygaśnięcia lub rozwiązania umowy depozyt zostanie przeznaczony na pokrycie kosztów bez umownego korzystania z lokalu. 
45.	Najemca jest zobowiązany zdać przedstawicielowi Wynajmującego klucze oraz inne urządzenia przekazane do użytku przez Wynajmującego natychmiast po wykwaterowaniu się z lokalu.
46.	Za zwłokę w dokonywaniu opłat Najemca płaci odsetki ustawowe.
47.	W przypadku wzrostu kosztów mediów, kosztów eksploatacyjnych budynku, wzrostu stawek podatków, i innych czynników niezależnych od Wynajmującego czynsz miesięczny może ulec zmianie jeden raz w roku, na co Najemca wyraża zgodę.
RENT AND OTHER CHARGES
EN §4
48.	The Lessee undertakes to pay the monthly rent referred to in §1 par. 1 in the amount of PLN 1 150 / PLN  950 / PLN 900 / PLN 850 per month (in words: One thousand one hundred fifty  /nine hundred fifty / nine hundred / eight hundred fifty). Persons accommodated after the 15th day of the month pay 50% of the monthly rate. Accommodation before the 15th day of the month requires payment for the entire month. Check-out by the 15th of the month is charged at 50% of the monthly rate. If you move out after the 15th of the month, the customer will have to pay for the whole month.
49.	The monthly rent includes charges for water, rubbish and sewage disposal, electricity, internet and cleaning of common areas 
50.	The Lessee undertakes to pay to the Lessor the fee referred to in §4, par. 1 by the 10th day of the month to the individual bank account 16109000048853300400234547, which is also held in the student's account in the new.isaps.pl system. The date of payment shall be the date on which the payment is received in the bank account. Confirmation of payment should be delivered by e-mail to: bof@byd.pl. The applicable amount of fees and the rules of payment are regulated by the appropriate WSG Rector's Decree for the given Academic Year.
51.	In order to secure the coverage of possible costs of damage caused by the Lessee, as well as other obligations of the Lessee including rental fees or covering unpaid fees as concluded with the lessor on the terms and principles of payment , the Lessor charges a one-off fee (deposit) in the amount of the rent, i.e: PLN 1 150 / PLN  950 / PLN 900 / PLN 850 *.
–	students coming within the framework of student mobility programmes (Erasmus, Kazakhstan) or other agreements between WSG and partners are exempted from paying a deposit.
52.	In order to secure coverage of possible costs of property damage, accidents during the stay in the academic house, medical costs arising as a result of random accidents, the Lessee undertakes to conclude an individual third party liability policy (civil liability) through the Student Government of the University of Economy - www.samorzad. byd.pl; tab: Insurance within 7 days from the date of signing this contract.
53.	The Lessee shall pay the one-off fee referred to in §4 par. 5 within 7 days of signing the agreement at the latest to the individual bank account 16109000048853300400234547, which is also held in the student's account in the new.isaps.pl system. If the full amount of the deposit mentioned in §4 par. 5 is used to cover the costs specified therein, the Landlord is entitled to charge the Tenant another deposit in the same amount and/or secure himself from the third party liability policy.
54.	The deposit shall be returned to the Tenant in full or reduced by the costs specified in §4 par. 5, if incurred, upon termination of the tenancy agreement and vacating the premises.
55.	If the tenant does not vacate the premises at the date of expiry or termination of the agreement, the deposit will be used to cover the costs of non-contractual use of the premises. 
56.	The tenant is obliged to hand over the keys and other equipment handed over for use by the landlord to the representative of the landlord immediately after vacating the premises.
57.	The Tenant shall pay statutory interest for late payment of fees.
58.	In the event of an increase in the cost of utilities, building operating costs, increase in tax rates, and other factors beyond the control of the Landlord, the monthly rent may be changed once a year, to which the Tenant agrees.
ROZWIĄZANIE UMOWY
PL §5
59.	Okres wypowiedzenia umowy przez każdą ze stron wynosi 3 miesiące-obowiązuje forma pisemna wypowiedzenia .Wypowiedzenie należy składać na dormitory@byd.pl.
60.	Niniejsza umowa ulega automatycznemu rozwiązaniu w przypadku 
–	nie zakwaterowania się w terminie 2 dni od podpisania umowy,
–	niedopełnienia obowiązujących zasad zakwaterowania.
61.	Niniejsza umowa ulega rozwiązaniu z zachowaniem okresu wypowiedzenia określonym w ust. 1 w przypadku 
–	rezygnacji pisemnej Najemcy z zakwaterowania  na adres Dormitory@byd.pl
–	nie uregulowania należności za bieżący miesiąc do 10 dnia następnego miesiąca (w przypadku kontynuacji zakwaterowania),
–	skreślenia z listy studentów,
–	ukończenia studiów (obrony pracy dyplomowej).
62.	Niniejsza umowa ulega rozwiązaniu w trybie natychmiastowym, z zachowaniem konsekwencji finansowych wynikających z okresu wypowiedzenia oraz (§4 ust.4-kaucja) w przypadku
–	rażącego naruszenia przez Najemcy postanowień niniejszej Umowy, Regulaminu Pokoi Studenckich lub norm współżycia społecznego,
–	przypadkach opisanych w niniejszej umowie,
–	rezygnacji najemcy z zakwaterowania bez powiadomienia o tym Wynajmującego.
63.	Niniejsza umowa ulega rozwiązaniu w przypadku niespełnienia przez Najemcę wymagań związanych z zakwaterowaniem, a narzuconych przez akty wyższego rzędu. (Np. obowiązku szczepień dla osób przebywających w obiektach zbiorowego zakwaterowania, utrata prawa pobytu w Polsce). 
64.	Przed dokonaniem formalności związanych z wykwaterowaniem, Najemca jest zobowiązany do uiszczenia na rzecz Najemcy należnych i wymaganych opłat z tytułu zakwaterowania.
65.	W razie rozwiązania umowy lub jej wygaśnięcia Najemca zobowiązany jest do opuszczenia zajmowanego lokalu w terminie 2 dni lub w uzasadnionych przypadkach dłuższym, wyznaczonym przez Wynajmującego. W przypadku niedopełnienia przez Najemcy tego obowiązku, Wynajmujący jest upoważniony do komisyjnego wykwaterowania oraz do przeniesienia ruchomości Najemcy do magazynu na koszt i ryzyko Najemcy, na co Najemca wyraża zgodę.
66.	Rzeczy osoby wykwaterowanej są komisyjnie zabezpieczane przez Wynajmującego przez okres jednego miesiąca od dnia komisyjnego wykwaterowania. Nie zgłoszenie się osoby wykwaterowanej po odbiór swoich rzeczy w wyżej ustalonym terminie skutkuje przekazaniem ich instytucjom pomocy społecznej lub komisyjnym zniszczeniem, na co Najemca  wyraża zgodę.
67.	Najemca w momencie opuszczenia/ zdawania pokoju akademickiego, niezależnie od przyczyn- upływ terminu umowy, wypowiedzenia umowy, rozwiązania umowy w trybie natychmiastowym zobowiązany jest do gruntownego posprzątania pokoju akademickiego. W przypadku nie posprzątania pokoju akademickiego Wynajmujący ma uprawnienie do zatrzymaniem opłaty  jednorazowej (kaucji) przez Wynajmującego określonej w §4 pkt 4 umowy w wysokości pokrywającej koszty sprzątania zastępczego.
TERMINATION OF THE AGREEMENT
EN §5
68.	The period of notice for termination of the contract by either party shall be 3 months. The termination must be submitted to the dormitory@byd.pl
69.	This Agreement shall automatically terminate in the event of 
–	not to be accommodated within two days of signing the contract,
–	failure to comply with the accommodation rules in force.
70.	This Agreement shall terminate with the notice period specified in paragraph 1 in the event of 
–	Tenant's resignation from accommodation should be put in written and sent to dormitory@byd.pl
–	failure to pay for the current month by the 10th day of the following month (in the case of continued accommodation),
–	removal from the list of students,
–	completion of studies (defence of the diploma thesis).
71.	This agreement shall be terminated with immediate effect, subject to the financial consequences resulting from the notice period and (§ 4 section4-deposit) in the event of 
–	gross violation by the Tenant of the provisions of this Agreement, the Student Residence Regulations or standards of social coexistence,
–	in the cases described in this Agreement,
–	the tenant resigns from accommodation without informing the Lessor.
72.	This agreement shall be terminated if the Tenant fails to comply with accommodation requirements imposed by higher-level legislation. (e.g. vaccination obligation for persons staying in collective accommodation or loss of the right of residence in Poland). 
73.	Before the check-out formalities are completed, the Tenant shall pay to the Renter the accommodation fees due and required.
74.	In the event of the termination of the agreement or its expiry, the Tenant is obliged to vacate the premises occupied by him/her within 2 days or, in justified cases, longer, as specified by the Student Lessor. Should the Lessee fail to comply with this obligation, the Lessor of the Student's House is authorised to conduct a removal procedure and to transfer the Lessee's movables to a storage facility at the expense and risk of the Lessee, to which the Lessee agrees by signing this agreement.
75.	The student's belongings are secured by the Lessor of the Student's suite for a period of one month from the date of removal. If the student does not come to collect their belongings within the aforementioned time limit, they will be handed over to social welfare institutions or destroyed by the committee, which the Tenant hereby agrees to.
76.	The tenant at the time of leaving / passing the academic room, regardless of the reasons - the expiry of the contract period, termination of the contract, termination of the contract with immediate effect is obliged to thoroughly clean the academic room. In the event of not cleaning the academic room, the Lessor has the right to retain the one-off fee (deposit) by the Lessor specified in §4 point 4 of the contract in the amount covering the costs of replacement cleaning.
POSTANOWIENIE KOŃCOWE
PL §6
77.	Wszystkie zmiany niniejszej umowy wymagają dla swojej ważności formy pisemnej.
78.	W przypadku przekwaterowania najemcy do innego pokoju lub lokalizacji, w sytuacji gdy zmiana nie generuje innych kwot czynszu,  jest ona nanoszona na obydwa egzemplarze umowy i parafowana przez każdą ze stron.
79.	W przypadku zmiany standardu pokoju umowa jest rozwiązywana z datą zaistnienia zmiany i podpisywana jest nowa umowa.
80.	W razie wypadku lub innej sytuacji zagrażającej zdrowiu lub życiu Najemca wyraża zgodę na powiadomienie:
–	Imię i nazwisko …………………………………………………	tel. ………………………………………………….
–	Imię i nazwisko …………………………………………………	tel. ………………………………………………….
81.	W sprawach nieuregulowanych niniejszą umową mają zastosowanie przepisy kodeksu cywilnego. Wszelkie spory mogące wyniknąć z realizacji niniejszej umowy strony poddają rozstrzygnięciu właściwego rzeczowo Sądu w Bydgoszczy.
82.	Umowę sporządza się w dwóch jednobrzmiących egzemplarzach, po jednym dla każdej ze stron.
FINAL CLAUSES
EN §6
83.	All amendments to this Agreement shall be made in writing and shall be valid.
84.	In the event of a tenant being relocated in another room/location, where the change does not generate a different amount of rent, it shall be noted on both copies of the agreement and initialled by each of the parties.
85.	In the event of a change of room standard, the contract is terminated on the date of the change and a new contract is signed.
86.	In the event of an accident or any other situation endangering health or life, the Tenant agrees to notify:
–	Name and surname …………………………………………………	tel. ………………………………………………….
–	Name and surname …………………………………………………	tel. ………………………………………………….
87.	In matters not regulated by this agreement, the provisions of the Civil Code shall apply. Any disputes that may arise from the performance of this agreement shall be submitted by the parties to the resolution of the Court in Bydgoszcz, Poland.
88.	The Agreement shall be drawn up in duplicate, one for each party.



……………………………………………………..	………………………………………………………
	Podpis Najemcy / Tenant’s Sign	podpis Wynajmującego / Lessor’s Sign


Oświadczenie
Wyrażam zgodę na przetwarzanie moich danych osobowych zgodnie z rozporządzeniem Parlamentu Europejskiego i Rady (UE) 2016/679 z dnia 27.04.2016 r. („RODO”) przez administratora danych: Wyższa Szkoła Gospodarki w  Bydgoszczy (Garbary 2, 85- 229 Bydgoszcz) w celu i w zakresie niezbędnym do realizacji niniejszej umowy. Jestem świadomy/ świadoma, że przysługuje mi prawo do wglądu i poprawiania moich danych osobowych.

Statement
I consent to the processing of my personal data in accordance with Regulation (EU) 2016/679 of the European Parliament and of the Council of 27.04.2016. ("RODO") by the data controller: Wyższa Szkoła Gospodarki in Bydgoszcz (Garbary 2, 85- 229 Bydgoszcz) for the purpose and to the extent necessary for the performance of this agreement. I am aware that I have the right to inspect and correct my personal data
.

 	……………………………………………………..
 	Podpis Najemcy / Lessor’s Sign
(* - niepotrzebne skreślić/ delete as appropriate)




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
- Ceny: pokój 1-os. 1150 PLN, pokój 2-os. 850 PLN, 3-os. 700 PLN, kaucja 850 PLN
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
    phone: str = ""
    email: str = ""
    is_wsg: bool = True
    gender: str = "any"
    dorm_id: int
    floor: str = ""
    room: str = ""
    checkin: str
    checkout: str = ""
    full_name: str = ""
    notes: str = ""
    status: str = "pending"

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

    prompt = f"""
Otrzymujesz email od mieszkańca akademika.

Nadawca: {data.sender if data.sender else "brak"}
Treść emaila:
{data.email_text}

Zadanie:
1. Wykryj język wiadomości.
2. Odpowiedz w tym samym języku:
   - jeśli email jest po polsku — odpowiedz po polsku,
   - jeśli email jest po angielsku — odpowiedz po angielsku,
   - jeśli email jest po ukraińsku — odpowiedz po ukraińsku,
   - jeśli email jest po rosyjsku — odpowiedz po rosyjsku.
3. Odpowiedź ma być profesjonalna, uprzejma i w stylu administracji akademika.
4. Nie dodawaj zbędnych wyjaśnień.
5. Podpisz wiadomość jako administracja akademika.
"""

    try:
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Jesteś profesjonalnym asystentem administracji akademika WSG. Piszesz krótkie, uprzejme i formalne odpowiedzi."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        reply = r.choices[0].message.content

        db.save_email_draft({
            "sender": data.sender,
            "original": data.email_text,
            "draft": reply
        })

        return {"draft": reply}

    except Exception as e:
        print("EMAIL AI ERROR:", str(e))
        return {
            "draft": f"Błąd generowania odpowiedzi AI: {str(e)}"
        }

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

@app.put("/api/reservations/{res_id}")
async def update_reservation(res_id: int, data: dict, password: str = ""):
    check_admin(password)
    db.update_reservation(res_id, data)
    return {"ok": True}

@app.delete("/api/reservations/{res_id}")
async def delete_reservation(res_id: int, password: str = ""):
    check_admin(password)
    db.delete_reservation(res_id)
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