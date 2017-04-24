#!/usr/bin/env python
import argparse

import server
import resources.user
import resources.message


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help='listening port number', type=int, default=3000)
    parser.add_argument('-db', '--database', help='url of database', default='sqlite:///www/db.sqlite')
    args = parser.parse_args()

    app = server.Server(__name__)

    app.use_db(args.database)

    app.use_resource(resources.user)
    app.use_resource(resources.message)

    app.run(args.port)
