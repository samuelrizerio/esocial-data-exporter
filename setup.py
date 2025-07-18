from setuptools import setup, find_packages

setup(
    name="esocial-migration",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "lxml>=4.6.3",
        "sqlalchemy>=1.4.23",
        "pandas>=1.3.3",
        "python-dotenv>=0.19.0",
        "pydantic>=1.8.2",
        "tqdm>=4.62.2",
    ],
    python_requires=">=3.8",
    author="Samuel",
    author_email="samuel@example.com",
    description="Ferramenta de migração de dados do eSocial",
    keywords="esocial, migração, dados, csv, xml, xlsx",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
