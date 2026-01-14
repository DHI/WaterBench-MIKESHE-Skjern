
import zipfile
import glob

zip_fn = ".publish/WaterBench-MIKESHE-Skjern-output.zip"


def zip_output():
    with zipfile.ZipFile(zip_fn, "w") as z:
        for fn in glob.glob("**/*", recursive=True):
            if (
                 "output_sample" in fn
            ):
                z.write(fn)
            else:
                print(f"Excluded: {fn}")

    print(f"Zip file created: {zip_fn}")


if __name__ == "__main__":
    zip_output()