import server
import resources
import resources.user


if __name__ == '__main__':
    app = server.Server(__name__)
    app.use_resource(resources.user)
    app.run(3000)
