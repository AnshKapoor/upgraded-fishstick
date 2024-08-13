from ServerSocket import Server


class Core:
    def __init__(self):
        self.server = Server().start()


def main():
    c = Core()


if __name__ == "__main__":
    main()
