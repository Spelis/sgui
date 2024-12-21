if __name__ == "__main__":
    import shutil,os
    shutil.rmtree(os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../dist")),True)
    os.system("python -m build")
    os.system("python -m twine upload dist/*")
