== Purpose ==

This set of scripts copy and import the information about the Brazilian federal government
organizational structure, contained within the xml dump file at

http://repositorio.dados.gov.br/governo-politica/administracao-publica/estrutura-organizacional/

and saves it as a csv file in the [schema](http://data.okfn.org/data/okfn/public-bodies) used
by the [public bodies project](https://github.com/okfn/publicbodies).

== Dependencies ==

* lxml (also requires libxml, see [installation instructions](http://lxml.de/installation.html))
* nltk
* phonenumberslite

== Installation ==

Note: it's not necessary to install these scripts as a Python package. As long as your system
satisfies the dependencies described here, you can just run the scripts directly.

Install the system libraries for libxml2 and libxslt (required for lxml,
[see instructions](http://lxml.de/installation.html)).

Proceed to install the package in the usual Python way. That is, create an empty virtual
environment (install Python [virtualenv](http://virtualenv.readthedocs.org/en/latest/virtualenv.html)
if you haven't already):

```
$ virtualenv --no-site-packages pyenv
```

Then activate the environment and install the package from where you downloaded it:

```
$ source pyenv/bin/activate
(pyenv)$ pip install -e .
```

This should take care of the dependencies on other python packages.

== Usage ==

Fist you need to download the xml dump files to a local folder.

Then, run the command for conveting the data from xml to csv format.
For instructions on the converter script, try typing on a terminal

```
$ python xmltocsv.py

Usage: xmltocsv.py [filename] [outfile] [domainfilename]

    filename:    file containing the Brazilian government's SIORG xml dump
           outfile:  output csv filename (optional)
    domainfilename:  file containing domain table information (optional)
                     (note: both files can be obtained at the following URL)
                      http://repositorio.dados.gov.br/governo-politica/administracao-publica/estrutura-organizacional/
```

The first parameter after that is the name of the input xml file containing the data.

The second parameter is the output csv file.

The third parameter optionally reads the xml file containing domain information.
This is required if you want to fill the classification and tags fields.

== To do ==

* refactor to use the Python standard library instead of lxml to simplify installation
* refactor to some simpler slugging code not to require the whole nltk library
