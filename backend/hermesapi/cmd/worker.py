from .. import worker


def main():
    server = worker.create_server()
    server.run()
