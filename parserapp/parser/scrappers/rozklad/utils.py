class RozkladRetryException(Exception):

    @classmethod
    def check_html(cls, html):
        if 'Сторінка тимчасово недоступна' in html:
            raise cls()


def get_rozklad_uuid(url):
    url = str(url)
    assert url[-37] == "="
    return url[-36:]
