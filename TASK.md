# Intro

Celem projektu jest stworzenie aplikacji do zapisywania wyników meczów w ping-ponga (i w inne gry indywidualne, np. badmington, squash, tenis zmiemny, bilard, lotki) podczas turniejów.

Organizator organizuje turniej, wybierając dyscyplinę oraz ilość
zawodników. Turniej ma też nazwę i puchar, który można zdobyć. Obrazki pucharów powinne być automatycznie generowane na podstawie nazwy/daty/etc.
Tutaj inwencja twórcza mile widziana.

Każda dyscyplina ma swoje właściwości.

Zawodnicy zapisują się na turniej.
Pokazuje się wizualizacja turnieju w formie drzewka. W zależności od dyscypliny
na drzewku rozgrywek pojawia się odpowiednie boisko oraz przeciwnicy.


Zawodnicy grają mecz w rzeczywistych warunkach. Aplikacja służy do wizualizacji, postępów, rankingu i przypomnienia o meczu. Po meczu podają wynik (sety oraz punkty cząstkowe).
W ping ponga gra może być do 11 lub do 21.

Jeden z zawodników podaje wynik. Aby on się ukazał, potrzeba akceptacji
drugiego zawodnika. Jeżeli tej akceptacji nie ma, to organizator
musi rozwiązać spór.

Aplikacja udostępnia ranking graczy (ranking danego turnieju jak i ogólny). Ranking ogólny jest liczony na podstawie wszystkich rozegranych meczy.

Aplikacja przypomina o nadchodzącym meczu poprzez notyfikację "push".

Aplikacja umożliwia "wyzwanie na pojedynek" - czyli mecz ad hoc. Taki mecz liczy się też do rankingu ogólnego.

# Wymagania techniczne - backend/fullstack

* django templates
* fikstury wygenerowane przez factory_boy i faker
* backend w Django i baza danych postgresql


# Wymagania techniczne - frontend

* react js
* min. json server  z przykładowymi danymi, tak aby po uruchomieniu projketu była dostępna wersja klikalna
* RWD
* PWA
* webpack 
 

# Wymagania projektowe

* testy
* kod, commity i komentarze po angielsku
* pull requesty
* projekt realizowany w etapach, zależy nam na dobrej komunikacji i iteracyjnym podejściu
* projekt nie musi być zrealizowany do końca, raczej zakładamy iż kandydat dokończy go już w pracy
* projekt ma dać pole do rozmowy w biurze
* README.md z dokładnym opisem jak uruchomić aplikację (po angielsku)

