from django.http import HttpResponse


class CsvHttpResponse(HttpResponse):
    def __init__(self, file_name: str, content: str, *args, **kwargs):
        headers = {'Content-Disposition': f'attachment; filename="{file_name}"'}
        super().__init__(content_type='text/csv', content=content, headers=headers, *args, **kwargs)
