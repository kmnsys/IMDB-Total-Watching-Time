import requests
from bs4 import BeautifulSoup

print("1) Calculate Only Movie Watching Time(Faster - 4 secs/page)")
print("2) Calculate Both Movie and TV-Series Watching Times(Slower - 2 mins/page) ")

while True:
    choiceMT = int(input("Choose 1 or 2: "))
    if choiceMT == 1 or choiceMT == 2:
        while True:
            next_page = input("\nEnter ratings page link: ")
            imdb = requests.get(next_page)
            if imdb.status_code == 404:
                print("Invalid URL! Try Again")
            else:
                break
        break
    else:
        print("Invalid Choice! Try Again")

imdb_main = "https://www.imdb.com"
#next_page = "https://www.imdb.com/user/ur76920409/ratings"

def checkmovie(link): # Check if it is a movie or tv-series
    content_req = requests.get(link)
    content_soup = BeautifulSoup(content_req.text, "html.parser")
    check = content_soup.find_all('div', class_="button_panel navigation_panel")
    runtime = 0
    if check == []:
        #print("Movie")
        return 1, runtime
    else:
        #print("TV-Series")
        episodes = check[0].a.div.div.span.text
        episodes = int(episodes[:-9])
        return 0, episodes # return episode number

def runtimeToMin(runtime): # convert runtime string to minutes integer
    hr = 0
    min = 0
    len_runt = len(runtime)
    for i in range(len_runt):
        if runtime[i] == "h":
            hr = int(runtime[:i - 1])
        if runtime[i] == "m":
            if i-3>=0:
                min = int(runtime[i - 3:i])
            else:
                min = int(runtime[:i])
    runtime = 60 * hr + min
    return runtime

unknowns = []
def OnlyMovies(page_link): # Visit only rating list not all movie-tv pages individually for faster solution
    i = 0
    imdb = requests.get(page_link)
    soup = BeautifulSoup(imdb.text, "html.parser")
    rated_divs = soup.find_all('div', class_="lister-item mode-detail")

    movie_runtime = 0
    for rating in rated_divs:
        i += 1
        content = rating.find(class_="lister-item-content")

        name = content.h3.a.text
        runtime = content.find('span', class_="runtime")
        if runtime == None:
            runtime = "0 hr"
            unknowns.append(name)
        else:
            runtime = runtime.text
        runtime = runtimeToMin(runtime)

        if runtime > 70: # Get only runtimes above 70 mins as movies (Optional)
            movie_runtime += runtime
        print(i, name, "-", "Runtime: ", runtime)

    page = soup.find('div', class_="list-pagination")
    page = page.find_all('a')
    next_page = page[1]['href']
    #print(next_page)

    if next_page == "#":
        return 0, movie_runtime
    else:
        next_page = imdb_main + next_page
        #print(next_page)
        return next_page, movie_runtime

def MovAndTV(page_link): # Visit all movie-tv pages individually and get episode numbers (Too Slow)
    i = 0
    imdb = requests.get(page_link)
    soup = BeautifulSoup(imdb.text, "html.parser")
    rated_divs=soup.find_all('div', class_="lister-item mode-detail" )

    movie_runtime = 0
    tv_runtime = 0
    for rating in rated_divs:
        i+=1
        content = rating.find(class_="lister-item-content")
        name = content.h3.a.text

        content_page = content.h3.a['href']
        content_page_link = imdb_main+content_page

        checkMT = checkmovie(content_page_link)
        if checkMT[0] == 1:
            #runtime = int(checkMT[1])
            runtime = content.find('span', class_="runtime")
            if runtime == None:
                runtime = "0 hr"
                unknowns.append(name)
            else:
                runtime = runtime.text
            runtime  =runtimeToMin(runtime)
            movie_runtime += runtime
            print(i, name, "-", "Runtime: ",runtime)

        if checkMT[0] == 0:
            runtime = content.find('span', class_="runtime")
            if runtime == None:
                runtime = "0 hr"
                unknowns.append(name)
            else:
                runtime = runtime.text

            isepisode = content.h3.small
            if isepisode == None:
                episodes = checkMT[1]
            else:
                episodes = 1

            eptime = runtimeToMin(runtime)
            runtime = eptime*episodes
            tv_runtime += runtime

            print(i, name, "(", episodes, ") - Episode Runtime: ",eptime, "- TV Runtime: ", runtime)

    page = soup.find('div', class_="list-pagination")
    page = page.find_all('a')
    next_page = page[1]['href']
    #print(next_page)

    if next_page == "#":
        return 0, movie_runtime, tv_runtime
    else:
        next_page = imdb_main + next_page
        #print(next_page)
        return next_page, movie_runtime, tv_runtime

def convertTime(runtime):
    minutes = 0
    hours = 0
    days = 0
    months = 0

    hours = int(runtime / 60)
    mins = int(runtime % 60)

    if (hours > 24):
        days = int(hours / 24)
        hours = int(hours % 24)

        if (days > 30):
            months = int(days / 30)
            days = int(days % 30)
    return mins, hours, days, months

movie_runtime = 0
tv_runtime = 0
i = 1
while next_page != 0:
    print("\n", i, ". Page\n")
    if choiceMT == 1:
        next_page, mov = OnlyMovies(next_page)
        movie_runtime += mov
    else:
        next_page, mov, tv= MovAndTV(next_page)
        movie_runtime += mov
        tv_runtime += tv
    i+=1


if choiceMT == 1:
    mminutes, mhours, mdays, mmonths = convertTime(movie_runtime)
    print("\n\nMovie Watching Time:", mmonths, "Months", mdays, "Days", mhours, "Hours", mminutes, "Minutes")

else:
    total_runtime = movie_runtime+tv_runtime
    minutes, hours, days, months = convertTime(total_runtime)
    mminutes, mhours, mdays, mmonths = convertTime(movie_runtime)
    tminutes, thours, tdays, tmonths = convertTime(tv_runtime)

    print("\n\nMovie Watching Time:", mmonths, "Months", mdays, "Days", mhours, "Hours", mminutes, "Minutes")
    print("Series Watching Time:", tmonths, "Months", tdays, "Days", thours, "Hours", tminutes, "Minutes")
    print("***", minutes, hours, days, months)
    print("TOTAL Watching Time:", months, "Months", days, "Days", hours, "Hours", minutes, "Minutes")

    print("\nUnknown Runtimes:")
    for i in unknowns:
        print(i)

input("\nPress enter to close...")





