import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vkbotkit",
    version="1.0a5",
    author="kensoi",
    author_email="kensoi@dshdev.ru",
    description="Asynchronous library for VK Bots API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.dshdev.ru/vkbotkit",
    project_urls={
        "Bug Tracker": "https://github.com/kensoi/vkbotkit/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages = setuptools.find_packages(include=('bkpm', "vkbotkit")),
    install_requires = ["aiohttp", "six"],
    python_requires = '>=3.7',
)