import settings

import gspread
from gspread import NoValidUrlKeyFound
from gspread.utils import rowcol_to_a1
from statistics import mean


class SheetsProcessor:

    _gc = gspread.service_account(settings.SERVICE_ACCOUNT_DIR)

    @classmethod
    def _open_worksheet(cls, url):
        sh = cls._gc.open_by_url(url)
        return sh.sheet1

    @classmethod
    def _get_list_of_names(cls, url):

        worksheet = cls._open_worksheet(url)

        last_name_header = worksheet.find("Фамилия")
        first_name_header = worksheet.find("Имя")

        ln_list = worksheet.col_values(last_name_header.col)
        ln_list.remove("Фамилия")

        fn_list = worksheet.col_values(first_name_header.col)
        fn_list.remove("Имя")

        list_of_names = list()
        for i in range(len(ln_list)):
            list_of_names.append(str(ln_list[i] + ' ' + fn_list[i]))

        return list_of_names

    @classmethod
    def get_num_of_participants(cls, url):

        worksheet = cls._open_worksheet(url)

        last_name_header = worksheet.find("Фамилия")
        num_of_participants = len(worksheet.col_values(last_name_header.col)) - 1

        return num_of_participants

    @classmethod
    def check_edit_access(cls, url):

        try:
            sh = cls._gc.open_by_url(url)
        except NoValidUrlKeyFound:
            return 'invalid-link'

        permissions = sh.list_permissions()
        role = None

        for dictionary in permissions:
            if dictionary['id'] == 'anyoneWithLink':
                role = dictionary['role']

        return role

    @classmethod
    def find_or_add_header(cls, url, header_name):

        worksheet = cls._open_worksheet(url)
        header_cell = worksheet.find(header_name)

        if header_cell is None:
            num_of_columns = len(worksheet.row_values(1))
            worksheet.update_cell(1, num_of_columns + 1, header_name)
            worksheet.format(rowcol_to_a1(1, num_of_columns + 1), {'textFormat': {'fontSize': 11, 'bold': True}})
            header_cell = worksheet.find(header_name)

        return header_cell.col

    @classmethod
    def find_row(cls, url, person):

        worksheet = cls._open_worksheet(url)

        try:
            last_name, first_name, *other = person.split()
        except ValueError:
            return 'value-error'

        ln_entries = worksheet.findall(last_name)
        fn_entries = worksheet.findall(first_name)

        ln_rows = [entry.row for entry in ln_entries]
        fn_rows = [entry.row for entry in fn_entries]

        intersection = set(ln_rows).intersection(fn_rows)

        try:
            row, *other = intersection
        except ValueError:
            return None

        return row

    @classmethod
    def find_row_by_discord(cls, url, discord_name):

        worksheet = cls._open_worksheet(url)
        cell = worksheet.find(discord_name)

        if cell is None:
            return None

        return cell.row

    @classmethod
    def find_result(cls, url, row):

        worksheet = cls._open_worksheet(url)

        if row is None:
            return None

        return worksheet.row_values(row)

    @classmethod
    def find_empty_cells(cls, url, col):

        worksheet = cls._open_worksheet(url)

        num_of_rows = len(worksheet.col_values(1))
        values_list = worksheet.col_values(col)
        gaps_list = [''] * num_of_rows

        for value in values_list:
            gaps_list[values_list.index(value)] = value
        gaps_list.pop(0)

        list_of_names = cls._get_list_of_names(url)
        empty_cells = dict()
        current_index = 0

        for value in gaps_list:
            if value == '':
                empty_cells[list_of_names[current_index]] = [current_index + 2, col]

            current_index += 1

        return empty_cells

    @classmethod
    def add_value(cls, url, row, col, value):

        worksheet = cls._open_worksheet(url)
        worksheet.update_cell(row, col, value)

    @classmethod
    def get_summary(cls, url):

        worksheet = cls._open_worksheet(url)

        s_header = worksheet.find("S" or "s")
        e_header = worksheet.find("E" or "e")

        s_values = worksheet.col_values(s_header.col)
        s_values.pop(0)

        e_values = worksheet.col_values(e_header.col)
        e_values.pop(0)

        s_summary = round(mean(float(value) for value in s_values), 2)
        e_summary = round(mean(float(value) for value in e_values), 2)

        return [s_summary, e_summary]


def main():
    pass


if __name__ == '__main__':
    main()
