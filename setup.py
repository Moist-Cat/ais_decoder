import setuptools
from pathlib import Path

with open("README.md", "r") as file:
    long_description = file.read()

with open("requirements/pro.txt") as file:
    REQUIREMENTS = file.read().split("\n")

setuptools.setup(
     name="ais_decoder",  
     version="0.1.0",
     author="Moist-Cat",
     author_email="moistanonpy@gmail.com",
     description="AIS message processing tool",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/Moist-Cat/",
     install_requires=REQUIREMENTS,
     include_package_data=True,
     package_dir={"":"src"},
     packages=setuptools.find_packages(where="src"),
     python_requires=">=3.8",
     classifiers=[
         "Programming Language :: Python :: 3",
#         "License :: OSI Approved :: MIT License",
         "Operating System :: POSIX :: Linux",
     ],
 )
