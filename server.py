"""
Flask application implementing a simple REST API to serve 
IMDb movies data from TSV files.

Author Sirius Fuenmayor
"""

# import necessary libraries and functions
from flask import Flask, jsonify, request, send_from_directory
import csv, os

# We create an instance of the the Flask class
app = Flask(__name__, static_folder='static', static_url_path='')

# Starts the debugger. 
app.config["DEBUG"] = True

# To serve the static files of the SPA
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/movies/', methods=['GET'])
def movies():

  response = []

  # I get the search query parameters
  title = request.args.get('title')
  genre = request.args.get('genre')
  runtime = request.args.get('runtime')
  pageNumber = request.args.get('pageNumber')
  sortBy = request.args.get('sortBy')
  sortingOrder = request.args.get('sortingOrder')
  pageSize = 25

  # I will use the search query parameters to find all movies 
  # that match the parameters in the movies TSV file. I could 
  # put the filtered list of movies directly into memory but 
  # since the results could be large, and there could be many 
  # requests to the server at the same time, I will create a new 
  # file with the filtered results. Only a number of the results 
  # of this file will be returned in a response so if this is 
  # the first time a search with specific parameters is made and
  # there is no TSV file with the filtered results I will filter 
  # the main TSV file and create a new TSV file with the filtered 
  # results

  # if there is already a TSV file with the filtered results and 
  # the user only wants the next page we extract the desired set 
  # of results correspoding to the range requested from existing 
  # TSV file with filtered results
  rowNumber = 0
  try:
    # open the file
    with open("movies-" + "title-" + title + "-genre-" + genre + "-runtime-" + runtime + "-sortedBy-" + sortBy + "-" + sortingOrder + ".tsv", newline='', encoding="utf8") as parsedTsvfile:
      # populate the reader dictionary list
      reader = csv.DictReader(parsedTsvfile, delimiter='\t')
      # if the row or line number is between the requested range
      for row in reader:
        rowNumber += 1
        if ((rowNumber > int(pageNumber)*pageSize) and (rowNumber <= (int(pageNumber)+1)*pageSize)):
          # we add the dictionary associated with the current row
          # to the response
          response.append(row)
  # if there is no file associated with the search query then
  # we filter the main TSV file and create the filtered file:
  except IOError:
    # the runtime search query has the sintax 'min_duration-max_duration' 
    # so we split the runtime search query in an array with the 2 
    # values, min time and max time
    runtimes = runtime.rsplit('-',1)

    # we open the master TSV file with the movies info
    with open("only.movies.w.ratings.tsv", encoding="utf8") as tsvfile:
      # tsv file contents are readed as a dictionary and copied into
      # the "reader" object
      reader = csv.DictReader(tsvfile, delimiter='\t')
      # now we open the destination file that will contain the  
      # filtered results
      with open("movies-" + "title-" + title + "-genre-" + genre + "-runtime-" + runtime + ".tsv", 'w', newline='', encoding="utf8") as parsedTsvfile:
        fieldnames = ['tconst', 'titleType', 'primaryTitle', 'originalTitle', 'isAdult', 'startYear', 'endYear', 'runtimeMinutes', 'genres', 'averageRating', 'numVotes']      
        writer = csv.DictWriter(parsedTsvfile, fieldnames=fieldnames, delimiter='\t') 
        writer.writeheader()
        # and we write the filtered rows to the destination file
        # according to the search filters
        for row in reader:
          if ((title in row['primaryTitle']) and 
          ((genre in 'any') or (genre in row['genres'])) and 
          (runtime in 'any' or (row['runtimeMinutes'] != '\\N' and int(row['runtimeMinutes']) >= int(runtimes[0])) and (int(row['runtimeMinutes']) <= int(runtimes[1])))):
            writer.writerow(row)

    # We order the file with the filtered data as requested in query
    if sortingOrder == 'desc':
      reverseOrder = True
    else:
      reverseOrder = False

    # Open the results file and create and ordered dictionary list
    # according to the query parameters
    with open("movies-" + "title-" + title + "-genre-" + genre + "-runtime-" + runtime + ".tsv", newline='', encoding="utf8") as parsedTsvfile:
      reader = csv.DictReader(parsedTsvfile, delimiter='\t')
      # We are going to use the function sorted() to sort the results
      # by using as key the column selected in the sortBy filter
      # if the column values are strings such as primaryTitle we sort 
      # the values as string
      if sortBy == 'primaryTitle':
        sortedlist = sorted(reader, key = lambda row: row[sortBy], reverse=reverseOrder)
      # if the column values are numbers such as averageRating,
      # startYear and runtimeMinutes we sort the values as numbers
      elif (sortBy == 'startYear' or sortBy == 'runtimeMinutes' or sortBy == 'averageRating'):
        sortedlist = sorted(reader, key = lambda row: float(row[sortBy]) if ('\\N' not in row[sortBy]) else 0, reverse=reverseOrder)

    # Put that ordered list in a new file
    with open("movies-" + "title-" + title + "-genre-" + genre + "-runtime-" + runtime + "-sortedBy-" + sortBy + "-" + sortingOrder + ".tsv", 'w', newline='', encoding="utf8") as parsedOrderedTsvfile:
        fieldnames = ['tconst', 'titleType', 'primaryTitle', 'originalTitle', 'isAdult', 'startYear', 'endYear', 'runtimeMinutes', 'genres', 'averageRating', 'numVotes']      
        writer = csv.DictWriter(parsedOrderedTsvfile, fieldnames=fieldnames, delimiter='\t') 
        writer.writeheader()
        for row in sortedlist:
            writer.writerow(row)    

    # remove the unordered filtered TSV file
    os.remove("movies-" + "title-" + title + "-genre-" + genre + "-runtime-" + runtime + ".tsv")

    # we open the file with the filtered lines and return its first 
    # 25 lines as a response, every line of the TSV is a dictionary
    # that will be converted to JSON
    # open the file
    with open("movies-" + "title-" + title + "-genre-" + genre + "-runtime-" + runtime + "-sortedBy-" + sortBy + "-" + sortingOrder + ".tsv", newline='', encoding="utf8") as parsedTsvfile:
      # populate the reader dictionary list
      reader = csv.DictReader(parsedTsvfile, delimiter='\t')
      # if the row or line number is between the requested range
      for row in reader:
        rowNumber += 1
        if ((rowNumber > int(pageNumber)*pageSize) and (rowNumber <= (int(pageNumber)+1)*pageSize)):
          # we add the dictionary associated with the current row
          # to the response
          response.append(row)

  # We retun as a response the lines or rows in the TSV file 
  # resulting from the search in the requested range (page) 
  # as dictionaries converted to JSON
  #print(response)
  return jsonify(response)


# driver function
if __name__ == '__main__':

  app.run(host='0.0.0.0', debug=True, port=80)
