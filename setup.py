from setuptools import setup

setup(
    name='garage_sale',
    packages=['garage_sale'],
    include_package_data=True,
    install_requires=[
        'flask',
        'wtforms',
        'cryptography',
        'flask-reuploaded',
        'passlib',
        'werkzeug'
    ],
)
