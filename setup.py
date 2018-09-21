from setuptools import setup

setup(
    name='tinycal',
    version='0.1.6',
    description='A Python implementation of cal utility',
    author='Chang-Yen Chih',
    author_email='michael66230@gmail.com',
    scripts=['scripts/tcal'],
    packages=['tinycal'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
)
