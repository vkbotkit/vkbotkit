import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="testbotlib",
    version="1.0a3",
    author="kensoi",
    author_email="kensoi@dshdev.ru",
    description="Asynchronous library for VK Bots API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kensoi/testbot-newvk",
    project_urls={
        "Bug Tracker": "https://github.com/kensoi/testbot-newvk/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages = setuptools.find_packages(include=('testbotlib')),
    install_requires = ["aiohttp", "six"],
    python_requires = '>=3.7',
)