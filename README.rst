===============================================================================
Tiny-cal
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

Here comes tiny-cal.


Usage
-------------------------------------------------------------------------------
tiny-cal comes with a command utility ``tcal``.
It's command line argument design is mostly based on traditional ``cal``.

A snapshot of help page here:

::

  $ python tcal.py -h
  usage: tcal.py [-h] [--col COL] [-A AFTER] [-B BEFORE] [-3] [-w] [-W] [-s]
                 [-S] [-b] [-nb] [-f] [-F] [-c] [-C] [-j] [-J] [-m] [-M]
                 [year] [month]

  Tiny cal

  positional arguments:
    year              Year to display.
    month             Month to display. Must specified after year.

  optional arguments:
    -h, --help        show this help message and exit
    --col COL         Specify the column numbers.
    -A AFTER          Display the number of months after the current month.
    -B BEFORE         Display the number of months before the current month.
    -3                Equals to -A 1 -B 1.
    -w                Display week number.
    -W                Don`t display week number.
    -s, --sep         Display separation lines.
    -S, --no-sep      Don`t display separation lines.
    -b, --border      Display border lines.
    -nb, --no-border  Don`t display border lines.
    -f, --fill        Fill every month into rectangle with previous/next month
                      dates.
    -F, --no-fill     Don`t fill month into rectangle.
    -c                Enable VT100 color output.
    -C                Disable VT100 color output.
    -j                Enable Japanese weekday names.
    -J                Disable Japanese weekday names.
    -m                Use Monday as first weekday.
    -M                Use Sunday as first weekday.

Example usage:

..  image:: screenshot.png
