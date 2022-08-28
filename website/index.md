---
published: true
permalink: /
layout: default
filename: index.md
ref: root
desc: An open database about every part of government.
---

<div class="row">
  <div class="span8" markdown="1">

# Jurisdictions

{% assign juris=site.jurisdictions %}
{% for jurisdiction in juris  %}
      
  <div class="row-fluid jurisdiction">
    <a href="{{ jurisdiction.key | relative_url }}">
      <div class="span5 title">{{ jurisdiction.name }}</div>
      <div class="span2 code">{{ jurisdiction.key }}</div>
      <div class="span3">{{ site.data[jurisdiction.key].size }} bodies</div>
    </a>
    <div class="span2 download">
      <a class="btn btn-inverse" href="https://github.com/okfn/publicbodies/raw/master/data/{{ jurisdiction.key }}.csv">
        <i class="icon-download-alt"> csv</i>
      </a>
    </div>
  </div>

{% endfor %}

  </div>
  <div class="span4 sidebar" markdown="1">

### Open Data [![This material is Open Data](https://assets.okfn.org/images/ok_buttons/od_80x15_blue.png)](https://opendefinition.org/)

This is all [open data](https://opendefinition.org/) licensed under the 
[Public Domain Dedication and License](https://opendatacommons.org/licenses/pddl/1.0/).
Please use and reuse freely.

### Contribute

Want to contribute (or just have a question)? Join the Open Knowledge Discuss forum and see the
[Open Knowledge Labs](https://discuss.okfn.org/c/open-knowledge-labs/34)
section.

Want to dive straight in? All the code *and* data are hosted in 
[this github repo](https://github.com/okfn/publicbodies)
and there's a list of [issues](https://github.com/okfn/publicbodies/issues)
where we need help!

  </div>
</div>
