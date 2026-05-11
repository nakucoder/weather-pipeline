import zipfile, os

os.chdir("/home/juana/weather-pipeline")

with zipfile.ZipFile("lambda.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk("package"):
        for file in files:
            filepath = os.path.join(root, file)
            arcname = os.path.relpath(filepath, "package")
            zf.write(filepath, arcname)
    zf.write("lambda_function.py", "lambda_function.py")

size = os.path.getsize("lambda.zip")
print(f"lambda.zip created: {size/1024/1024:.1f} MB")
