try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='sftpmgr',
    version='0.1',
    description='SFTP Stack Manager CLI Tool',
    author='Ethan McCreadie',
    author_email='ethanmcc@gmail.com',
    url='https://github.com/ethanmcc/sftpmgr',
    py_modules=['sftpmgr'],
    install_requires=[
        'boto>=2.38.0',
    ],
    entry_points={
        'console_scripts': [
            'sftpmgr = sftpmgr:execute',
        ],
    },
)
