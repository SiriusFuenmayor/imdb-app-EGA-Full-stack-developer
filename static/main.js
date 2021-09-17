// En caso de que se quieran hacer cosas cuando el contenido se cargue
document.addEventListener('DOMContentLoaded', init);
function init() {
  //document.getElementById('ID_DEL_ELEMENTO').addEventListener('click', FUNCION_PARA_LLAMAR_POR_EVENTO_CLICK);
}

/******************************************/
/********** Search form control **********/
/******************************************/

// Variables needed for fetching
var title = '';
var genre = 'any';
var runtime = 'any';
var sortField = 'title';
var sortingOrder = 'asc';
var pageNumber = 0;

function setTitle() {
  title = document.getElementById("title").value;
}
function setGenre() {
  genre = document.getElementById("genre").value;
}
function setRuntime() {
  runtime = document.getElementById("runtime_").value;
}
function setSortField() {
  sortField = document.getElementById("sort_field").value;
}
function setSortingOrder() {
  sortingOrder = document.getElementById("sorting_order").value;
}

function startSearch(event) {

  event.preventDefault();

  console.log('Search started');
  pageNumber = 0;
  fetchData(pageNumber);
}

const form = document.getElementById('search_form');
form.addEventListener('submit', startSearch);

/******************************************/
/******* Search result list control *******/
/******************************************/

function fetchData(pageNumber) {

  //////////////////////////////////////////////////////////
  // CREAR QUERY PARA LA BUSQUEDA O FETCH A PATIR DE LA
  // DATA RECOPILADA EN EL FORMULARIO DE FILTROS DE BUSQUEDA
  
  // Ejemplo search query
  // https://myapp.com/movies?groups=top_1000&view=simple&sort=user_rating,desc 

  // Posibles parametros
  //
  // sort=runtime,year,rating,title
  // filter by genre, runtime, title
  
  // If a new search query is made...
  if (title) {

    // Construct the query string
    var searchQueryString ='title=' + title + 
                        '&genre=' + genre +
                        '&runtime=' + runtime +
                        '&pageNumber=' + pageNumber +                      
                        '&sortBy=' + sortField + 
                        '&sortingOrder=' + sortingOrder;                        

    console.log('Query string: ' + searchQueryString);

    // and the final URL for fetching
    finalURL = '/api/movies/?' + searchQueryString
    console.log('Final URL: ' + finalURL);

    // Every time a new search is made the page number
    // is cleaned
    var myList = document.querySelector('ul');
    myList.innerHTML = '';
 
    //////////////////////////////////////////////////////////
    // Now we made the fetch with the URL and query strings created  
    fetch(finalURL, {
      method: 'GET'
    })
    .then(response => {
      if (!response.ok) {
        throw new Error("HTTP error, status = " + response.status);
      }
      // Check if content type of response is JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new TypeError("Oops, we haven't got JSON!");
      }
      // Nota que esta linea convierte el JSON a objetos javascript 
      // que se guardan en la variable data que se pasa en la siguiente
      // promesa
      return response.json();
    })
    // We use the data obtained in the fetch (JSON array) to show the 
    // list of movies 
    .then(data => {
      console.log('MOVIES DATA:', data);
      if (data.length === 0) {
        var listItem = document.createElement('li');
        listItem.innerHTML = '<h2 style="color:Red;text-align:center;">No results</h2>';
        myList.appendChild(listItem);       
      }
      // for every item in the JSON array we create a new item in the list
      for(var i = 0; i < data.length; i++) {
        var listItem = document.createElement('li');
        listItem.className = 'listItem';
        listItem.innerHTML = '<h2 style="color:Black">' + data[i].primaryTitle + '</h2>';
        listItem.innerHTML +='Year: ' + data[i].startYear;
        listItem.innerHTML +=' | Runtime in minutes: ' + data[i].runtimeMinutes;
        listItem.innerHTML +=' | Genres: ' + data[i].genres;
        listItem.innerHTML +=' | Rating: ' + data[i].averageRating;
        listItem.innerHTML += '<br><hr style="margin-top:10px"/>';
        myList.appendChild(listItem);
      }
      // This part is for the navigation controls
      // This is to create the space for the navigation controls
      var navControls = document.getElementById("navigation_controls");
      navControls.innerHTML = "";
      navControls.className = 'centered-item';
      // If we are showing the first page of results then we only show
      // the next control option
      if (data.length != 0) {
        if (pageNumber == 0) {
          var nextPage = document.createElement('span');
          nextPage.innerHTML = 'Next';
          nextPage.className = 'navigation-text';
          nextPage.onclick = () => {
            pageNumber++;
            fetchData(pageNumber)
          };
          navControls.appendChild(nextPage);
        } else {
          // ir a la pagina previa
          var previousPage = document.createElement('span');
          previousPage.innerHTML = 'Previous';
          previousPage.className = 'navigation-text';
          previousPage.onclick = () => {
            pageNumber--;
            fetchData(pageNumber)
          };
          navControls.appendChild(previousPage);
          // ir a la pagina siguiente
          var nextPage = document.createElement('span');
          nextPage.innerHTML = '&nbsp;|&nbsp;Next';
          nextPage.className = 'navigation-text';
          nextPage.onclick = () => {
            pageNumber++;
            fetchData(pageNumber);
          };
          navControls.appendChild(nextPage);
        }
      }
    })
    //////////////////////////////////////////////////////////
    // EN CASO DE ERROR
    .catch((error) => {
      console.error('Error:', error);
      var p = document.createElement('p');
      p.appendChild(document.createTextNode('Error: ' + error.message));
      document.body.insertBefore(p, myList);
    });
  }

}