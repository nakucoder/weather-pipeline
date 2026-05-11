import zipfile, os

with zipfile.ZipFile('lambda.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk('package'):
        for file in files:
            fp = os.path.join(root, file)
            arcname = os.path.relpath(fp, 'package')
            zf.write(fp, arcname)
    zf.write('lambda_function.py', 'lambda_function.py')

print('lambda.zip created, size:', os.path.getsize('lambda.zip'))
