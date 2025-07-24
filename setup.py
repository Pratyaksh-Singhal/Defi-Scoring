from setuptools import find_packages,setup
from typing import List


def get_requirements()->List[str]:
    requirement_list:List[str] = []
    try:
        with open('requirements.txt','r') as file:
            lines = file.readlines()

            for line in lines:
                requirement = line.strip()

                if requirement and requirement != '-e .':
                    requirement_list.append(requirement)

    except FileExistsError:
        print("requirements.txt not found")

    return requirement_list

setup(
    name = "Defi Scoring",
    version="0.0.1",
    author="Pratyaksh Singhal",
    author_email="pratyakshsinghal635@gmail.com",
    packages=find_packages(),
    install_requires = get_requirements()
)