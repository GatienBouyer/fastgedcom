from setuptools import setup #type: ignore[import]

with open("Readme.md", "r") as f:
	long_description = f.read()

with open("requirements.txt", "r") as f:
	requirements = f.readlines()

with open("requirements-dev.txt", "r") as f:
	requirements_dev = f.readlines()

setup(
	name="fastgedcom",
	version="0.0.5",
	description="A lightweight tool to parse, browse and edit gedcom files.",
	packages=["fastgedcom"],
	package_data={"fastgedcom": ["py.typed"]},
	long_description=long_description,
	long_description_content_type="text/markdown",
	zip_safe=False,
	install_requires=requirements,
	extras_require={
		"dev": requirements_dev,
	},
	python_requires=">=3.10", # typing.TypeGuard, addded in 3.10, is need
	url="https://github.com/GatienBouyer/fastgedcom",
	author="Gatien Bouyer",
	author_email="gatien.bouyer.dev@gmail.com",
	license="MIT",
	classifiers=[
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python :: 3.10",
		"Programming Language :: Python :: 3.11",
		"Topic :: Sociology :: Genealogy",
		"Intended Audience :: Developers",
		"Operating System :: OS Independent",
		"Development Status :: 3 - Alpha",
	],
	keywords='fastgedcom gedcom parser genealogy',
	project_urls={
		'Bug Reports': 'https://github.com/GatienBouyer/fastgedcom/issues',
		'Source': 'https://github.com/GatienBouyer/fastgedcom',
	},
)
