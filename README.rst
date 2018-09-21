===============================================================================
Tinycal
===============================================================================
A Python implementation of ``cal`` command.


Story
-------------------------------------------------------------------------------
My Mac has a built-in ``cal`` command, but it has no color at all.
It's hard to see which day is today.

I found the other ``cal`` implementation in a single C file.
After modify it's source code a little bit, I was able to build it.

And it worked for a long period of time.

One day I need to know the week number of a day.
But ``cal`` didn't provide such argument, so I have to flip my badge over and
over again.

"NO, we RD exists to solve problems! At least our own problems..."

Here comes tinycal.


Installation
-------------------------------------------------------------------------------
::

  $ pip install --upgrade tinycal

Or, if you don't have access to PyPI, there are two ways to install it by hand.

1.  Single file solution

    (a) Copy ``tinycal/tcal.py`` into ``~/bin/``
    (b) Rename it to ``tcal``.
    (c) ``chmod 755 tcal``.

2.  Whole folder solution

    (a) Put the repository into your favorite folder, like ``~/bin/tinycal/``
    (b) Put a shell script into ``~/bin/``, named ``tcal`` ::

          #!/usr/bin/env sh
          cd ~/bin/tinycal/ && python -m tinycal "$@"

Make sure ``~/bin/`` is in your ``$PATH``.

It's just an example, you can decide which place to put.


Usage
-------------------------------------------------------------------------------
tinycal comes with a command utility ``tcal``.
It's command line argument design is mostly based on traditional ``cal``.

A snapshot of help page here:

::

  usage: tcal [-h] [--col COL] [-A AFTER] [-B BEFORE] [-3] [-w] [-W] [-s] [-S]
              [-b] [-nb] [-f] [-F] [-c] [-C] [-l {jp,zh,en}] [-j] [-z] [-e] [-m]
              [-M]
              [year] [month]

  tinycal: A Python implementation of cal utility.

  positional arguments:
    year                  Year to display.
    month                 Month to display. Must specified after year.

  optional arguments:
    -h, --help            show this help message and exit
    --col COL             Specify the column numbers.
    -A AFTER              Display the number of months after the current month.
    -B BEFORE             Display the number of months before the current month.
    -3                    Equals to -A 1 -B 1.
    -w                    Display week number.
    -W                    Don`t display week number.
    -s, --sep             Display separation lines.
    -S, --no-sep          Don`t display separation lines.
    -b, --border          Display border lines.
    -nb, --no-border      Don`t display border lines.
    -f, --fill            Fill every month into rectangle with previous/next month dates.
    -F, --no-fill         Don`t fill month into rectangle.
    -c                    Enable VT100 color output.
    -C                    Disable VT100 color output.
    -l {jp,zh,en}, --lang {jp,zh,en}
                          Select the language used to display weekday.
    -j                    Enable Japanese weekday names, equals to --lang=jp.
    -z                    Enable Chinese weekday names, equals to --lang=zh.
    -e                    Enable Chinese weekday names, equals to --lang=en.
    -m                    Use Monday as first weekday.
    -M                    Use Sunday as first weekday.

  Configuration files:
  1st: ~/.config/calrc
  2nd: ~/.calrc

Example usage:

..  image:: screenshot.png


Configuration File
-------------------------------------------------------------------------------
Hey, you still reading :D

tinycal finds its configuration file in this order:

1.  ``~/.config/calrc``
2.  ``~/.calrc``

Here is the full set of configurable options, with default values:

::

  col = 3
  after = 0
  before = 0
  wk = false
  sep = true
  fill = false
  border = true
  start_monday = false
  lang = en

  wk.color = BLACK
  fill.color = BLACK
  title.color = none:none
  weekday.color = none:none
  weekday.sunday.color = none:none
  weekday.monday.color = none:none
  weekday.tuesday.color = none:none
  weekday.wednesday.color = none:none
  weekday.thursday.color = none:none
  weekday.friday.color = none:none
  weekday.saturday.color = none:none
  sunday.color = none:none
  monday.color = none:none
  tuesday.color = none:none
  wednesday.color = none:none
  thursday.color = none:none
  friday.color = none:none
  saturday.color = none:none
  today.color = none:white

The ordering is not important.

For color settings, use ``foreground:background`` format to describe colors.

Recognized colors: ``black``, ``red``, ``green``, ``yellow``, ``blue``, ``magenta``, ``cyan``, ``white``.

If every letter in foreground is capitalized, the color will be bright.

Several color configuration may refer to the same day (like today & saturday).
The more specific setting overrides the other.

For example, this configuration:

::

  col = 5
  sep = true
  wk = true
  border = true
  fill = true

  title.color = black:cyan
  wk.color = black:white
  today.color = RED
  weekday.color = YELLOW
  weekday.sunday.color = GREEN
  weekday.saturday.color = GREEN

looks like this:

..  image:: screenshot-config-example.png

If it looks ugly, I'm sorry :(

But you can design your own configuration anyway :)


License
-------------------------------------------------------------------------------
This software is released under 2-clause BSD license, please refer to LICENSE.txt.
