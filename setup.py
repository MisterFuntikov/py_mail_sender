from setuptools import setup, find_packages

setup(
    name='py_mail_sender',
    description='py_mail_sender',
    version='0.1.0',

    author='Funtikov Ilya',
    author_email='ilyafunyan@yandex.ru',
    url='https://t.me/mister_funtikov',

    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],

    packages=find_packages(),
    py_modules=['checker', 
                'helpers', 
                'sender'],

    python_requires=">=3.8",
    install_requires=[],        
)
