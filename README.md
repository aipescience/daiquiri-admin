Daiquiri Admin
==============

Daiquiri Admin is a python library meant to be used with the Daiquiri Framework.

Daiquiri can be downloaded from [https://github.com/aipescience/daiquiri](https://github.com/aipescience/daiquiri).

Daiquiri Admin provides a set of functions which can be used to use some functions of a Daiquiri powered application inside a script. The nessesarry http requests are abstracted in a transparent way.

A script for getting the emails of all users using Daiquiri Admin could look like this:

```python
#!/usr/bin/env python
import argparse

from daiquiri import Connection
from daiquiri import Auth

parser = argparse.ArgumentParser(description='Fetch the emails of all users.')
parser.add_argument('host', help='the daiquiri host')
parser.add_argument('username', help='the daiquiri username')
args = parser.parse_args()

connection = Connection(args.host, username=args.username)

for user in Auth(connection).fetch_users():
    print user['email']
```

This software is still under development and by no means complete.
