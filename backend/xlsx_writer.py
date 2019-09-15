import xlwt
import tempfile


class Writer(object):
    def __init__(self, title=None):
        self.wb = xlwt.Workbook()
        self.ws = self.wb.add_sheet('sheet1')
        self.current_row = 0
        self._title = title
        self._headers = []
        self._data = []

    def new_sheet(self, name, title=None):
        if not title:
            title = name

        self.ws = self.wb.add_sheet(name)
        self.current_row = 0
        self._title = title
        return self

    def set_header(self, headers):
        self._headers = headers

        if self._title is not None:
            style = xlwt.easyxf('font: name SimHei, height 300, bold on; align: horizontal center')
            self.ws.write_merge(self.current_row, 0, self.current_row, len(headers) - 1, self._title, style)
            self.current_row += 1

        style = xlwt.easyxf('font: name SimHei, height 280, bold on; align: horizontal left')
        for index, header in enumerate(headers):
            self.ws.write(self.current_row, index, header, style)
        self.current_row += 1

        return self

    def write(self, data):
        style = xlwt.easyxf('font: height 280')
        self._data = data
        self._determine_width()

        for row_data in data:
            for col, value in enumerate(row_data):
                self.ws.write(self.current_row, col, value, style)
            self.current_row += 1

        return self

    def save(self, filename):
        self.wb.save(filename)
        return self

    def save_tmp(self):
        with tempfile.NamedTemporaryFile(prefix='xlsx-', suffix='.xlsx', delete=False) as fp:
            self.save(fp.name)

        return fp.name

    def _determine_width(self):
        data_length = len(self._headers)
        widths = [0] * data_length

        for row_data in self._data[:100]:
            for index, value in enumerate(row_data):
                if len(str(value)) > widths[index]:
                    widths[index] = len(str(value))

        for index, w in enumerate(widths):
            self.ws.col(index).width = w * 600 + 1500


if __name__ == '__main__':
    headers = [
        '序号', '名称', '性别', '年龄'
    ]

    data = [
        ['1', '用户一', '男', '25555'],
        ['2', '用户二三十', '女', '25'],
        ['3', '很长的名字很长的名字很长的名字', '女', '25'],
        ['4', '很长的名字很长的名字很长的名字很长的名字很长的名字', '女', '25'],
        ['5', '很长的名字很长的名字很长的名字很长的名字很长的名字很长的名字很长的名字很长的名字很长的名字', '女', '25'],
    ]

    # writer = Writer('文档标题')
    writer = Writer()
    filename = writer.set_header(headers).write(data).save_tmp()
    print(filename)
