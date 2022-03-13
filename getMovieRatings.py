# Ranks movies using ratings from IM data base

import os
import time

from imdb import Cinemagoer

def main():
    with open("movies.txt", "r") as f:
        videoNames = [line.strip() for line in f.readlines()]

    videoNames = videoNames[:10]
    rating = {}
    ia = Cinemagoer()
    for videoName in videoNames:
        movies = ia.search_movie(videoName)
        if len(movies) == 0:
            print("No movie found for: " + videoName)
            rating[videoName] = 0.0
            continue
        movie = movies[0]
        time.sleep(0.5)
        ratingFound = ia.get_movie(movie.getID(), info=['main']).get('rating')
        if ratingFound is None:
            print("No rating found for: " + videoName)
            rating[videoName] = 0.0
            continue
        else:
            print(f"Rating for {videoName} was {ratingFound}")
        ratingFound = float(ratingFound)
        rating[videoName] = ratingFound
        time.sleep(0.5)

    videoNames.sort(key = lambda x: rating[x], reverse = True)
    print(list(zip(videoNames, sorted(rating.values(), reverse=True))))

if __name__ == "__main__":
    main()
