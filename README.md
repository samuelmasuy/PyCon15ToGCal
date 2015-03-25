# PyCon15ToGCal

## Description

Command line application to port PyCon talks and keynotes events to
Google calendar.

## Installation

You will need to create a [project][gapi] on Google develloper console,
with the permission for calendar. The key and secret is necessary for
this application.

I strongly suggest you to create a [virtualenv][ve] for this project.
Then, providing you have pip installed on your machine,
use `pip install -r requirements.txt` to install the required modules.

## Running

```bash
    usage: pycon_schedule.py [-h] [-c CALENDAR] [-a] clientid clientsecret

    Port PyCon talks and keynotes to Google calendar.

    positional arguments:
      clientid         Get your client ID from Google developer console.
      clientsecret     Get your client secret from Google developer console.

    optional arguments:
      -h, --help       show this help message and exit
      -c CALENDAR, --calendar CALENDAR
                       Name of the secondary calendar you would like to port
                       the event to. If you would like it to be your primary
                       calendar, insert `primary`. (Default: `PyCon15`)
      -a, --all        Add all the events to your google calendar. The
                       default is a provides an interface to select talks and
                       keynotes. (Pick one talk per session.)
```

## Contribute

Found a bug? Have a good idea for improving this app?
If you'd like to contribute or extend this project:

1. Clone your fork.
1. Create a branch to contain your change.
1. Hack!
1. Document in a README your new functionalities.
1. Push the branch on GitHub.
1. Send a pull request to this project.

## License

GNU General Public License version 2.0
Please refer to [LICENSE](/LICENSE/).

[gapi]: https://developers.google.com/console/
[ve]: http://www.virtualenv.org/en/latest/virtualenv.html#installation
