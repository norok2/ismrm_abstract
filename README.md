Honolulu Abstract
=================

...or...

How to manage your ISMRM abstract offline and live happier ever since (Honolulu/2017 edition)
=============================================================================================

by [Riccardo Metere](mailto:metere@cbs.mpg.de)


## Introduction
This short project consist mainly of the `honolulu_abstract.py` Python script, which aims at providing a viable way of writing offline and sharing your abstracts for the ISMRM annual meeting and exhibition 2017 in Honolulu. Technically, the tool checks the limits suggested/imposed by the submission system in a source file written with a subset of MarkDown (with the double backslash convention for mathematical elements). The appearance of the document can be tweaked through CSS.


## honolulu_abstract.py
The ISMRM electronic submission system is not ideal under a variety of situations, including e.g. poor user interface (UI), intermittent internet connection, multiple writing iterations with coauthors, etc.
For this reasons, some mechanisms to read/write/share your abstract without this limitation may be desireable. By using a combination of open source software, i.e. [Python](https://www.python.org) (easily obtainable with [Anaconda](https://www.continuum.io/)), [pandoc](http://pandoc.org), [wkhtmltopdf](http://wkhtmltopdf.org), [git](https://git-scm.com) and your favorite text editor, like [kate](https://kate-editor.org) or [Atom](https://atom.io/)) it is possible to achieve a reasonable pipeline that can output HTML or PDF documents to be shared with your coauthors or for archiving purposes. Unfortunately, due to the limitations of the UI provided, it is not possible to retain formatting through clipboard actions (i.e. `copy`/`paste` will not store formatting information). This means that if you use **ANY** editor except for the one provided by the submission system you must manually adjust the following text formatting:

- new lines
- **bold** or __strong__,
- *italic* or _slanted_
- <u>underline</u>
- super<sup>script</sup>
- sub<sub>script</sub>

Fortunately, this formatting is (or should be) seldom used in such documents and it is sensible to adjust a reduced number of items upon submission. Note that HTML code, which is usually valid to insert in MarkDown, is inserted verbatim by the submission system, so pay extra attention to strip it from your abstract if you plan to use it in the first place.

### Mathematical Formulae

To properly deal with mathematical formulae it is possible to use the so called *double backslash* MarkDown extension. This means that mathematical formulae can be written using standard [LaTeX](https://www.latex-project.org/) like \\(\LaTeX\\) and will be beautifully rendered by [MathJax](https://www.mathjax.org/). Therefore, to write mathematical equations you should use: `\\(` and `\\)` for inline math elements like \\(T_1\\) or \\(T_2^*\\), or `\\[` and `\\]` for display math elements like:
\\[S\propto V M_0\mathrm{e}^{-{T_E}/{T_2^*}}\sin{\alpha}\frac{1-\mathrm{e}^{-{T_R}/{T_1}}}{1-\cos{\alpha}\mathrm{e}^{-{T_R}/{T_1}}}\\]

Please note that for the purpose of submission a custom notation is suggested, making use of `$$` and `$$$` symbols for delimiting display and inline math environments, respectively. The preview system actually also recognize the standard *single backslash* MarkDown extension, but for some reasons this method seems to be deprecated. The *double backslash* notation has been adopted by this script in the hope that any eventual inaccuracies related to this approach will not go unnoticed at the time of submission.

### Figures and Tables

Figures should be included with a line starting with `![]`, followed by their path between parenthesis, e.g. `(path/to/figure.png)`. The resulting figure link reads: `![](path/to/figure.png)`.
Alternatively, if a link to the figure in the HTML is desired, the following notation should be used (`1` should be a number and should different for each figures):

    [1]:path/to/figure.png
    [![][1]][1]

A blank like should be separated the figure links and their caption (for improved source readability).
Since there is no automatic way of reference your figures, you should manually maintain their labels in the caption.
There is no specific limitation to the allowed file formats from this script, but submission system requires 'BMP, GIF, JPEG, JPG, or PNG'. The preferred image file format is PNG, or JPG (only for very large pictures where negligible thin elements).
If unsure, use PNG.

Tables should be also included as figures. Please use the same heading as for figures in this document. The label in the caption should probably be kept consistent with figures.

If you have not yet enough motivation to submit your brand new research, have a look at the nice pictures in the template document!

### Side Notes

As a side note, I would have liked to have a submission sistem working more like this script (i.e. with a predictable behavior and with copy/paste capabilities) rather than that half-way WYSIWYG user-interface provided.
Incidentally, this is also pretty easy to implement, the offline version being more or less in place, which is relatively straightforward to implement for online use.
If other (enough) people feel the same, we could probably put some pressure to have it this way.

    If you have any question, please feel free to contact me.


## Technical Specification
The script expects an input file formatted as MarkDown (+double-backslash extension) and outputs a *fixed version* of the file which contain a new section (*Summary of Results*) with the results of checking against the ISMRM abstract limits.
The *Summary of Results* is also printed to the terminal (eventually colored, a dark background is expected/recommended).
To run this script only Python (preferably 3.5) is required, but the optional export  features will be unavailable.
For colored messages in the terminal, install the [blessed](https://pypi.python.org/pypi/blessed) or [blessings](https://pypi.python.org/pypi/blessings) Python package (both are available through PyPI and therefore `pip`-installable).
The export to HTML feature requires the [pandoc](http://pandoc.org/installing.html) binary.
The export to PDF feature requires both [pandoc](http://pandoc.org/installing.html) and [wkhtmltopdf](http://wkhtmltopdf.org/downloads.html) binaries.
The VCS capabilities are managed through [git](https://git-scm.com/downloads), which should be installed
and set up separately.
Additional automation may be obtained with [GNU Make](https://www.gnu.org/software/make/), for example for automatically running the plotting scripts, converting `svg` diagrams to `png`, running this script, etc.


## Explanation of 'Summary of Results'
Each line consist of an item (e.g. word count or file size) followed by the numeric result of the analysis, \\(x\\) and the corresponding limit \\(x_\mathrm{Max}\\) separated by a `/`, i.e. \\(x/x_\mathrm{Max}\\).
Items subject to limitations are colored in <span class="green">green</span> and end with `OK`, or in <span class="red">red</span> and end with `ERR`, depending on whether the limits are respected or exceeded, respectively. Non-colored items are either not subject to limitations (if the corresponding limit is equal to 0) or they contribute to the items whose name end with a gliph in parenthesis (if the corresponding limit is equal to the the same gliph).
Please refer to the command-line help, the in-code documentation or the source code itself for further reference.


## Writing Style
To keep your MarkDown source clean, it is recommended to make a wise use of new lines and text editor capabilities. Particularly, a dynamic word wrapping feature is of great help in maintaining long lines without the need to manually deal with unwanted new lines as result of unforeseen edits. Feel free to use the provided template.

Additionally, keep in mind the recommendation from the ISMRM are reported below.:

- [How to submit your HTML-based abstract](http://www.ismrm.org/2017-annual-meeting-exhibition/2017-call-for-abstracts/how-to-submit-your-html-based-abstract/)
- [2017 Call for Abstracts](http://www.ismrm.org/2017-annual-meeting-exhibition/2017-call-for-abstracts/)

for further information.
