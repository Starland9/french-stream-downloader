import os


if __name__ == "__main__":
    for file in os.listdir("src/ui"):
        if file.endswith(".ui"):
            os.system(f"pyuic6 src/ui/{file} -o src/ui/{file[:-3]}.py")
