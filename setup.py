"""
Setup Script
"""

import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vkbotkit",
    version="1.3а4",
    author="kensoi",
    author_email="kensoidev@gmail.com",
    description=(
        'асинхронная библиотека с инструментами для разработки ботов ВКонтакте'
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://vkbotkit.github.io/vkbotkit",
    project_urls={
        "Releases": "https://github.com/vkbotkit/vkbotkit/releases",
        "Bug Tracker": "https://github.com/vkbotkit/vkbotkit/issues",
        "Template": "https://github.com/vkbotkit/template/",
        "Examples": "https://github.com/vkbotkit/examples/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages = setuptools.find_packages(),
    install_requires = ["aiohttp", "six"],
    python_requires = '>=3.7',
)