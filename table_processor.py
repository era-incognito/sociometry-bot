from tabulate import tabulate


class TableProcessor:

    @classmethod
    def create_table(cls, dictionary, headers):

        data = [[key, *dictionary[key]] for key in dictionary]
        table = tabulate(data, headers=headers, tablefmt="fancy_grid")

        return table


def main():
    pass


if __name__ == '__main__':
    main()
