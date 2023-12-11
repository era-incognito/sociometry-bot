import settings
from sheets_processor import SheetsProcessor as sProc
from json_processor import JSONProcessor as jProc
from format_processor import FormatProcessor as fProc
from table_processor import TableProcessor as tProc
from image_processor import ImageProcessor as iProc

import os
import discord
from discord import app_commands
from discord.ext import commands
from datetime import date


def main():

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="!!", intents=intents)
    json_path = settings.SURVEYS_DIR / f"{settings.GUILD_ID}.json"

    @bot.event
    async def on_ready():
        await bot.tree.sync()

    @bot.tree.command(description="Добавить новый опрос в общий список")
    @app_commands.describe(name="Название опроса, которое отобразится в общем списке")
    @app_commands.rename(name="название")
    @app_commands.describe(url="Ссылка на Google-таблицу с правами редактирования")
    @app_commands.rename(url="ссылка")
    @app_commands.default_permissions(manage_guild=True)
    async def initiate(interaction: discord.Interaction, name: str, url: str):

        if sProc.check_edit_access(url) != "writer":
            response = "Отсутствуют права редактора по ссылке, опрос не был добавлен"
            message = fProc.format_notification(response)
        else:
            sProc.find_or_add_header(url, "Discord")
            current_date = f"{date.today().month} {date.today().year}"
            response = jProc.initiate_survey(name, url, current_date, json_path)
            message = fProc.format_notification(response)

        await interaction.response.send_message(message, ephemeral=True)

    @bot.tree.command(description="Добавить опрос из общего списка в архив")
    @app_commands.describe(name="Название опроса, который будет архивирован")
    @app_commands.rename(name="название")
    @app_commands.default_permissions(manage_guild=True)
    async def archive(interaction: discord.Interaction, name: str):

        response = jProc.archive_survey(name, json_path)
        message = fProc.format_notification(response)
        await interaction.response.send_message(message, ephemeral=True)

    @bot.tree.command(description="Добавить опрос из архива обратно в общий список")
    @app_commands.describe(name="Название опроса, который будет убран из архива")
    @app_commands.rename(name="название")
    @app_commands.default_permissions(manage_guild=True)
    async def enable(interaction: discord.Interaction, name: str):

        response = jProc.enable_survey(name, json_path)
        message = fProc.format_notification(response)
        await interaction.response.send_message(message, ephemeral=True)

    @bot.tree.command(description="Удалить опрос")
    @app_commands.describe(name="Название опроса, который будет удален")
    @app_commands.rename(name="название")
    @app_commands.default_permissions(manage_guild=True)
    async def delete(interaction: discord.Interaction, name: str):

        response = jProc.delete_survey(name, json_path)
        message = fProc.format_notification(response)
        await interaction.response.send_message(message, ephemeral=True)

    @bot.tree.command(description="Вывести общий список опросов")
    async def survey_list(interaction: discord.Interaction):

        response = jProc.get_list(json_path)
        message = fProc.format_table(response)
        await interaction.response.send_message(message, ephemeral=True)

    @bot.tree.command(description="Вывести полный список опросов (включая архивированные)")
    @app_commands.default_permissions(manage_guild=True)
    async def survey_list_full(interaction: discord.Interaction):

        response = jProc.get_full_list(json_path)
        message = fProc.format_table(response)
        await interaction.response.send_message(message, ephemeral=True)

    @bot.tree.command(description="Проверить наличие пустых ячеек в колонке Discord")
    @app_commands.describe(name="Название опроса, Google-таблица которого будет проверена")
    @app_commands.rename(name="название")
    @app_commands.default_permissions(manage_guild=True)
    async def check_empty_cells(interaction: discord.Interaction, name: str):

        await interaction.response.defer(ephemeral=True)

        url = jProc.get_value(0, name, json_path)

        if url is None:
            response = "Опроса с таким именем не существует"
            message = fProc.format_notification(response)

        elif sProc.check_edit_access(url) == 'invalid-link':
            response = "Отсутствуют права читателя по ссылке, невозможно проверить таблицу"
            message = fProc.format_notification(response)

        else:
            col = sProc.find_or_add_header(url, "Discord")
            empty_cells = sProc.find_empty_cells(url, col)

            if len(empty_cells) == 0:
                response = "Пустые ячейки отсутствуют"
                message = fProc.format_notification(response)
            else:
                response = tProc.create_table(empty_cells, ["Фамилия Имя", "Строка", "Столбец"])
                message = fProc.format_table(response)

                if len(message) > 2000:
                    response = (f"В указанной таблице {len(empty_cells)} пустых ячеек в колонке Discord\n" +
                                "Увы, из-за такого большого количества невозможно вывести подробный результат проверки")
                    message = fProc.format_long_notification(response)

        await interaction.followup.send(message, ephemeral=True)

    @bot.tree.command(description="Заполнить или переписать ячейку в колонке Discord")
    @app_commands.describe(name="Название опроса, который будет отредактирован")
    @app_commands.rename(name="название")
    @app_commands.describe(person="Фамилия Имя человека из таблицы")
    @app_commands.rename(person="фамилия-имя")
    @app_commands.describe(user="Никнейм человека на сервере")
    @app_commands.rename(user="никнейм")
    @app_commands.default_permissions(manage_guild=True)
    async def fill(interaction: discord.Interaction, name: str, person: str, user: discord.User):

        await interaction.response.defer(ephemeral=True)

        url = jProc.get_value(0, name, json_path)

        if url is None:
            response = "Опроса с таким именем не существует"
            message = fProc.format_notification(response)

        elif sProc.check_edit_access(url) != "writer":
            response = "Отсутствуют права редактора по ссылке, невозможно проверить таблицу"
            message = fProc.format_notification(response)

        else:
            row = sProc.find_row(url, person)
            col = sProc.find_or_add_header(url, "Discord")

            if row is None:
                response = "Человек с таким именем не найден в таблице"
                message = fProc.format_notification(response)

            elif row == 'value-error':
                response = "Неправильный формат ввода, необходимо ввести два слова: фамилию и имя"
                message = fProc.format_notification(response)

            else:
                sProc.add_value(url, row, col, user.name)
                response = "Готово, изменения внесены в таблицу"
                message = fProc.format_notification(response)

        await interaction.followup.send(message, ephemeral=True)

    @bot.tree.command(description="Составить персональный отчет человека по его фамилии и имени")
    @app_commands.describe(name="Название опроса, по которому будет составлен отчет")
    @app_commands.rename(name="название")
    @app_commands.describe(person="Фамилия Имя человека из таблицы")
    @app_commands.rename(person="фамилия-имя")
    @app_commands.default_permissions(manage_guild=True)
    async def result(interaction: discord.Interaction, name: str, person: str):

        await interaction.response.defer(ephemeral=True)

        url = jProc.get_value(0, name, json_path)

        if url is None:
            response = "Опроса с таким именем не существует"
            message = fProc.format_notification(response)

        elif sProc.check_edit_access(url) == 'invalid-link':
            response = "Отсутствуют права читателя по ссылке, невозможно проверить таблицу"
            message = fProc.format_notification(response)

        else:
            row = sProc.find_row(url, person)

            if row is None:
                response = "Человек с таким именем не найден в таблице"
                message = fProc.format_notification(response)

            elif row == 'value-error':
                response = "Неправильный формат ввода, необходимо ввести два слова: фамилию и имя"
                message = fProc.format_notification(response)

            else:
                personal_result = list(map(str, sProc.find_result(url, row)))
                last_name, first_name, s_value, e_value, place, *other = personal_result
                person_name = last_name + " " + first_name

                group_summary = list(map(str, sProc.get_summary(url)))
                s_summary, e_summary = group_summary

                num_of_participants = str(sProc.get_num_of_participants(url))
                date = jProc.get_value(1, name, json_path)

                local_path = iProc.create_personal_report(date, num_of_participants, person_name,
                                                          s_value, e_value, place, s_summary, e_summary)
                report_image_file = discord.File(local_path, filename=local_path.name)

                await interaction.user.send(file=report_image_file)
                os.remove(local_path)

                response = "Готово, отчет отправлен в личные сообщения"
                message = fProc.format_notification(response)

        await interaction.followup.send(message, ephemeral=True)

    @bot.tree.command(description="Получить персональный отчет за прошедший опрос")
    @app_commands.describe(name="Название опроса, по которому будет составлен отчет")
    @app_commands.rename(name="название")
    async def myresult(interaction: discord.Interaction, name: str):

        await interaction.response.defer(ephemeral=True)

        url = jProc.get_value(0, name, json_path)
        admin_permissions = interaction.user.guild_permissions.administrator

        if url is None:
            response = "Опроса с таким именем не существует"
            message = fProc.format_notification(response)

        elif sProc.check_edit_access(url) == 'invalid-link':
            response = "Невозможно получить данные опроса: возможно, администратор закрыл к ним доступ"
            message = fProc.format_notification(response)

        elif (jProc.get_value(2, name, json_path) == "Архив") and (admin_permissions is False):
            response = "Невозможно получить данные опроса: возможно, администратор закрыл к ним доступ"
            message = fProc.format_notification(response)

        else:
            row = sProc.find_row_by_discord(url, interaction.user.name)

            if row is None:
                response = "Персональный результат не найден, невозможно составить отчет"
                message = fProc.format_notification(response)

            else:
                personal_result = list(map(str, sProc.find_result(url, row)))
                last_name, first_name, s_value, e_value, place, *other = personal_result
                person_name = last_name + " " + first_name

                group_summary = list(map(str, sProc.get_summary(url)))
                s_summary, e_summary = group_summary

                num_of_participants = str(sProc.get_num_of_participants(url))
                date = jProc.get_value(1, name, json_path)

                local_path = iProc.create_personal_report(date, num_of_participants, person_name,
                                                          s_value, e_value, place, s_summary, e_summary)
                report_image_file = discord.File(local_path, filename=local_path.name)

                await interaction.user.send(file=report_image_file)
                os.remove(local_path)

                response = "Готово, отчет отправлен в личные сообщения"
                message = fProc.format_notification(response)

        await interaction.followup.send(message, ephemeral=True)

    @bot.tree.command(description="Получить групповой отчет за прошедший опрос")
    @app_commands.describe(name="Название опроса, по которому будет составлен отчет")
    @app_commands.rename(name="название")
    async def group_result(interaction: discord.Interaction, name: str):

        await interaction.response.defer(ephemeral=True)

        url = jProc.get_value(0, name, json_path)
        admin_permissions = interaction.user.guild_permissions.administrator

        if url is None:
            response = "Опроса с таким именем не существует"
            message = fProc.format_notification(response)

        elif sProc.check_edit_access(url) == 'invalid-link':
            response = "Невозможно получить данные опроса: возможно, администратор закрыл к ним доступ"
            message = fProc.format_notification(response)

        elif (jProc.get_value(2, name, json_path) == "Архив") and (admin_permissions is False):
            response = "Невозможно получить данные опроса: возможно, администратор закрыл к ним доступ"
            message = fProc.format_notification(response)

        else:
            row = sProc.find_row_by_discord(url, interaction.user.name)

            if (row is None) and (admin_permissions is False):
                response = "Невозможно составить отчет: ваше имя не найдено в списке участников опроса"
                message = fProc.format_notification(response)

            else:
                group_summary = list(map(str, sProc.get_summary(url)))
                s_summary, e_summary = group_summary

                num_of_participants = str(sProc.get_num_of_participants(url))
                date = jProc.get_value(1, name, json_path)

                local_path = iProc.create_group_report(date, num_of_participants, s_summary, e_summary)
                report_image_file = discord.File(local_path, filename=local_path.name)

                await interaction.user.send(file=report_image_file)
                os.remove(local_path)

                response = "Готово, отчет отправлен в личные сообщения"
                message = fProc.format_notification(response)

        await interaction.followup.send(message, ephemeral=True)

    bot.run(settings.DISCORD_API_SECRET)


if __name__ == '__main__':
    main()
