(function() {
  var BASE_URL = '/search/'
  var idx = createSearchIndex()
  window.searchFormSubmitted = searchFormSubmitted
  window.addEventListener('popstate', urlChanged)
  onPageLoad()

  function onPageLoad() {
    urlChanged()
    document.getElementById('search-box').focus()
  }

  function urlChanged() {
    var searchTerm = getQueryVariable('q')
    doSearch(searchTerm)
  }

  function searchFormSubmitted() {
    var searchTerm = document.getElementById('search-box').value
    doSearch(searchTerm)
    return false
  }

  function createSearchIndex() {
    return lunr(function () {
      this.field('id')
      this.field('title', { boost: 10 })
      this.field('content')
      this.metadataWhitelist.push('position')

      for (var key in window.episodeStore) { // Add the data to lunr
        var post = window.episodeStore[key]
        this.add({
          'id': key,
          'title': post.title,
          'author': post.author,
          'category': post.category,
          'content': post.content
        }, this)
      }
    })
  }

  function getQueryVariable(variable) {
    var query = window.location.search.substring(1)
    var vars = query.split('&')
  
    for (var i = 0; i < vars.length; i++) {
      var pair = vars[i].split('=')
  
      if (pair[0] === variable) {
        return decodeURIComponent(pair[1].replace(/\+/g, '%20'))
      }
    }
  }
  
  function displaySearchResults(episodes, episodeStore) {
    var summaryLabel = document.getElementById('search-results-summary')
    var resultList = document.getElementById('search-results')
  
    var summaryHtml = 'No results found'
    var listHtml = ''

    var converter = new showdown.Converter();
    if (episodes.length > 0) {
      summaryHtml = 'Found ' + episodes.length + ' episode' + (episodes.length > 1 ? 's' : '') + ':'
      for (var i=0; i<episodes.length; i++) {
        var episode = episodes[i]
        listHtml += '<li>'
        listHtml += '  <a href="' + episode.url + '"><h3>' + episode.title + '</h3></a>'
        listHtml += '  <p>' + converter.makeHtml(episode.highlightedContent) + '</p>'
        listHtml += '</li>'
      }
    }
  
    summaryLabel.innerHTML = summaryHtml
    resultList.innerHTML = listHtml
  }
  
  function doSearch(originalSearch) {
    if (!originalSearch || !originalSearch.trim()) {
      originalSearch = ''
    }

    var searchBox = document.getElementById('search-box')
    searchBox.value = originalSearch
    searchBox.blur()

    if (originalSearch) {
      var lunrSearchString = createLunrSearchTerms(originalSearch)
      var searchResults = idx.search(lunrSearchString)
      var episodes = searchResults.map(function(result) {
        var episode = episodeStore[result.ref]
        Object.keys(result.matchData.metadata).forEach(function(term) {
          var contentMetadata = result.matchData.metadata[term].content
          if (contentMetadata && contentMetadata.position) {
            var positions = contentMetadata.position
            episode.highlightedContent = createHighlightedContent(episode.content, positions)
          } else {
            episode.highlightedContent = episode.content.slice(0, 150) + '...'
          }
        })
        return episode
      })

      updateQueryString(originalSearch)
      displaySearchResults(episodes, window.episodeStore)
    }
  }

  function createHighlightedContent(content, positions) {
    var highlightedContent = content;
    for (var i=positions.length-1; i>=0; i--) {
      var position = positions[i]
      var start = position[0]
      var end = start + position[1]
      highlightedContent = 
        highlightedContent.slice(0, start) + 
        '<span class="search-result-highlight">' +
        highlightedContent.slice(start, end) + 
        '</span> ' +
        highlightedContent.slice(end+1, highlightedContent.length)
    }

    if (positions.length > 0) {
      var firstPosition = positions[0]
      var start = firstPosition[0]
      if (start > 50) {
        highlightedContent = '...'  + highlightedContent.slice(start-50)
      }

      var end = highlightedContent.lastIndexOf('</span>')
      if (highlightedContent.length - end > 50) {
        highlightedContent = highlightedContent.slice(0, end + 50) + '...'
      }
    }

    return highlightedContent
  }

  function createLunrSearchTerms(originalSearch) {
    // Prefix all terms with "+" to perform a logical AND (unless they already have a prefix):
    return originalSearch
      .trim()
      .split(/\s+/)
      .map(function(term) {
        if (term.startsWith('+') || term.startsWith('~')) {
          return term
        } else {
          return '+' + term
        }
      })
      .join(' ')
  }

  function updateQueryString(searchTerm) {
    var currentUrl = window.location.pathname + window.location.search
    var newUrl = BASE_URL + '?q=' + searchTerm
    if (newUrl != currentUrl) {
      history.pushState({}, null, newUrl)
    }
  }

})()
