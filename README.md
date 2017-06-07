![logo](logo.png)

# Woosh Server
Part of an open source, secured chat project for university

### Abstract

Woosh is a secured e2e chat implementation, carried using a system of server-client network. It was developed as part of my final project for my B.Sc of Computer Science in Ben Gurion University of the Negev, as a demonstration of computer and network security principals.

Woosh comes to provide a secured solution for the carrying of private conversations on the application level. It takes inspiration from "trusted provider" encryption algorithms, such as Telegram's **MTProto** or Signal's (and WhatsApp's) **Signal** protocols - where communication is not p2p, but the distribution of keys and routing of messages is being done through a trusted central server. If the "trustfulness" invariant is being kept, said server is not able to read contents from any of the messages, as they're entirely encrypted on the clients' side.

### Assumptions and constraints

By design, the server component is completely agnostic to the process of encryption, and only serves as mean to distribute data between users and route messages from one to another. Therefore, the server works under the following assumptions and constraints:

1. It cannot, under any circumstances, confirm the integrity of encrypted data. As a result, it is up to the client to be robust enough in order to handle cases where it receives malformed data.

2. It does not provide Transport-Level security. That's why it is important to run this server behind a TLS termination proxy.

3. The server is enitrely restful-like, meaning that it holds no state regarding the connection.

### How it works

This article refers to the implementation of the **server** application. For the client's, refer to the documentation in the [Woosh Client Repository](https://github.com/illBeRoy/secured-chat-client).

**Technologies**

By design, the server has a stateless restful-like architecture. It is powered by [flask](http://flask.pocoo.org) and [sqlalchemy](https://www.sqlalchemy.org).

The platform and language of choice, as a result, is [python 2.7](https://www.python.org/download/releases/2.7), where I used [pip](https://pip.readthedocs.io/en/stable) as my package manager tool.

**Framework**

When designing the server, I wanted it to be both generic enough in order to allow abstraction over network and db operations, and powerful enough to prevent redundant boilerplate code while keeping io operations to a minimum.

In order to achieve that, I've come up with a system of resources: while the actual implementation of the server and the orm is being done as part of a framework (under the `/server/` directory), it provides an extensible interface to declare logic by value returning and exception raising (which, in turn, become the respectful responses).

What's left was to provide an interface for the logic to parse incoming parameters from the user. As a method to achieve that, I've come up with a set of `RequestParser` classes, which act much like the famous [argparse](https://docs.python.org/2.7/library/argparse.html) library, and are inspired by [flask-restful](https://flask-restful.readthedocs.io/en/0.3.5/quickstart.html#argument-parsing)'s parsers.

**Resources**

Resources contain the actual logic of the application, including the models definition (stored in the respective database tables by the server framework) and the endpoints.

There are two resources:

1. Users: Contain information about the users, and actions which they can perform, such as registration, authentication, search.

2. Messages: Contain information about messages, basically who sent to whom and when. The actual contents of the messages are expected to be encrypted on the clients' end (that's why the tests don't check for cryptography). The Messages resource provides related actions, such as sending messages, polling messages, and deleting obsolete messages.

### Running and Packaging

**Running locally**

In order to run the project locally, the dependencies must first be installed using pip:

`$ pip install -r requirements.txt`

It is advisable to use [virtualenv](https://virtualenv.pypa.io/en/stable) in order to perserve project encapsulation.

Then, running the program could be easily done by running:

`$ ./start.py` or `$ python start.py`

The program receives multiple command line arguments, which could determine which port and database to use. By default, it listens on port 3000 and uses a local [sqlite](https://www.sqlite.org) database.

**Testing**

The program has a series of sanity tests, where each starts a clean instance of the server on a child process, and tests requests against it.

The suite itself is written using python's [unittest](https://docs.python.org/2/library/unittest.html) framework.

**Integration Scripts**

Under the `/scripts/` directory there's a script called `integration_start.py`. It is used by the client when running integration tests, and its sole purpose is to provide a general interface for the client's testing framework to start a fresh instance of the server, without having to be familiar with it.

**Running with docker**

Aside from running the server locally, there's an option to start it on a [docker](https://www.docker.com) container. In order to run it, you must first build an image of it:

`$ docker build -t woosh-server .`

The image installs all required dependencies, and exposes port 3000.

Afterwards, start an instance of it:

`$ docker run -p 3000:3000 woosh-server`

**Note:** The docker instance runs the server with an internal sqlite database, and provides no means of persistence, meaning that it loses all data when the container is removed.

### Attributions

The project is the work of Roy Sommer - but not solely: behind the scenes it uses many open source packages, thanks to the huge community standing behind python and pypi. From flask to sqlalchemy - I owe a huge thanks to the open source community. A full list of open source project could be found in my project's `requirements.txt`.
