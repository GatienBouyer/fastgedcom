from setuptools import find_packages, setup

with open("Readme.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.readlines()

setup(
    name="fastgedcom",
    version="0.0.10",
    description="A gedcom tool to parse, browse and modify gedcom files",
    packages=find_packages(exclude=['fastgedcom.test']),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GatienBouyer/fastgedcom",
    author="Gatien Bouyer",
    author_email="gatien.bouyer.dev@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Topic :: Sociology :: Genealogy",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
    ],
    keywords='fastgedcom gedcom parser genealogy',
    install_requires=requirements,
    python_requires=">=3.11",
	project_urls={
        'Bug Reports': 'https://github.com/GatienBouyer/fastgedcom/issues',
        'Source': 'https://github.com/GatienBouyer/fastgedcom',
    },
)
