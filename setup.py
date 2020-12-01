from setuptools import setup

setup(
    name='garage_sale',
    packages=['garage_sale'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-wtf',
        'wtforms',
        'cryptography',
        'flask-reuploaded',
        'passlib',
        'werkzeug',
        'flask-bootstrap',
        'stripe'
    ],
)
