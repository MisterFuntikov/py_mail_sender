#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program in the COPYING files.
# If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2025 https://github.com/MisterFuntikov
#

import re
from .helpers import preException


__all__ = [
    'checkParams',
    'mailCheck'
]


class checkException(preException):
    def __init__(self, *args):
        super().__init__('Ошибка при проверке почты', *args)


class checkParams:
    def __init__(self,
                 empty_ignore: bool = False,
                 russian_letter_ignore: bool = False,
                 detailed_description: bool = False,
                 compress_spaces: bool = False,
                 remove_spaces: bool = False,
                 multiple: bool = False,
                 split_symbols: str = ';|; |,|, '
                 ):
        """Параметры для mailCheck

        Args:
            empty_ignore (bool, optional): игнорировать пустые почтовые адреса.
            russian_letter_ignore (bool, optional): игнорировать русские буквы.
            detailed_description (bool, optional): детальное описание ошибки.
            compress_spaces (bool, optional): ижимать пробельные символы.
            remove_spaces (bool, optional): удалять все пробельные символы.
            multiple (bool, optional): несколько почтовых адресов.
            split_symbols (str, optional): разделитель почтовых адресов.        
        """
        self.empty_ignore = empty_ignore
        self.russian_letter_ignore = russian_letter_ignore
        self.detailed_description = detailed_description
        self.compress_spaces = compress_spaces
        self.remove_spaces = remove_spaces
        self.multiple = multiple
        self.split_symbols = split_symbols
        pass


def mailCheck(mail: str,
              params: checkParams,
              return_mail_seq: bool = False
              ):
    """_summary_

    Args:
        mail (str): почтовый адрес / почтовые адреса.
        params (type[checkParams]): параметры проверки
        return_mail_seq (bool, optional): при успешной проверке возвращает message с массивом почтовых адресов.

    Raises:
        checkException: Выбран параметр multiple но не указаны split_symbols.

    Returns:
    """

    if type(mail) == type(list()):
        c_mail = ','.join(mail)
    else:
        c_mail = str(mail)

    if params.remove_spaces:
        c_mail = re.sub(r'\s+', '', c_mail)
    elif params.compress_spaces:
        c_mail = re.sub(r'\s{2,}', ' ', c_mail)

    if params.multiple:
        if not params.split_symbols:
            raise Exception('Выбран параметр multiple но не указаны split_symbols')
        mas_mail = re.split(params.split_symbols, c_mail)
    else:
        mas_mail = [c_mail]

    mas_mail = [x for x in mas_mail if x]

    if len(mas_mail) == 0:
        if params.empty_ignore:
            return ['']
        raise checkException('Отсутствует почта')

    if params.russian_letter_ignore:
        pattern = r'^[\w\-\+\.]+\@[\w\-\+]+(\.[\w\-\+]+)+$'
    else:
        pattern = r'^[0-9A-Za-z\_\-\+]+[0-9A-Za-z\_\-\+\.]*\@[0-9A-Za-z\_\-\+]+(\.[0-9A-Za-z\_\-\+]+)+$'

    col_err = 0
    mas_err = ''

    for i in range(len(mas_mail)):

        if params.compress_spaces:
            mas_mail[i] = re.sub(r'\s+', '', mas_mail[i])

        if re.fullmatch(pattern, mas_mail[i]):
            continue

        if col_err > 0:
            mas_err += '\t'

        col_err += 1
        mas_err += 'неверный почтовый адрес "' + mas_mail[i] + '"'

        if not params.detailed_description:
            continue
        if re.search(r'\s', mas_mail[i]):
            mas_err += ' - содержит пробельный символ'
        if not params.russian_letter_ignore and re.search(r'[а-яА-Я]', mas_mail[i]):
            mas_err += ' - содержит кириллицу'
        if not re.search(r'\@', mas_mail[i]):
            mas_err += ' -  Отсутствует почтовый домен'
        elif re.search(r'^[\w\-\+\.]+\@', mas_mail[i]) and not re.search(r'\@\s*[\s\w\-\+]+(\.[\s\w\-\+]+)+$', mas_mail[i]):
            mas_err += ' - неправильный почтовый домен'

    if col_err != 0:
        raise checkException(mas_err)
    if return_mail_seq:
        return mas_mail
    return
