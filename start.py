import server
import resources.user
import resources.message


if __name__ == '__main__':
    app = server.Server(__name__)

    app.use_db('sqlite:///www/db.sqlite')

    app.use_resource(resources.user)
    app.use_resource(resources.message)

    app.run(3000)
