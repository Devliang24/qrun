from setuptools import setup, find_packages

setup(
    name='ai-test',
    version='0.1.0',
    description='AI-driven Android business testing framework',
    author='AI Test Team',
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
    ],
    entry_points={
        'console_scripts': [
            'ai-test=src.cli:cli',
        ],
    },
)
