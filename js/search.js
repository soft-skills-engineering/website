(function() {
  var idx = createSearchIndex();
  window.searchFormSubmitted = searchFormSubmitted;
  window.addEventListener('popstate', urlChanged);
  urlChanged()
  /*
  var searchTerm = getQueryVariable('q');
  if (searchTerm) {
    document.getElementById('search-box').setAttribute("value", searchTerm)
    doSearch(searchTerm)
  }
  */

  function urlChanged() {
    console.log("urlChanged:", window.location.pathname + window.location.search)
    var searchTerm = getQueryVariable('q');
    doSearch(searchTerm)
  }

  function searchFormSubmitted() {
    var searchTerm = document.getElementById('search-box').value
    doSearch(searchTerm)
    return false
  }

  function createSearchIndex() {
    return lunr(function () {
      this.field('id');
      this.field('title', { boost: 10 });
      this.field('author');
      this.field('category');
      this.field('content');

      for (var key in window.postStore) { // Add the data to lunr
        var post = window.postStore[key];
        this.add({
          'id': key,
          'title': post.title,
          'author': post.author,
          'category': post.category,
          'content': post.content
        }, this);
      }
    });
  }

  function getQueryVariable(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split('&');
  
    for (var i = 0; i < vars.length; i++) {
      var pair = vars[i].split('=');
  
      if (pair[0] === variable) {
        return decodeURIComponent(pair[1].replace(/\+/g, '%20'));
      }
    }
  }
  
  function displaySearchResults(results, postStore) {
    console.log("displaySearchResults", results.length)
    var resultList = document.getElementById('search-results');

    document.getElementById('search-results-summary').innerHTML = 
        results.length > 0
          ? 'Found ' + results.length + ' episodes:'
          : ''
  
    var resultsHtml = '<li>No results found</li>'
    if (results.length > 0) {
      resultsHtml = ''
      for (var i=0; i<results.length; i++) {
        var post = postStore[results[i].ref];
        resultsHtml += '<li>'
        resultsHtml += '  <a href="' + post.url + '"><h3>' + post.title + '</h3></a>'
        resultsHtml += '  <p>' + post.content + '</p>'
        resultsHtml += '</li>'
      }
    }
  
    resultList.innerHTML = resultsHtml;
  }
  
  function doSearch(searchTerm) {
    if (!searchTerm || !searchTerm.trim()) {
      searchTerm = ''
    }

    var searchBox = document.getElementById('search-box')
    searchBox.value = searchTerm
    searchBox.blur()

    if (searchTerm) {
      var results = idx.search(searchTerm)
      updateQueryString(searchTerm)
      displaySearchResults(results, window.postStore)
    } else {
      document.getElementById('search-results').innerHTML = ''
      document.getElementById('search-results-summary').innerHTML = ''
    }
  }

  function updateQueryString(searchTerm) {
    var currentUrl = window.location.pathname + window.location.search
    var newUrl = "/search/?q=" + searchTerm
    if (newUrl != currentUrl) {
      console.log("Updating history")
      history.pushState({}, null, newUrl);
    } else {
      console.log("Not updating history")
    }
  }

})();
