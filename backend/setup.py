import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aws_vps_manager_backend",
    version="0.0.1",
    author="Guillaume BITON",
    author_email="guillaume@gbweb.fr",
    description="Backend package for AWS VPS manager.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gbwebdev/aws-vps-manager/backend",
    project_urls={
        "Bug Tracker": "https://github.com/gbwebdev/aws-vps-manager/issues",
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    entry_points={
        'console_scripts': [
            'avmb = aws_vps_manager_backend:cli',
        ],
    },
    python_requires=">=3.10",
    install_requires= [
        "boto3",
        "click",
        "pyyaml",
        "logger"
    ]
)