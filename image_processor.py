import settings

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


class ImageProcessor:

    _font_small = ImageFont.truetype(str(settings.GRAPHIC_RESOURCES_DIR / "arial.ttf"), 19)
    _font_medium = ImageFont.truetype(str(settings.GRAPHIC_RESOURCES_DIR / "arial.ttf"), 34)
    _font_large = ImageFont.truetype(str(settings.GRAPHIC_RESOURCES_DIR / "arial.ttf"), 82)

    _fill = '#000000'

    _pr_date_pos = (130, 171)
    _pr_participants_pos = (426, 171)
    _pr_name_pos = (59, 294)
    _pr_s_pos = (59, 1026)
    _pr_e_pos = (331, 1026)
    _pr_place_pos = (603, 1026)
    _pr_s_summary_pos = (227, 1241)
    _pr_e_summary_pos = (498, 1241)

    _gr_date_pos = (145, 165)
    _gr_participants_pos = (426, 165)
    _gr_gg_pos = (600, 493)
    _gr_ag_pos = (615, 574)

    @classmethod
    def create_personal_report(cls, date, num_of_participants, person, s_value, e_value, place, s_summary, e_summary):

        with Image.open(str(settings.GRAPHIC_RESOURCES_DIR / "personal_blank.png")) as img:
            img.load()

        draw = ImageDraw.Draw(img)
        draw.text(cls._pr_date_pos, date, font=cls._font_small, fill=cls._fill)
        draw.text(cls._pr_participants_pos, num_of_participants, font=cls._font_small, fill=cls._fill)
        draw.text(cls._pr_name_pos, person, font=cls._font_medium, fill=cls._fill)
        draw.text(cls._pr_s_pos, s_value, font=cls._font_large, fill=cls._fill)
        draw.text(cls._pr_e_pos, e_value, font=cls._font_large, fill=cls._fill)
        draw.text(cls._pr_place_pos, place, font=cls._font_large, fill=cls._fill)
        draw.text(cls._pr_s_summary_pos, s_summary, font=cls._font_small, fill=cls._fill)
        draw.text(cls._pr_e_summary_pos, e_summary, font=cls._font_small, fill=cls._fill)

        local_path = settings.JUNK_DIR / f"{settings.GUILD_ID}_personal-report_{person}.png"
        img.save(str(local_path))

        return local_path

    @classmethod
    def create_group_report(cls, date, num_of_participants, s_summary, e_summary):

        gg_value = s_summary[-2:] + '%'
        ag_value = e_summary[-2:]

        with Image.open(str(settings.GRAPHIC_RESOURCES_DIR / "group_blank.png")) as img:
            img.load()

        draw = ImageDraw.Draw(img)
        draw.text(cls._gr_date_pos, date, font=cls._font_small, fill=cls._fill)
        draw.text(cls._gr_participants_pos, num_of_participants, font=cls._font_small, fill=cls._fill)
        draw.text(cls._gr_gg_pos, gg_value, font=cls._font_medium, fill=cls._fill)
        draw.text(cls._gr_ag_pos, ag_value, font=cls._font_medium, fill=cls._fill)

        local_path = settings.JUNK_DIR / f"{settings.GUILD_ID}_group-report.png"
        img.save(str(local_path))

        return local_path


def main():
    pass


if __name__ == '__main__':
    main()
