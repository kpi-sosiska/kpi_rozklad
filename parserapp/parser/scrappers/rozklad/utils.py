class RozkladRetryException(Exception):

    @classmethod
    def check_html(cls, html):
        if 'Сторінка тимчасово недоступна' in html:
            raise cls()


def remove_rozklad_prefix(url):
    return str(url).removeprefix('http://rozklad.kpi.ua').removeprefix('/Schedules/ViewSchedule.aspx')\
        .removeprefix('?v=').removeprefix('?g=')
