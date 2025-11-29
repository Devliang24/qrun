from setuptools import setup, find_packages

setup(
    name='qrun',
    version='0.1.0',
    description='AI-driven Android testing framework - Quick Run',
    author='QRun Team',
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[
        'robotframework>=6.1.0',
        'robotframework-appiumlibrary>=2.0.0',
        'Appium-Python-Client>=3.1.0',
        'dashscope>=1.14.0',
        'click>=8.1.0',
        'PyYAML>=6.0',
        'Pillow>=10.0.0',
        'colorama>=0.4.6',
        'requests>=2.31.0',
        'uiautomator2>=3.0.0',
    ],
    entry_points={
        'console_scripts': [
            'qrun=src.cli:cli',
        ],
    },
)
