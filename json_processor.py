from table_processor import TableProcessor as tProc
import json


class JSONProcessor:

    _public_headers = ["Название", "Дата", "Статус"]

    @classmethod
    def _check_key(cls, key, data: dict):
        return bool(data.get(key))

    @classmethod
    def _update_data(cls, data, path):
        with open(path, "w") as file:
            json.dump(data, file)

    @classmethod
    def _get_data(cls, path):
        try:
            with open(path, "r") as file:
                data = json.load(file)
                return data

        except FileNotFoundError:
            cls._update_data({}, path)
            return cls._get_data(path)

    @classmethod
    def initiate_survey(cls, name, url, date, path):

        data = cls._get_data(path)
        response = "Опрос добавлен в список"

        if cls._check_key(name, data):
            response = "Опрос с таким именем уже существует, придумай что-то новенькое"

        else:
            data.update({name: [url, date, "Доступен"]})
            cls._update_data(data, path)

        return response

    @classmethod
    def archive_survey(cls, name, path):

        data = cls._get_data(path)
        response = "Опрос архивирован"

        if cls._check_key(name, data):

            if data[name][2] == "Архив":
                response = "Опрос уже находится в архиве"
            else:
                data[name][2] = "Архив"

            cls._update_data(data, path)

        else:
            response = "Опроса с таким именем не существует"

        return response

    @classmethod
    def enable_survey(cls, name, path):

        data = cls._get_data(path)
        response = "Опрос доступен всем"

        if cls._check_key(name, data):

            if data[name][2] == "Доступен":
                response = "Опрос не находится в архиве и доступен"
            else:
                data[name][2] = "Доступен"

            cls._update_data(data, path)

        else:
            response = "Опроса с таким именем не существует"

        return response

    @classmethod
    def delete_survey(cls, name, path):

        data = cls._get_data(path)
        response = "Опрос удален"

        if cls._check_key(name, data):
            del data[name]
            cls._update_data(data, path)

        else:
            response = "Опроса с таким именем не существует"

        return response

    @classmethod
    def get_list(cls, path):

        data = cls._get_data(path)
        available_surveys = {}
        response = "Список доступных опросов:\n\n"

        for survey in data:
            if data[survey][2] == "Доступен":
                available_surveys.update({survey: data[survey]})
                available_surveys[survey].pop(0)

        if len(available_surveys) != 0:
            table = tProc.create_table(available_surveys, cls._public_headers)
            response += f"{table}\n\nЧтобы узнать свой результат, воспользуйся командой /myresult"

        else:
            response = "Нет доступных опросов"

        return response

    @classmethod
    def get_full_list(cls, path):

        data = cls._get_data(path)
        available_surveys = {}
        response = "Список доступных опросов:\n\n"

        for survey in data:
            available_surveys.update({survey: data[survey]})
            available_surveys[survey].pop(0)

        if len(available_surveys) != 0:
            table = tProc.create_table(available_surveys, cls._public_headers)
            response += f"{table}\n\nЧтобы узнать результат, воспользуйся командой /myresult или /result"

        else:
            response = "Нет доступных опросов"

        return response

    @classmethod
    def get_value(cls, value, name, path):

        data = cls._get_data(path)

        if cls._check_key(name, data):
            return data[name][value]

        else:
            return None


def main():
    pass


if __name__ == '__main__':
    main()
