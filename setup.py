import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="testbotlib",
    version="0.0.1",
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
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)