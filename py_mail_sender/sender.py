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

import os
import smtplib
from datetime import datetime
from typing import Literal, Any, Union
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
# from email.header import Header
# from email.utils import formataddr

from .checker import checkParams, mailCheck
from .helpers import preException


__all__ = [
    'mailFiles',
    'mailSender'
]


class senderException(preException):
    def __init__(self, *args):
        super().__init__('Ошибка почтового сервера', *args)


class fileException(preException):
    def __init__(self, *args):
        super().__init__('Ошибка создания прикрепляемого файла', *args)


class mailFile:

    def __init__(self,
                 path: str = None,
                 name: str = None,
                 ext: str = None,
                 byte: bytes = None
                 ):
        """
        Прикрепляемый файл к письму

        Args:
            path (str, optional): путь к локальному файлу.
            name (str, optional): название файла.
            ext (str, optional): расширение файла.
            byte (bytes, optional): байт содержимое файла.

        Raises:
            Exception: 'Не указано имя файла'
        """

        if path:
            # Получение локального файла по его пути
            self.name = name if name else os.path.basename(path)
            with open(path, 'rb') as f:
                self.byte = f.read()
        else:
            # Закачка байт содержимого
            if not name:
                raise fileException('Не указано имя файла')
            self.name = name
            self.byte = byte

        subf = self.name.split('.')

        if ext:
            self.ext = ext
        else:
            self.ext = subf[-1] if len(subf) > 1 else None

        if len(subf) == 1 and self.ext:
            self.name += '.' + self.ext
        pass

    def getApplication(self):
        """
        Получение MIME содержимого

        Returns:
            class: MIMEApplication
        """
        if self.ext:
            part = MIMEApplication(_data=self.byte, Name=self.name, _subtype=self.ext)
        else:
            part = MIMEApplication(_data=self.byte, Name=self.name)
        part.add_header('Content-Disposition', 'attachment', filename=self.name)
        return part


class mailSender:

    def __init__(self,
                 host: str,
                 port: int = 25,
                 user: str = None,
                 password: str = None,
                 ssl: bool = False,
                 timeout: int = 1000):
        """
        mailSender

        Args:
            host (str): адрес почтового сервера.
            port (int, optional): порт почтового сервера. 
            user (str, optional): пользователь. 
            password (str, optional): пароль. 
            ssl (bool, optional): ssl. 
            timeout (int, optional): ожидание подключения. 
        """
        self._smtpobj = None
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._ssl = ssl
        self._timeout = timeout
        pass

    def connect(self):
        """
        Соединение с почтовым сервером
        """
        try:
            self._smtpobj = smtplib.SMTP(self._host, self._port, timeout=self._timeout)
            if self._ssl:
                self._smtpobj.starttls()
            if self._user and self._password:
                self._smtpobj.login(self._user, self._password)
        except Exception as e:
            raise senderException(f'Ошибка при подключении к серверу: {e}')
        return

    def close(self):
        """
        Закрытие соединения
        """
        try:
            self._smtpobj.close()
        except Exception as e:
            raise senderException(f'Ошибка закрытия соединения: {e}')
        return

    def send(self,
             m_from: str,
             m_to: str,
             copy: str = None,
             hidden_copy: str = None,
             msg_title: str = '',
             msg_body: str = '',
             msg_file: Union[list[mailFile], None] = None,
             check_mail: bool = False,
             check_mail_type: tuple = ('from', 'to', 'copy', 'hidden_copy'),
             check_mail_params: Union[checkParams, None] = None,
             sendlog: bool = False
             ):
        """
        Отправка сообщения

        Args:
            m_from (str): отправитель (от кого).
            m_to (str): получатель (кому).
            copy (str, optional): ящик для копии.
            hidden_copy (str, optional): ящик для скрытой копии.
            msg_title (str, optional): название сообщения.
            msg_body (str, optional): тело сообщения в формате html utf-8.
            msg_file (dict, optional): файлы для сообещения
            check_mail (bool, optional): _description_. Defaults to False.
            check_mail_type (set, optional): _description_. Defaults to ('from', 'to', 'copy', 'hidden_copy').
            check_mail_params (dict, optional): _description_. Defaults to {}.
            sendlog (bool, optional): Журнал отправки. При успешной отправке сформируется журнал со сведениями об отправке сообщения.

        Returns:
        """

        addresses = {
            'from': m_from,
            'to': m_to,
            'copy': copy,
            'hidden_copy': hidden_copy,
        }

        if check_mail:

            if check_mail_params == None:
                check_mail_params = checkParams()

            if check_mail_type == None:
                check_mail_type = set()

            for key in check_mail_type:
                addresses[key] = mailCheck(mail=addresses[key],
                                           params=check_mail_params,
                                           return_mail_seq=True)

        if type(addresses['from']) != type(list()):
            addresses['from'] = [addresses['from']]
        if type(addresses['to']) != type(list()):
            addresses['to'] = [addresses['to']]
        if addresses['copy'] and type(addresses['copy']) != type(list()):
            addresses['copy'] = [addresses['copy']]
        if addresses['hidden_copy'] and type(addresses['hidden_copy']) != type(list()):
            addresses['hidden_copy'] = [addresses['hidden_copy']]

        message = MIMEMultipart()
        message['Subject'] = str(msg_title)
        message['From'] = addresses['from'][0]
        # message['From'] = formataddr((str(Header('ИМЯ ЯЩИКА', 'utf-8')), self._params['from']))
        message['To'] = ', '.join(addresses['to'])
        if addresses['copy']:
            message['Cc'] = ', '.join(addresses['copy'])
        message.attach(MIMEText(str(msg_body), 'html', 'utf-8'))

        if msg_file:
            for mfile in msg_file:
                message.attach(mfile.getApplication())

        to_addrs = addresses['to']
        if addresses['copy']:
            to_addrs += addresses['copy']
        if addresses['hidden_copy']:
            to_addrs += addresses['hidden_copy']

        reconnect = False
        while True:
            try:
                self._smtpobj.sendmail(from_addr=addresses['from'][0],
                                       to_addrs=to_addrs,
                                       msg=message.as_bytes())
            except smtplib.SMTPServerDisconnected as e:
                if reconnect:
                    raise senderException(f'Ошибка отправки письма: {e}')
                self.connect()
                reconnect = True
                continue
            except Exception as e:
                raise senderException(f'Ошибка отправки письма: {e}')
            break

        if not sendlog:
            return

        slog = {
            'from': addresses['from'][0],
            'to': addresses['to'],
            'copy': addresses['copy'],
            'hidden_copy': addresses['hidden_copy'],
            'datetime': datetime.now().isoformat(),
            'title': msg_title,
        }
        return {k: v for k, v in slog.items() if v is not None}
