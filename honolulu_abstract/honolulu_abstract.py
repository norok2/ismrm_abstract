#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test a markdown source for ISMRM abstracts submission constraints.

This is optimized for ISMRM 2017 abstracts.

Note: only Python is required, but optional features may be unavailable.
For colored messages, install the `blessed` or `blessings` Python package
(both are available through PyPI).
The export to HTML feature requires the `pandoc` binary.
The export to PDF feature requires both `pandoc` and `wkhtmltopdf` binaries.
The VCS capabilities are managed through `git`, which should be installed
and set up separately.
"""

#    Copyright (C) 2015 Riccardo Metere <metere@cbs.mpg.de>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# ======================================================================
# :: Future Imports
from __future__ import (
    division, absolute_import, print_function, unicode_literals)

try:
    from builtins import (
        bytes, dict, int, list, object, range, str, ascii, chr, hex, input,
        next, oct, open, pow, round, super, filter, map, zip)
except ImportError:
    pass

# ======================================================================
# :: Python Standard Library Imports
import os  # Miscellaneous operating system interfaces
import sys  # System-specific parameters and functions
import itertools  # Functions creating iterators for efficient looping
import functools  # Higher-order functions and operations on callable objects
import datetime  # Basic date and time types
import argparse  # Parser for command-line options, arguments and subcommands
import subprocess  # Subprocess management
import shlex  # Simple lexical analysis
import re  # Regular expression operations

# :: External Imports

# :: External Imports Submodules

# ======================================================================
# :: Version
__version__ = '0.1.0.0'

# ======================================================================
# :: Script details
INFO = {
    'name': 'ISMRM_abstract',
    'author': 'Riccardo Metere <metere@cbs.mpg.de>',
    'copyright': 'Copyright (C) 2016',
    'license': 'License: GNU General Public License version 3 (GPLv3)',
    'notice':
        """
This program is free software and it comes with ABSOLUTELY NO WARRANTY.
It is covered by the GNU General Public License version 3 (GPLv3).
You are welcome to redistribute it under its terms and conditions.
        """,
    'version': __version__
}

# ======================================================================
# :: supported verbosity levels
VERB_LVL_NAMES = (
    'none', 'lowest', 'lower', 'low', 'medium', 'high', 'higher', 'highest',
    'warning', 'debug')
VERB_LVL = {k: v for k, v in zip(VERB_LVL_NAMES, range(len(VERB_LVL_NAMES)))}
D_VERB_LVL = VERB_LVL['lowest']

# ======================================================================
# :: internals
D_SKIP_TOKENS = ('#', '!', '[')
D_HDR_TOKENS = tuple('#' * (n + 1) + ' ' for n in range(6))
D_HDR_TOKENS_NL = ('==', '--')
D_SKIP_SECTIONS = (
    'Authors',
    'Synopsis',
    'References',
    'Acknowledgements',
    'Figure',
    'Table')

# :: limits
D_LIMITS = dict((
    ('wc_tot', 750),  # Max word count in non-skip sectionscss
    ('wc_synopsis', 100),  # Max word count in synopsis
    ('wc_fig', 100),  # Max word count in figure captions
    ('n_figs', 5),  # Max number of figures
    ('fig_size', 2e6),  # Max figure size in bytes
))

# :: external tools
TOOLS = dict((
    ('md2html',
     'pandoc --standalone --mathjax --section-divs'
     ' {css_str} {self_contained_str} '
     ' --read markdown+tex_math_double_backslash --write html5'),
    ('html2pdf',
     'wkhtmltopdf --page-size A4 --margin-bottom 15mm --margin-left 15mm '
     '--margin-right 15mm --margin-top 15mm --javascript-delay 2000 '
     '--image-dpi {figs_dpi} {html_filepath} {pdf_filepath}'),
    ('vcs',
     'git commit -uno -a -m "Save before validation."')
))
_MD2HTML_MULTI_CSS = '--css='
D_LOG = '.{name}.{source}.log'

# :: gliph for marking
GLIPH = '⋆'

# :: the CSS to use
D_CSS = [
    'https://fonts.googleapis.com/css?family=Roboto:100,100i,300,300i,'
    '400|Roboto+Mono:100,100i,300,300i,400,400i']
D_CSS_FILEPATH = 'default.css'
D_CSS_FILECONTENT = \
    '/* automatically generate by `{__file__}` */'.format(**locals()) + '''
body {
    margin: 0ex auto 4ex;
    font: normal normal 300 12pt "Roboto", sans-serif; }
h1, h2, h3, h4, h5, h6 { margin: 0.8ex auto 0ex; clear: both; }
h1, h2, h3 { margin: 2ex auto 0ex; font-weight: 400; }
h1 { font-size: 140%; color: #336; margin: 1.6ex auto 0ex; }
h2 { font-size: 125%; color: #339; margin: 1.2ex auto 0ex; }
h3 { font-size: 110%; color: #33c; margin: 1.0ex auto 0ex; }
p { font-size: 100%; margin: 0.4ex auto 1ex; }
hr { clear: both; }
section { overflow: auto; margin: 0ex; padding; 0ex; }
img { max-width: 100%; max-height: 96vh; }

.red { color: red; }
.green { color: green; }

/* improved appearance */
#authors h2 { display: none; }
#authors { margin-top: 1ex; }
#authors > ol { font-size: 85%; }
#synopsis > p { font-weight: 400; }
#synopsis + section, #references, #figures, #test-results {
    margin-top: 2.0ex; }
#figures section h3 { margin: 0.4em auto 0em; }
#figures section { border-bottom: 1px solid #666; }
#figures section:first-of-type { border-top: 1px solid #666; }
#test-results > :not(h2) {
    font-family: "Roboto Mono", monospace; font-size: 80%; }
#test-results > ul { list-style-type: none; padding-left: 0ex; }
#test-results > p { text-align: center; font-size: 130%; }

@media print {
    body { max-width: 100%; font-size: 11pt; }
    h1, h2, h3, h4, h5, h6 {
        page-break-before: auto; page-break-after: avoid; }
    p, span { page-break-inside: avoid; page-break-after: auto; }
    table { page-break-inside: auto; }
    tr { page-break-inside: avoid; page-break-after: avoid; }
    tbody { page-break-inside: avoid; page-break-after: auto; }
    #test-results, #figures { page-break-before: always; }
    hr { visibility: hidden; }
    img { max-width: 515px; max-height: 205px; }
    #figures figure, #figures a {
        float: left; margin: 0.1em 1em 0em 0em; padding: 0em; }
    #figures h2 { margin: 0em auto 0.6em; }
    #figures h3 { margin: 0em auto 0.1em; }
}

@media screen {
    body { max-width: 95%; font-size: 11.5pt; }
    #test-results > :not(h2) { font-size: 1.65vw; }
    #figures, #test-results { margin-top: 1em; }
    #figures figure, #figures a {
        float: left; margin: 0.1em 1em 0em 0em; padding: 0em; }
    #figures p::before {
        content: ""; min-width: 12em; display: block; overflow: hidden;
        padding: 0ex; margin: 0ex; }
}

@media screen and (min-width: 800px) {
    body { max-width: 80%; }
    #test-results > :not(h2) { font-size: 1.55vw; }
}

@media screen and (min-width: 1000px) {
    body { max-width: 80%; }
    #test-results > :not(h2) { font-size: 90% }
}

@media screen and (min-width: 1200px) {
    body { max-width: 96%; }
    section .level2 { width: 65%; }
    #figures { width: 30%; position: absolute; top: 1.6em; left: 68%; }
    #figures section:last-of-type { border-bottom: none; }
}

@media screen and (min-width: 1600px) {
    body { font-size: 12.5pt; }
}
'''


# ======================================================================
def msg(
        text,
        verb_lvl=D_VERB_LVL,
        verb_threshold=D_VERB_LVL,
        fmt=None,
        *args,
        **kwargs):
    """
    Display a feedback message to the standard output.

    Args:
        text (any): Message to display.
        verb_lvl (int): Current level of verbosity.
        verb_threshold (int): Threshold level of verbosity.
        fmt (str): Format of the message (if `blessed` supported).
            If None, a standard formatting is used.
        *args (tuple): Positional arguments to be passed to `print`.
        **kwargs (dict): Keyword arguments to be passed to `print`.

    Returns:
        None.

    Examples:
        >>> s = 'Hello World!'
        >>> msg(s)
        Hello World!
        >>> msg(s, VERB_LVL['medium'], VERB_LVL['low'])
        Hello World!
        >>> msg(s, VERB_LVL['low'], VERB_LVL['medium'])  # no output
        >>> msg(s, fmt='{t.green}')  # if ANSI Terminal, green text
        Hello World!
        >>> msg('   :  a b c', fmt='{t.red}{}')  # if ANSI Terminal, red text
           :  a b c
        >>> msg(' : a b c', fmt='cyan')  # if ANSI Terminal, cyan text
         : a b c
    """
    if verb_lvl >= verb_threshold and text:
        # if blessed/blessings is not present, no coloring
        blessed = None
        try:
            import blessed
        except ImportError:
            try:
                import blessings as blessed
            except ImportError:
                blessed = None

        if blessed:
            t = blessed.Terminal()
            if not fmt:
                if VERB_LVL['low'] < verb_threshold <= VERB_LVL['medium']:
                    e = t.cyan
                elif VERB_LVL['medium'] < verb_threshold < VERB_LVL['debug']:
                    e = t.magenta
                elif verb_threshold >= VERB_LVL['debug']:
                    e = t.blue
                elif text.startswith('I:'):
                    e = t.green
                elif text.startswith('W:'):
                    e = t.yellow
                elif text.startswith('E:'):
                    e = t.red
                else:
                    e = t.white
                # first non-whitespace word
                txt1 = text.split(None, 1)[0]
                # initial whitespaces
                n = text.find(txt1)
                txt0 = text[:n]
                # rest
                txt2 = text[n + len(txt1):]
                txt_kwargs = {
                    'e1': e + (t.bold if e == t.white else ''),
                    'e2': e + (t.bold if e != t.white else ''),
                    't0': txt0, 't1': txt1, 't2': txt2, 'n': t.normal}
                text = '{t0}{e1}{t1}{n}{e2}{t2}{n}'.format(**txt_kwargs)
            else:
                if 't.' not in fmt:
                    fmt = '{{t.{}}}'.format(fmt)
                if '{}' not in fmt:
                    fmt += '{}'
                text = fmt.format(text, t=t) + t.normal
        print(text, *args, **kwargs)


# ======================================================================
def which(args):
    """
    Determine the full path of an executable, if possible.

    It mimics the behavior of the POSIX command `which`.

    Args:
        args (str|list[str]): Command to execute as a list of tokens.
            Optionally can accept a string which will be tokenized.

    Returns:
        args (list[str]): Command to execute as a list of tokens.
            The first item of the list is the full path of the executable.
            If the executable is not found in path, returns the first token of
            the input.
            Other items are identical to input, if the input was a str list.
            Otherwise it will be the tokenized version of the passed string,
            except for the first token.
        is_valid (bool): True if path of executable is found, False otherwise.
    """

    def is_executable(file_path):
        return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

    # ensure args in the correct format
    try:
        args = shlex.split(args)
    except AttributeError:
        pass

    cmd = args[0]
    dirpath, filename = os.path.split(cmd)
    if dirpath:
        is_valid = is_executable(cmd)
    else:
        is_valid = False
        for dirpath in os.environ['PATH'].split(os.pathsep):
            dirpath = dirpath.strip('"')
            tmp = os.path.join(dirpath, cmd)
            is_valid = is_executable(tmp)
            if is_valid:
                cmd = tmp
                break
    return [cmd] + args[1:], is_valid


# ======================================================================
def execute(
        args,
        in_pipe=None,
        mode='call',
        timeout=None,
        encoding='utf-8',
        log=None,
        dry=False,
        verbose=D_VERB_LVL):
    """
    Execute command and retrieve/print output at the end of execution.

    Args:
        args (str|list[str]): Command to execute as a list of tokens.
            Optionally can accept a string.
        in_pipe (str|None): Input data to be used as stdin of the process.
        mode (str): Set the execution mode (affects the return values).
            Allowed modes:
             - 'spawn': Spawn a new process. stdout and stderr will be lost.
             - 'call': Call new process and wait for execution.
                Once completed, obtain the return code, stdout, and stderr.
             - 'flush': Call new process and get stdout+stderr immediately.
                Once completed, obtain the return code.
                Unfortunately, there is no easy
        timeout (float): Timeout of the process in seconds.
        encoding (str): The encoding to use.
        log (str): The template filename to be used for logs.
            If None, no logs are produced.
        dry (bool): Print rather than execute the command (dry run).
        verbose (int): Set level of verbosity.

    Returns:
        ret_code (int|None): if mode not `spawn`, return code of the process.
        p_stdout (str|None): if mode not `spawn`, the stdout of the process.
        p_stderr (str|None): if mode is `call`, the stderr of the process.
    """
    ret_code, p_stdout, p_stderr = None, None, None

    args, is_valid = which(args)
    if is_valid:
        msg('{} {}'.format('$$' if dry else '>>', ' '.join(args)),
            verbose, D_VERB_LVL if dry else VERB_LVL['medium'])
    else:
        msg('W: `{}` is not in available in $PATH.'.format(args[0]))

    if not dry and is_valid:
        if in_pipe is not None:
            msg('< {}'.format(in_pipe),
                verbose, VERB_LVL['highest'])

        proc = subprocess.Popen(
            args,
            stdin=subprocess.PIPE if in_pipe and not mode == 'flush' else None,
            stdout=subprocess.PIPE if mode != 'spawn' else None,
            stderr=subprocess.PIPE if mode == 'call' else subprocess.STDOUT,
            shell=False)

        # handle stdout nd stderr
        if mode == 'flush' and not in_pipe:
            p_stdout = ''
            while proc.poll() is None:
                out_buff = proc.stdout.readline().decode(encoding)
                p_stdout += out_buff
                msg(out_buff, fmt='', end='')
                sys.stdout.flush()
            ret_code = proc.wait()
        elif mode == 'call':
            # try:
            p_stdout, p_stderr = proc.communicate(
                in_pipe.encode(encoding) if in_pipe else None)
            # except subprocess.TimeoutExpired:
            #     proc.kill()
            #     p_stdout, p_stderr = proc.communicate()
            p_stdout = p_stdout.decode(encoding)
            p_stderr = p_stderr.decode(encoding)
            if p_stdout:
                msg(p_stdout, verbose, VERB_LVL['high'], fmt='')
            if p_stderr:
                msg(p_stderr, verbose, VERB_LVL['high'], fmt='')
            ret_code = proc.wait()
        else:
            proc.kill()
            msg('E: mode `{}` and `in_pipe` not supported.'.format(mode))

        if log:
            name = os.path.basename(args[0])
            pid = proc.pid
            for stream, source in ((p_stdout, 'out'), (p_stderr, 'err')):
                if stream:
                    log_filepath = log.format(**locals())
                    with open(log_filepath, 'wb') as fileobj:
                        fileobj.write(stream.encode(encoding))
    return ret_code, p_stdout, p_stderr


# ======================================================================
def multi_replace(text, replaces):
    """
    Perform multiple replacements in a string.

    Args:
        text (str): The input string.
        replaces (tuple[str,str]): The listing of the replacements.
            Format: ((<old>, <new>), ...).

    Returns:
        text (str): The string after the performed replacements.

    Examples:
        >>> multi_replace('python.best', (('thon', 'mrt'), ('est', 'ase')))
        'pymrt.base'
        >>> multi_replace('x-x-x-x', (('x', 'est'), ('est', 'test')))
        'test-test-test-test'
        >>> multi_replace('x-x-', (('-x-', '.test'),))
        'x.test'
    """
    return functools.reduce(lambda s, r: s.replace(*r), replaces, text)


# ======================================================================
def check_redo(
        in_filepaths,
        out_filepaths,
        force=False):
    """
    Check if input files are newer than output files, to force calculation.

    Args:
        in_filepaths (iterable[str]): Input filepaths for computation.
        out_filepaths (iterable[str]): Output filepaths for computation.
        force (bool): Force computation to be re-done.

    Returns:
        force (bool): True if the computation is to be re-done.

    Raises:
        IndexError: If the input filepath list is empty.
        IOError: If any of the input files do not exist.
    """
    # todo: include output_dir autocreation
    # check if input is not empty
    if not in_filepaths:
        raise IndexError('List of input files is empty.')

    # check if input exists
    for in_filepath in in_filepaths:
        if not os.path.exists(in_filepath):
            raise IOError('Input file does not exists.')

    # check if output exists
    if not force:
        for out_filepath in out_filepaths:
            if out_filepath:
                if not os.path.exists(out_filepath):
                    force = True
                    break

    # check if input is older than output
    if not force:
        for in_filepath, out_filepath in \
                itertools.product(in_filepaths, out_filepaths):
            if in_filepath and out_filepath:
                if os.path.getmtime(in_filepath) \
                        > os.path.getmtime(out_filepath):
                    force = True
                    break
    return force


# ======================================================================
def word_count(
        in_filepath,
        skip_tokens=D_SKIP_TOKENS,
        hdr_tokens=D_HDR_TOKENS,
        hdr_tokens_nl=D_HDR_TOKENS_NL,
        skip_sections=(),
        encoding='utf-8'):
    """
    Calculate word count for each Markdown section.

    Args:
        in_filepath (str): The path to the input file.
        skip_tokens (iterable[str]): Skip token identifier.
            Ignore lines starting with any of the tokens indicated.
        hdr_tokens (iterable[str]): Header token identifier.
            Lines stating with any of the tokens are considered header.
        hdr_tokens_nl (iterable[str]): Header-after-new-line token identifier.
            Ignore lines immediately above and starting with any of the tokens
            indicated.
        skip_sections (iterable[str]): Skip from word count.
            The sections included in this list will not count toward the
            total word count.
        encoding (str): The encoding to use.

    Returns:
        blocks (list[dict]): A list of dicts containing section info.
            Each dict contains:
                - 'title': the section title as a text string.
                - 'level': level of heading (1 to 6).
                - 'text': the section text as a list of text string lines.
                - 'num_words': the number of words as int.
                - 'skip': False if block is skipped in partial counts.
        wc_partial (int): The partial number of words.
            Titles and sections to skip are not included.
        wc_total (int): The total number of words.
            Titles are excludes, sections to skip are included.
    """
    with open(in_filepath, 'rb') as i_file:
        blocks = []
        lines = []
        len_last_line = 0
        for line in i_file.read().decode(encoding).splitlines():
            for i, token in enumerate(hdr_tokens):
                if line.startswith(token):
                    if len(blocks) > 0:
                        blocks[-1]['text'] = lines
                        lines = []
                    blocks.append(
                        {'title': line[len(token):], 'text': [], 'level': i})
            skip_line = False
            for skip_token in skip_tokens:
                if line.startswith(skip_token):
                    skip_line = True
            if skip_line:
                continue
            was_title = False
            for i, token in enumerate(hdr_tokens_nl):
                if len(line) == len_last_line and line.startswith(token):
                    was_title = True
            if was_title:
                title = lines.pop()
                if len(blocks) > 0:
                    blocks[-1]['text'] = lines
                    lines = []
                blocks.append({'title': title, 'text': [], 'level': i})
            elif len(line) > 0:
                # print(':: ', line)  # DEBUG
                lines.append(line)
            len_last_line = len(line)
        if blocks:
            blocks[-1]['text'] = lines

    wc_partial = 0
    wc_total = 0
    for i, block in enumerate(blocks):
        blocks[i]['num_words'] = len(' '.join(block['text']).split())
        skip = False
        for skip_section in skip_sections:
            if skip_section in block['title']:
                skip = True
                break
        blocks[i]['skip'] = skip
        wc_partial += block['num_words'] if not skip else 0
        wc_total += block['num_words']

    return blocks, wc_partial, wc_total


# ======================================================================
def find_figures(
        in_filepath,
        on_new_lines=True,
        encoding='utf-8'):
    """
    Calculate word count for each Markdown section.

    Args:
        in_filepath (str): The path to the input file.
        on_new_lines (bool): Include only figures on a separate line.
        encoding (str): The encoding to use.

    Returns:
        figs (list[str]): The figures referenced in the text.
    """
    # fix patterns for newlines
    fix_nl = '^' if on_new_lines else ''
    # :: match referenced figures
    pattern_ref_uri = fix_nl + r'\[(?P<ref>[0-9]+)\]:(?P<uri>.*)'
    pattern_ref = fix_nl + r'\[!\[.*\]\[(?P<ref>[0-9]+)\]\]\[(?P=ref)\]'
    # :: match unreferenced figures
    pattern_uri = fix_nl + r'!\[.*\]\((?P<uri>.*)\)'

    figs = []
    fig_refs, fig_uris = {}, [],
    with open(in_filepath, 'rb') as i_file:
        for line in i_file.read().decode(encoding).splitlines():
            re_ref = re.match(pattern_ref, line)
            if re_ref:
                figs.append(re_ref.group('ref'))

            re_ref_uri = re.match(pattern_ref_uri, line)
            if re_ref_uri:
                fig_refs[re_ref_uri.group('ref')] = re_ref_uri.group('uri')

            re_uri = re.match(pattern_uri, line)
            if re_uri:
                fig_uris.append(re_uri.group('uri'))
                figs.append(fig_uris[-1])
    for i, fig in enumerate(figs):
        if fig in fig_refs:
            figs[i] = fig_refs[fig].strip()

    return figs


# ======================================================================
def fix(
        in_filepath,
        out_filepath=None,
        attachment=None,
        encoding='utf-8',
        out_fmt='fix_{in_filename}',
        force=False,
        verbose=D_VERB_LVL):
    """
    Substitute maths environment standard delimiters with custom defined ones.

    Args:
        in_filepath (str): The input filepath.
        out_filepath (str): The output filepath.
        attachment (str): The text to attach to the abstract.
        encoding (str): The encoding to use.
        out_fmt (str): The output format if out_filepath is None.
        force (bool): Force new processing.
        verbose (int):set the level of verbosity.

    Returns:
        None.
    """
    in_dirpath, in_filename = os.path.split(in_filepath)
    if not out_filepath:
        out_filepath = out_fmt.format(**locals())
    if os.path.dirname(out_filepath) == '':
        out_filepath = os.path.join(in_dirpath, out_filepath)

    if check_redo([in_filepath], [out_filepath], force):
        with open(in_filepath, 'rb') as i_file:
            stream = i_file.read().decode(encoding)
            i_file.close()

        replaces = (
            ('.\n\n', '.' + ' ' * 3 + '\n\n'),
            ('.\n', '.' + ' ' + '\n'),
            ('\\\\(', '$$$'), ('\\\\)', '$$$'),
            ('\\\\[', '$$'), ('\\\\]', '$$'),
        )
        stream = multi_replace(stream, replaces)

        if attachment:
            stream += '\n' + attachment + '\n'

        with open(out_filepath, 'wb') as o_file:
            o_file.write(stream.encode(encoding))
            o_file.close()
        msg('Output: {}'.format(out_filepath), verbose, VERB_LVL['lowest'])


# ======================================================================
def gen_report(
        lines,
        tests,
        title='Test Results',
        final='Final Result: {result}',
        hdr_style=+2,
        prefix='',
        suffix='',
        use_html=False):
    """
    Generate a report of the tests performed.

    Args:
        lines (list[str]): A list of text strings with description of tests.
            This is usually the same as displayed in the terminal.
        tests (list[bool]): A list of the results of all tests performed.
        title (str): The title to use for the section heading.
        final (str): The template string to use for the final test.
            This is OK only if all tests are OK.
        hdr_style (int): Determine the style of the header to use.
            A positive number will use '#'-style heading (valid: 1-6).
            A negative number will use underlined-style heading (valid: 1-2).
        prefix (str): String to attach to the report before its content.
        suffix (str): String to attach to the report after its content.
        use_html (bool): Insert HTML specific tags for improved export.

    Returns:
        text (str): The report as valid MarkDown (eventually HTML-enriched).
    """
    text = '\n' * 2
    # title
    if hdr_style > 0:
        i = hdr_style - 1
        text += str(D_HDR_TOKENS[i]) + title + '\n'
    elif hdr_style < 0:
        i = hdr_style + 1
        text += title + '\n'
        text += '-' * len(title) + '\n'
    else:
        text += title + '\n'
    # body
    if use_html:
        for line, test in zip(lines, tests):
            if test:
                attr = 'green'
            elif test is not None:
                attr = 'red'
            else:
                attr = ''
            text += '{}- <span class="{}">{}</span>{}\n'.format(
                prefix, attr, line.replace(' ', '&nbsp;'), suffix)
    else:
        text += '\n'.join([prefix + line + suffix for line in lines])
    text += '\n'
    # final result
    if lines:
        final_test = all([test for test in tests if test is not None])
        color = 'green' if final_test else 'red'
        result = 'OK' if final_test else 'ERR'
        text += '\n' + '-' * len(lines[-1]) + '\n'
        text += '<span class="{}">'.format(color) if use_html else ''
        text += '{:>{n}s}'.format(
            final.format(**locals()), n=len(lines[-1]) if not use_html else '')
        text += '</span>' if use_html else ''
    return text


# ======================================================================
def honolulu(
        in_filepath,
        out_filepath,
        export=('html', 'pdf'),
        attach=True,
        backup=True,
        log=True,
        css=None,
        self_contained=False,
        encoding='utf-8',
        figs_dpi=72,
        limits=D_LIMITS,
        force=False,
        verbose=D_VERB_LVL):
    """

    Args:
        in_filepath (str): The input filepath.
        out_filepath (str): The output filepath.
            If None, it will be computed from the input file.
        export (list[str]): The export format(s).
            Accepted values are: [html|pdf]
        attach (bool): Attach results to output/export file(s).
        backup (bool): Backups before processing.
        css (list[str]): Specify the CSS sources.
        self_contained (bool): Specify if HTML export is self-contained.
        figs_dpi (float): Resolution of the figures in exports.
        encoding (str): The encoding to use.
        limits (dict): Limits to be used for testing.
            Defaults to ISMRM 2017 Honolulu abstracts.
        force (bool): Force new processing.
        verbose (int):set the level of verbosity.

    Returns:
        None.
    """

    export = [s.lower() for s in export]

    def _test_pass(cond, text, test_list, attach_list):
        if cond:
            mode, res = 'I', 'OK'
        elif cond is None:
            mode, res = GLIPH, ' '
        else:
            mode, res = 'E', 'ERR'
        text = '{}: {:64} {:.>6s}'.format(mode, text, res)
        msg(text)
        test_list.append(cond)
        attach_list.append(text)

    tests = []
    attaches = []

    if os.path.isfile(in_filepath):
        in_filepath = os.path.realpath(in_filepath)
    elif os.path.isdir(in_filepath):
        dirpath = os.path.realpath(in_filepath)
        in_filepath = os.path.join(
            dirpath, os.path.basename(dirpath) + '.md')
    if not os.path.isfile(in_filepath):
        msg('File `{}` not found.'.format(in_filepath))
        exit(1)
    msg('Input: {}'.format(in_filepath))

    if backup:
        args, is_valid = which(TOOLS['vcs'].format(**locals()))
        ret_code, p_stdout, p_stderr = execute(
            args, log=D_LOG, verbose=verbose)
        if ret_code == 0:
            msg('I: Your VCS has been updated.')
        else:
            reason = '(Returned: {})'.format(ret_code) \
                if is_valid else '(`{}` not found)'.format(args[0])
            msg('W: VCS backup failed {}.'.format(reason))

    # :: word count
    blocks, num_words_total, num_words_full = word_count(
        in_filepath, skip_sections=D_SKIP_SECTIONS, encoding=encoding)

    txt = '{:<48s}  {:>18s}'.format(
        'Word Count Total ({})'.format(GLIPH),
        '{:>8} / {:<7}'.format(num_words_total, limits['wc_tot']))
    _test_pass(num_words_total <= limits['wc_tot'], txt, tests, attaches)

    num_figure_captions = 0
    for block in blocks:
        if block['num_words']:
            gliph, limit, condition = '', 0, None
            if block['title'] == 'Synopsis':
                condition = block['num_words'] <= limits['wc_synopsis']
                limit = limits['wc_synopsis']
            elif block['title'].startswith('Figure'):
                num_figure_captions += 1
                condition = block['num_words'] <= limits['wc_fig']
                limit = limits['wc_fig']
            elif not block['skip']:
                gliph = limit = GLIPH
            txt = '{:<48s}  {:>18s}'.format(
                'Word Count: {}{}'.format(block['title'], gliph),
                '{:>8} / {:<7}'.format(
                    block['num_words'], limit))
            _test_pass(condition, txt, tests, attaches)

    figs = find_figures(in_filepath, encoding=encoding)
    figs_caps = [(len(figs), 'figures'), (num_figure_captions, 'captions')]
    for n, label in figs_caps:
        txt = '{:<48s}  {:>18s}'.format(
            'Number of {}'.format(label),
            '{:>8} / {:<7}'.format(n, limits['n_figs']))
        _test_pass(n <= limits['n_figs'], txt, tests, attaches)
    txt = ''.format('Matching number of figures and captions...')
    txt = '{:<48s}  {:>18s}'.format(
        'Matching number of figures and captions',
        '{:>8} {} {:<7}'.format(
            len(figs), '=' if len(figs) == num_figure_captions else '≠',
            num_figure_captions))
    _test_pass(len(figs) == num_figure_captions, txt, tests, attaches)

    for fig in figs:
        fig_filepath = os.path.expanduser(os.path.realpath(fig))
        if os.path.isfile(fig_filepath):
            fig_size = os.path.getsize(fig_filepath)
            txt_fig = '{:>8} / {:<7}'.format(
                *['{:.1f} {}'.format(n / 1e6, 'MB')
                  for n in (fig_size, limits['fig_size'])])
        else:
            fig_size = -1
            txt_fig = 'NOT FOUND!'
        txt = '{:<48s}  {:>18s}'.format('"{:s}"'.format(fig[:46]), txt_fig)
        _test_pass(0 <= fig_size <= limits['fig_size'], txt, tests,
                   attaches)

    # :: generate fixed version
    fix(in_filepath, out_filepath, gen_report(attaches, tests), encoding,
        force=force, verbose=verbose)

    # :: export to HTML and PDF
    if 'html' in export or 'pdf' in export:
        if css is None:
            if check_redo([__file__], [D_CSS_FILEPATH], force):
                with open(D_CSS_FILEPATH, 'wb') as fileobj:
                    fileobj.write(D_CSS_FILECONTENT.encode(encoding))
                msg('W: CSS `{}` may have been overwritten.'.format(
                    D_CSS_FILEPATH))
            css = D_CSS + \
                  [D_CSS_FILEPATH] if D_CSS_FILEPATH not in D_CSS else []
        css_str = ' '.join([_MD2HTML_MULTI_CSS + item for item in css])
        msg('CSS: {}'.format(css))

        html_filepath = os.path.splitext(in_filepath)[0] + '.html'
        self_contained_str = '--self-contained' if self_contained else ''
        if check_redo([in_filepath, __file__], [html_filepath], force):
            with open(in_filepath, 'rb') as fileobj:
                in_pipe = fileobj.read().decode(encoding)
            in_pipe += gen_report(attaches, tests, use_html=True)
            args, is_valid = which(TOOLS['md2html'].format(**locals()))
            if is_valid:
                ret_code, p_stdout, p_stderr = execute(
                    args, in_pipe, log=D_LOG, verbose=verbose)
                with open(html_filepath, 'wb') as fileobj:
                    fileobj.write(p_stdout.encode(encoding))
                msg('HTML: {}'.format(html_filepath))
            else:
                msg('W: cannot export HTML without `{}`.'.format(args[0]))

        # export to PDF
        if 'pdf' in export:
            pdf_filepath = os.path.splitext(in_filepath)[0] + '.pdf'
            in_filepaths = [html_filepath, __file__] + \
                           [item for item in css if not '://' in item]
            out_filepaths = [pdf_filepath]
            if check_redo(in_filepaths, out_filepaths, force):
                args, is_valid = which(TOOLS['html2pdf'].format(**locals()))
                if is_valid:
                    ret_code, p_stdout, p_stderr = execute(
                        args, log=D_LOG, verbose=verbose)
                    msg('PDF: {}'.format(pdf_filepath))
                else:
                    msg('W: cannot export PDF without `{}`.'.format(args[0]))

    if not all([test for test in tests if test is not None]):
        msg('WARNING! SOME TESTS HAVE FAILED!')


# ======================================================================
def handle_arg():
    """
    Handle command-line application arguments.
    """
    # :: Create Argument Parser
    arg_parser = argparse.ArgumentParser(
        description=__doc__,
        epilog='v.{} - {}\n{}'.format(
            INFO['version'], INFO['author'], INFO['license']),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # :: Add POSIX standard arguments
    arg_parser.add_argument(
        '--ver', '--version',
        version='%(prog)s - ver. {}\n{}\n{} {}\n{}'.format(
            INFO['version'],
            next(line for line in __doc__.splitlines() if line),
            INFO['copyright'], INFO['author'], INFO['notice']),
        action='version')
    arg_parser.add_argument(
        '-v', '--verbose',
        action='count', default=D_VERB_LVL,
        help='increase the level of verbosity [%(default)s]')
    arg_parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='override verbosity settings to suppress output [%(default)s]')
    # :: Add additional arguments
    arg_parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='force new processing [%(default)s]')
    arg_parser.add_argument(
        '-i', '--in_filepath', metavar='DIR',
        default=os.path.realpath(os.path.curdir),
        help='set input filepath [%(default)s]')
    arg_parser.add_argument(
        '-o', '--out_filepath', metavar='DIR',
        default=None,
        help='set output filepath [%(default)s]')
    arg_parser.add_argument(
        '-x', '--export', metavar='EXT',
        nargs='*',
        default=('html', 'pdf'),
        help='set export format(s) [%(default)s]')
    arg_parser.add_argument(
        '-a', '--attach',
        action='store_false',
        help='toggle attach results to output/export file(s) [%(default)s]')
    arg_parser.add_argument(
        '-b', '--backup',
        action='store_false',
        help='toggle backups before processing [%(default)s]')
    arg_parser.add_argument(
        '-l', '--log',
        action='store_false',
        help='toggle log of external tools [%(default)s]')
    arg_parser.add_argument(
        '-c', '--css',
        default=None,
        help='specify the CSS to use for HTML/PDF export [%(default)s]')
    arg_parser.add_argument(
        '-s', '--self-contained',
        action='store_true',
        help='toggle if HTML export should be self contained [%(default)s]')
    arg_parser.add_argument(
        '-e', '--encoding', metavar='ENCODING',
        default='utf-8',
        help='set the encoding to use [%(default)s]')
    return arg_parser


# ======================================================================
def main():
    # :: handle program parameters
    arg_parser = handle_arg()
    args = arg_parser.parse_args()
    # fix verbosity in case of 'quiet'
    if args.quiet:
        args.verbose = VERB_LVL['none']
    # print help info
    if args.verbose >= VERB_LVL['debug']:
        arg_parser.print_help()
    msg('\nARGS: ' + str(vars(args)), args.verbose, VERB_LVL['debug'])
    msg(__doc__.strip(), args.verbose, VERB_LVL['lower'])

    begin_time = datetime.datetime.now()

    kws = vars(args)
    kws.pop('quiet')
    honolulu(**kws)

    exec_time = datetime.datetime.now() - begin_time
    msg('ExecTime: {}'.format(exec_time), args.verbose, VERB_LVL['debug'])


# ======================================================================
if __name__ == '__main__':
    main()
