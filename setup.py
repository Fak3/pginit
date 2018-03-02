


from setuptools import setup, find_packages


setup(
    name='pginit',
    version='0.1',
    description='initialize postgres for django project',
    long_description='pginit path.to.settings',
    author='Roman Evstifeev',
    author_email='someuniquename@gmail.com',
    url='https://github.com/Fak3/pginit',
    license='MIT',
    #packages=find_packages(),
    py_modules=['postgres_init'],
    include_package_data=True,
    entry_points={
        'console_scripts': ['pginit = postgres_init:main'],
    },
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Android',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
)
