class RozkladRetryException(Exception):

    @classmethod
    def check_html(cls, html):
        if 'Сторінка тимчасово недоступна' in html:
            raise cls()
