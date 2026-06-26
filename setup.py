from setuptools import setup, find_packages

setup(
    name="skyjames",
    version="2.0.0",
    author="tbenjames",
    description="Production Computer Vision Pipeline",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.8.0",
        "torch>=2.0.0",
        "streamlit>=1.28.0",
        "ultralytics>=8.0.0",
        "flask>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "skyjames=skyjames:main",
        ],
    },
)
