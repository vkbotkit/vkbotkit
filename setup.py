import setuptools
from vkbotkit.__init__ import __version__
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vkbotkit",
    version=__version__,
    author="kensoi",
    author_email="kensoi@dshdev.ru",
    description="Simple Bot framework for VK Communities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.dshdev.ru/vkbotkit",
    project_urls={
        "Bug Tracker": "https://github.com/kensoi/vkbotkit/issues",
        "Bot Template": "https://github.com/kensoi/vkbotkit-bot-template/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages = setuptools.find_packages(include=("vkbotkit",)),
    install_requires = ["aiohttp", "six"],
    python_requires = '>=3.7',
)