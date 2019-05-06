from distutils.core import setup

__VERSION__ = '0.0.1'
__URL__ = 'https://github.com/krayzpipes/txt-ferret'

setup(
    author='Kyle Piper',
    author_email='kylepiper29@gmail.com',
    version=__VERSION__,
    description='Scan text files for sensitive (or non-sensitive) data.',
    url=__URL__,
    name='txt-ferret',
    keywords=['txt', 'ferret', 'scan', 'data', 'sensitive'],
    packages=['txt_ferret'],
    classifiers=[
        'Intended Audience :: Security and Data Owners',
        'License :: Apache 2.0',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)