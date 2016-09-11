INSTALLATION INSTRUCTIONS
=========================

Pre-requisites
--------------
- Python 2.7+ or Python 3.3+ (recommended)


Optional Requirements
---------------------
- python/blessed or python/blessings (for colored terminal output)
- Pandoc (for HTML/PDF export)
- wkhtmltopdf (for PDF export)
- git (for backups)


Installation
------------
- copy the script `honolulu_abstract.py` into a folder
- run it
- (optionally make sure that the folder is in your $PATH)


Optional Installation 
---------------------

### pandoc
See the [official documentation](http://www.pandoc.org/installing.html)

### wkhtmltopdf
See the [official documentation](http://wkhtmltopdf.org/downloads.html)

### git
See the [official documentation](https://git-scm.com/downloads) for installing `git`.

Then, for a quickstart, move to the directory where your source markdown file, e.g. `abstract.md`, is located.
Run the following:

~~~bash
    git init
    git add abstract.md
~~~

...and you are done. The script will take care of the rest.
