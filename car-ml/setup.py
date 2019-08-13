from setuptools import setup, find_packages

setup(
    name="xebikart",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'numpy==1.14.5',
        'requests==2.22.0',
        'tensorflow>=1.14.0',
        'donkeycar'
    ],
    extras_require={
        "gym": [
            'gym==0.12.1',
            'pillow==6.0.0'
        ],
        'rl': [
            'stable-baselines>=2.4.0'
        ]
    }
)
