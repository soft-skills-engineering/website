---
layout: page
title: Episodes
permalink: /episodes/
---

<ul>
{% for post in site.posts %}
  <li>

    <h2 class="post-list-header">
      <a class="post-link" href="{{ post.url | prepend: site.baseurl }}">{{ post.title }}</a>
    </h2>
    <span class="post-meta">{{ post.date | date: "%b %-d, %Y" }}</span>
  </li>
{% endfor %}
</ul>
