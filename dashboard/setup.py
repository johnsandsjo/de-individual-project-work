from setuptools import setup, find_packages

setup(
    name= "HR-dashboard",
    version= "0.0.2",
    description="""Used for creating dashboard in streamlit for HR-dashboard""",
    author= "John",
    install_requires = ["pandas", "streamlit", "bigquery", "openpyxl"],
    packages= find_packages(exclude=("exploration*", "pipeline*", "logs*")),
    python_requires =">=3.7"
)